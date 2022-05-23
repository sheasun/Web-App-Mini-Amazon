from db import *
from operator import and_
from socket import socket
import world_amazon_pb2 as  amazonBuffer
import ig_pb2 as igBuffer
from interface import *
from sqlalchemy import and_
import threading
from multiprocessing import Process

def reply_ack(sendingSocket, googleBufferMessage):
    '''reply ack back to the sender
    
    '''
    ackMessage = amazonBuffer.ACommands()
    ackMessage.acks.append(googleBufferMessage.seqnum)
    send_proto_message(sendingSocket, ackMessage)

def process_productArrived(worldSocket: socket, productArrived: amazonBuffer.APurchaseMore):
    '''handle arrive products

    message APurchaseMore{
        required int32 whnum = 1;
        repeated AProduct things = 2;
        required int64 seqnum = 3;
    }

    message AProduct{
        required int64 id = 1;
        required string description = 2;
        required int32 count = 3;
    }
    
    '''
    reply_ack(worldSocket, productArrived)

    dbSession = create_db_session()

    wareHouseId = productArrived.whnum
    for product in productArrived.things:
        itemInDb = dbSession.query(Items).filter(Items.id == product.id)
        itemId = -1
        if(itemInDb.count() == 0):
            newItem = Items(description=product.description)
            dbSession.add(newItem)
            dbSession.flush()
            itemId = newItem.id
        else:
            itemId = itemInDb[0].id
        
        stockInDb = dbSession.query(Stocks).filter(and_(Stocks.whid == wareHouseId, Stocks.item_id == product.id))
        if(stockInDb.count() == 0):
            newStock = Stocks(whid=wareHouseId, item_id=itemId, count=product.count)
            dbSession.add(newStock)
        else:
            stockInDb[0].count += product.count

        dbSession.commit()       
    return

def process_packed(worldSocket: socket, packed: amazonBuffer.APacked):
    '''handle packed orders

    message APacked {
        required int64 shipid = 1;
        required int64 seqnum = 2;
    }

    message APutOnTruck{
        required int32 whnum = 1;
        required int32 truckid = 2;
        required int64 shipid = 3;
        required int64 seqnum = 4;
    }

    message ACommands {
        repeated APurchaseMore buy = 1;
        repeated APack topack = 2; 
        repeated APutOnTruck load = 3;
        repeated AQuery queries = 4;
        optional uint32 simspeed = 5; 
        optional bool disconnect = 6;
        repeated int64 acks =7;
    }
    
    '''
    reply_ack(worldSocket, packed)

    dbSession = create_db_session()

    orderId = packed.shipid
    order = dbSession.query(Orders).filter(Orders.id == orderId)
    if(order.count() == 0):
        return
    order: Orders = order[0]

    order.status = Status_enum.two
    dbSession.commit()

    # block until truck is ready
    while(order.truck_id == None):
        # print("waiting")
        pass  

    order.status = Status_enum.three
    dbSession.commit()

    print("truck ready and packed")

    putOnTruck = amazonBuffer.APutOnTruck()
    putOnTruck.whnum = order.wh_id
    putOnTruck.truckid = order.truck_id
    putOnTruck.shipid = orderId
    putOnTruck.seqnum = get_seqnum_world()

    print("generating aCommand")
    aCommand = amazonBuffer.ACommands()
    aCommand.load.append(putOnTruck)
    aCommand.disconnect = False

    # send_proto_message(worldSocket, aCommand)
    try_send_proto_message(worldSocket, aCommand, putOnTruck.seqnum)
    print("load message sent")
    print(aCommand)

    return

def process_packageStatus(worldSocket: socket, package: amazonBuffer.APackage):
    '''handle package status
    
    message APackage{
        required int64 packageid =1;
        required string status = 2;
        required int64 seqnum = 3;
    }

    '''
    reply_ack(worldSocket, package)

    dbSession = create_db_session()
    orderId = package.packageid
    order: Orders = dbSession.query(Orders).filter(Orders.id == orderId)[0]
    order.status = package.status
    dbSession.commit()

    return

def process_loaded(worldSocket: socket, upsSocket: socket, loaded: amazonBuffer.ALoaded):
    ''' tell ups that truck is loaded and can be delieverd 

    message ALoaded{
        required int64 shipid = 1;
        required int64 seqnum = 2;
    }

    message CompleteLoading {
        required int32 truckid = 1;
        required int64 packageid = 2;
        required int64 sequenceNum = 3;
    }

    message AMsgs {
        repeated AReqTruck reqtruck = 1;
        repeated CompleteLoading completeloading = 2;
        repeated int64 acks = 3;
    }

    '''
    reply_ack(worldSocket, loaded)
    dbSession = create_db_session()

    orderId = loaded.shipid
    order: Orders = dbSession.query(Orders).filter(Orders.id == orderId)[0]
    order.status = Status_enum.four

    completeLoading = igBuffer.ACompleteLoading()
    completeLoading.truckid = dbSession.query(Orders).filter(Orders.id == orderId)[0].truck_id
    completeLoading.packageid = orderId
    completeLoading.sequenceNum = get_seqnum_ups()
        
    aMsg = igBuffer.AMsgs()
    aMsg.completeloading.append(completeLoading)

    order.status = Status_enum.five
    dbSession.commit()

    # send_proto_message(worldSocket=upsSocket, googleBufferMessage=aMsg)
    try_send_proto_message(
        sendingSocket=upsSocket, 
        googleBufferMessage=aMsg, 
        targetSeqNum=completeLoading.sequenceNum,
        toWorld=False
    )

    return

def handle_world_responses(worldSocket: socket, upsSocket: socket):
    '''handle response from world with while loop
    
    '''
    while(True):
        try:
            response = received_proto_message(worldSocket=worldSocket, googleBufferMessageType=amazonBuffer.AResponses)
        except:
            continue
        # print(response)
        for productArrived in response.arrived:
            t = threading.Thread(target=process_productArrived, args=(worldSocket, productArrived))
            t.start()

        for packed in response.ready:
            t = threading.Thread(target=process_packed, args=(worldSocket, packed))
            t.start()

        for loaded in response.loaded:
            t = threading.Thread(target=process_loaded, args=(worldSocket, upsSocket, loaded))
            t.start()

        for error in response.error:
            pass
            # print("error:", error)

        for ack in response.acks:
            global unackedseqNumsWorld
            if(ack in unackedseqNumsWorld):
                unackedseqNumsWorld.remove(ack)

        for package in response.packagestatus:
            print('package id: ', package.packageid, 'status: ', package.status)
            t = threading.Thread(target=process_packageStatus, args=(worldSocket, package))
            t.start()

        # if finished in response.finished:
        #     print('connection close, received from world: ', finished)
        #     worldSocket.close()
        #     break
            