import threading
from multiprocessing import Process
from config import *
from world_handler import handle_world_responses
from ups_handler import handle_ups_responses
from user_handler import handle_user_requests
from interface import *
from db import *
import world_amazon_pb2 as amazonBuffer
import world_ups_pb2 as upsBuffer
import web_pb2 as webBuffer
import ig_pb2

def init_warehouses_and_connect(worldSocket: socket, worldId: int):
    '''create 2 warehouses and connect to world
    
    '''
    dbSession = create_db_session()
    currentWareHouses: Warehouses = dbSession.query(Warehouses).order_by(Warehouses.id.asc())

    whId1, whId2 = 1, 2
    x1, y1 = 50, 40
    x2, y2 = 80, 90

    if(currentWareHouses.count() >= 2):
        whId1, whId2 = currentWareHouses[0].id, currentWareHouses[1].id
    else:
        warehouse1: Warehouses = Warehouses(x=x1, y=y1)
        warehouse2: Warehouses = Warehouses(x=x2, y=y2)

        dbSession.add(warehouse1)
        dbSession.add(warehouse2)
        dbSession.commit()
   
    aInitWarehouse1 = amazonBuffer.AInitWarehouse()
    aInitWarehouse1.id = whId1
    aInitWarehouse1.x = x1
    aInitWarehouse1.y = y1

    aInitWarehouse2 = amazonBuffer.AInitWarehouse()
    aInitWarehouse2.id = whId2
    aInitWarehouse2.x = x2
    aInitWarehouse2.y= y2

    aConnect = amazonBuffer.AConnect()
    aConnect.worldid = worldId
    aConnect.initwh.append(aInitWarehouse1)
    aConnect.initwh.append(aInitWarehouse2)
    aConnect.isAmazon = True

    send_proto_message(worldSocket, aConnect)
    print(received_proto_message(worldSocket, amazonBuffer.AConnected))

    return

def socket_server():
    init_db_for_world()

    world_socket = create_socket('WORLD')
    print("Connect to WORLD socket successfully!")

    # ups_socket = create_socket('UPS')

    upsToWorldSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    upsToWorldSocket.connect((socket.gethostbyname(WORLD_HOST), 12345))

    uConnect = upsBuffer.UConnect()
    uConnect.isAmazon = False
    
    send_proto_message(upsToWorldSocket, uConnect)
    response: upsBuffer.UConnected = received_proto_message(upsToWorldSocket, upsBuffer.UConnected)
    print(response)

    # ups_socket_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ups_socket_listener.bind((UPS_HOST, int(UPS_PORT)))
    # ups_socket_listener.listen(5)

    # ups_socket, addr = ups_socket_listener.accept()
    # response = ups_socket.recv(4096)

    web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web_socket.bind((WEB_HOST, WEB_PORT))
    web_socket.listen(5)

    # init_warehouses_and_connect(world_socket, response.worldid)
    init_warehouses_and_connect(world_socket, response.worldid)

    world_thread = threading.Thread(
        target=handle_world_responses, args=(world_socket, world_socket)
    )

    web_thread = threading.Thread(
        target=handle_user_requests, args=(world_socket, world_socket, web_socket)
    )

    # ups_thread = threading.Thread(
    #     target=handle_ups_responses, args=(ups_socket,)
    # )

    threads = [world_thread, web_thread]
    # threads = [world_thread, web_thread, ups_thread]
    for thread in threads:
        thread.start()

    while (1):
        pass

def mock_umsgs():
    message = ig_pb2.UMsgs()
    truck = message.trucks.add()
    truck.truckid = 1
    truck.seqnum = 5

if __name__ == '__main__':
    socket_server()

