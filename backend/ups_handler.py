from concurrent.futures import thread
import ig_pb2 as igBuffer
from db import *
from config import *
from interface import *
import threading

def process_truck_arrived(upsSocket: socket, truck):
    dbsession = create_db_session()

    truckid = truck.truckid
    packageid = truck.packageid
    seqnum = truck.seqnum
    order: Orders = dbsession.query(Orders).filter(Orders.id == packageid)[0]
    order.truck_id = truckid
    dbsession.commit()
    response = igBuffer.AMsgs()
    acks = seqnum
    acks = response.acks.append(acks)
    send_proto_message(upsSocket, response)

def process_package_delivered(upsSocket: socket, delivered):
    dbsession = create_db_session()

    packageid = delivered.packageid
    seqnum = delivered.seqnum
    order: Orders = dbsession.query(Orders).filter(Orders.id == packageid)[0]
    order.status = Status_enum.six
    dbsession.commit()
    response = igBuffer.AMsgs()
    response.acks.append(seqnum)
    send_proto_message(upsSocket, response)

def handle_ups_responses(ups_socket):
    '''
    message UTruckArrived{
        required int32 truckid = 1;
        required int64 packageid = 2;
        required int64 seqnum = 3;
        }
    message UFinishDelivery{
        required int64 packageid = 1;
        required int64 seqnum = 2;
        }

    '''
    # dbsession = create_db_session()
    while (1):
        try:
            message = received_proto_message(ups_socket, igBuffer.UMsgs)
        except:
            continue
        for truck in message.trucks:
            t = threading.Thread(target=process_truck_arrived, args=(ups_socket, truck))
            t.start()

        for delivered in message.finish:
            t = threading.Thread(target=process_package_delivered, args=(ups_socket, delivered))
            t.start()

        for ack in message.acks:
            global unackedseqNumsUps
            if(ack in unackedseqNumsUps):
                unackedseqNumsUps.remove(ack)
