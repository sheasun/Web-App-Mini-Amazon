import threading
from socket import socket

from interface import *
import web_pb2 as webBuffer
import world_amazon_pb2 as amazonBuffer
import ig_pb2 as igBuffer
from db import *

def process_packing(worldSocket: socket, upsSocket: socket, webOrder: webBuffer.WebOrder):
    '''parse an user order and send to the world
    
    message APack{
        required int32 whnum = 1;
        repeated AProduct things = 2;
        required int64 shipid = 3;
        required int64 seqnum = 4;
    }

    message AProduct{
        required int64 id = 1;
        required string description = 2;
        required int32 count = 3;
    }

    message WebOrder{
        required int64 orderID = 1;
    }

    message AReqTruck {
        required AInitWarehouse warehouse = 1;    // warehouse info
        repeated AProduct product = 2;    // products info
        required int64 packageid = 3;    // packageID
        required int64 sequenceNum = 4;
    }

    message AMsgs {
        repeated AReqTruck reqtruck = 1;
        repeated CompleteLoading completeloading = 2;
        repeated int64 acks = 3;
    }

    '''
    dbSession = create_db_session()

    orderId = webOrder.orderID
    order: Orders = dbSession.query(Orders).filter(Orders.id == orderId)[0]
    orderDetails = dbSession.query(OrderDetails).filter(OrderDetails.order_id == order.id)

    orderUser: Users = dbSession.query(Users).filter(Users.id == order.user_id)[0]
    wareHouse: Warehouses = dbSession.query(Warehouses).filter(Warehouses.id == Orders.wh_id)[0]

    # world command
    aCommands = amazonBuffer.ACommands()
    aPack = aCommands.topack.add()
    aPack.whnum = order.wh_id
    aPack.shipid = order.id
    aPack.seqnum = get_seqnum_world()

    # ups command
    aMsgs = igBuffer.AMsgs()
    aReqTruck = aMsgs.reqtruck.add()

    aReqTruck.warehouse.id = order.wh_id
    aReqTruck.warehouse.x = wareHouse.location_x
    aReqTruck.warehouse.y = wareHouse.location_y

    aReqTruck.packageid = order.id
    aReqTruck.sequenceNum = get_seqnum_ups()

    aReqTruck.buyer_x = orderUser.location_x
    aReqTruck.buyer_y = orderUser.location_y

    # aReqTruck.user_id = webOrder.userID
    if orderUser.ups_name is not None:
        aReqTruck.ups_name = orderUser.ups_name

    for orderDetail in orderDetails:
        item: Items = dbSession.query(Items).filter(Items.id == orderDetail.item_id)[0]

        aProduct = amazonBuffer.AProduct()
        aProduct.id = item.id
        aProduct.description = item.description
        aProduct.count = orderDetail.count

        aPack.things.append(aProduct)
        aReqTruck.product.append(aProduct)

    # send_proto_message(worldSocket, aCommands)
    # send_proto_message(upsSocket, aMsgs)
    try_send_proto_message(
        sendingSocket=worldSocket,
        googleBufferMessage=aCommands,
        targetSeqNum=aPack.seqnum
    )

    try_send_proto_message(
        sendingSocket=upsSocket,
        googleBufferMessage=aMsgs,
        targetSeqNum=aReqTruck.sequenceNum,
        toWorld=False
    )

    return

def process_purchaseMore(worldSocket: socket, purchase: webBuffer.WebPurchaseMore):
    ''' parse a purchase more request 

    message WebPurchaseMore{
        required int32 whnum = 1;
        repeated WebProduct things = 2;
    }

    message WebProduct{
        required int64 itemId = 1;
        required string description = 2;
        required int32 count = 3;
    }

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
    dbSession = create_db_session()

    aCommands = amazonBuffer.ACommands()
    aCommands.disconnect = False
    aPurchaseMore = aCommands.buy.add()
    aPurchaseMore.whnum = purchase.whnum
    aPurchaseMore.seqnum = get_seqnum_world()

    aProduct = amazonBuffer.AProduct()
    aProduct.id = purchase.itemId
    aProduct.description = dbSession.query(Items).filter(Items.id == purchase.itemId)[0].description
    aProduct.count = purchase.count

    aPurchaseMore.things.append(aProduct)
    
    # send_proto_message(worldSocket, aCommands)
    try_send_proto_message(
        sendingSocket=worldSocket,
        googleBufferMessage=aCommands,
        targetSeqNum= aPurchaseMore.seqnum
    )
    print(aCommands)

    return

def process_purchaseNew(worldSocket: socket, purchase: webBuffer.WebPurchaseNew):
    '''
    message WebPurchaseNew{
        required int32 whnum = 1;
        required string description = 2;
        required int32 count = 3;
    }

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

    dbSession = create_db_session()

    aCommands = amazonBuffer.ACommands()
    aCommands.disconnect = False
    aPurchaseMore = aCommands.buy.add()
    aPurchaseMore.whnum = purchase.whnum
    aPurchaseMore.seqnum = get_seqnum_world()

    item = dbSession.query(Items).filter(Items.description == purchase.description)
    itemId = -1
    if(item.count() == 0):
        newItem: Items = Items(description=purchase.description)
        dbSession.add(newItem)
        dbSession.commit()
        itemId = newItem.id
    else:
        item: Items = item[0]
        itemId = item.id

    aProduct = amazonBuffer.AProduct()
    aProduct.id = itemId
    aProduct.description = purchase.description
    aProduct.count = purchase.count

    aPurchaseMore.things.append(aProduct)
    
    try_send_proto_message(
        sendingSocket=worldSocket,
        googleBufferMessage=aCommands,
        targetSeqNum= aPurchaseMore.seqnum
    )
    print(aCommands)

    return

def handle_user_requests(worldSocket: socket, upsSocket: socket, webSocket: socket):
    '''handle requests from http server
    
    message WebCommands {
        repeated WebOrder orders = 1;
        repeated WebPurchaseMore purchaseMores = 2;
    }

    '''
    while(True):
        c, addr = webSocket.accept()
        try:
            webRequest = received_proto_message(c, webBuffer.WebCommands)
        except:
            continue
        for order in webRequest.orders:
            t = threading.Thread(target=process_packing, args=(worldSocket, upsSocket, order,))
            t.start()

        for purchase in webRequest.purchaseMores:
            t = threading.Thread(target=process_purchaseMore, args=(worldSocket, purchase,))
            t.start()

        for purchaseNew in webRequest.newProducts:
            t = threading.Thread(target=process_purchaseNew, args=(worldSocket, purchaseNew,))
            t.start()
