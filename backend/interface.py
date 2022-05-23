from time import sleep
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint
import socket
from db import *
import socket
import config
from threading import Lock
import multiprocessing

seqNumWorld: int = 0
seqNumUps: int = 0

seqNumWorldMutex = Lock()
seqNumUpsMutex = Lock()

sendLock = Lock()
receivedLock = Lock()

unackedseqNumsWorld = set()
unackedseqNumsUps = set()


def create_socket(service: str):
    '''create a socket
    
    Parameters
    ----------
    service: str
        world, ups or web

    Returns
    -------
    socket
        a socket

    '''
    host, port = '', -1
    if service.upper() == 'WORLD':
        host, port = config.WORLD_HOST, config.WORLD_PORT
    elif service.upper() == 'UPS':
        host, port = config.UPS_HOST, config.UPS_PORT
    elif service.upper() == 'WEB':
        host, port = config.WEB_HOST, config.WEB_PORT
    else:
        raise ValueError('service must be \'amazon\' or \'ups\'')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostName = socket.gethostbyname(host)   
    s.connect((hostName, port))
    return s

def send_proto_message(worldSocket: socket, googleBufferMessage):
    '''send a message to the world

    Parameters
    ----------
    worldSocket: socket
        socket
    googleBufferMessage: google buffer message
        google buffer message to be sent
    
    '''
    print(googleBufferMessage)
    request = googleBufferMessage.SerializeToString()

    # global sendLock
    # sendLock.acquire()
    # flag = False
    # while(flag == False):
    #     try:
    _EncodeVarint(worldSocket.send, len(request), None)
    worldSocket.send(request)
    # flag = True
        # except:
        #     print('error sending message')
        #     pass
    # sendLock.release()

    return

def try_send_proto_message(sendingSocket: socket, googleBufferMessage, targetSeqNum: int, toWorld=True):
    '''try sending message until ack received
    
    '''
    global unackedseqNumsWorld, unackedseqNumsUps
    while(True):
        send_proto_message(sendingSocket, googleBufferMessage)
        sleep(5)
        if(toWorld):
            if(targetSeqNum not in unackedseqNumsWorld):
                break
        else:
            if(targetSeqNum not in unackedseqNumsUps):
                break
    return

def received_proto_message(worldSocket: socket, googleBufferMessageType):
    '''receive a message from the world

    Parameters
    ----------
    worldSocket: socket
        socket
    googleBufferMessageType: google buffer type
        google buffer message type
    
    Returns
    -------
    google buffer message
        received message

    '''
    # global receivedLock
    # receivedLock.acquire()

    sizeHolder = b''
    while True:
        sizeHolder += worldSocket.recv(1)
        try:
            size = _DecodeVarint32(sizeHolder, 0)[0]
        except IndexError:
            continue
        break
    data = worldSocket.recv(size)
    response = googleBufferMessageType()
    response.ParseFromString(data)
    print(response)
    # receivedLock.release()

    return response


def get_seqnum_world():
    seqNumWorldMutex.acquire()

    global seqNumWorld, unackedseqNumsWorld
    seqNumWorld = seqNumWorld + 1
    new_seqnum = seqNumWorld
    unackedseqNumsWorld.add(seqNumWorld)

    seqNumWorldMutex.release()
    return new_seqnum

def get_seqnum_ups():
    seqNumUpsMutex.acquire()
    global seqNumUps, unackedseqNumsUps

    seqNumUps += 1
    new_seqnum = seqNumUps
    unackedseqNumsUps.add(seqNumUps)

    seqNumUpsMutex.release()
    return new_seqnum
