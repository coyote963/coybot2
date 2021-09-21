import socket
import struct
import sys
import datetime
import json
import time
from enum import Enum
from queue import Queue
import threading

SIZE_LIMIT = 20000
MESSAGE_COLOR = 65280

START_DELIMITER = b'\xe2\x94\x90'
END_DELIMITER = b'\xe2\x94\x94'

class rcon_event(Enum):
    rcon_ping = 41
    

class rcon_receive(Enum):
    login = 0
    ping = 1
    command = 2
    request_match = 5

start_read = b'\xe2\x94\x90' 
end_read = b'\xe2\x94\x94' 

def strip_first_last(string):
    return string[1:-1]


def refresh_connection(sock):
    buffer = b''
    while True:
        buffer += sock.recv(1024)
        while buffer.find(END_DELIMITER) != -1 and buffer.find(START_DELIMITER) != -1: 
            start_index = buffer.find(START_DELIMITER) 
            end_index = buffer.find(END_DELIMITER) + len(END_DELIMITER)
            data = buffer[start_index:end_index]
            buffer = buffer[end_index:] 
            if data != b'': 
                data_info = struct.unpack_from('<'+'3s'+'h',data,0) 
                event_data = struct.unpack_from('<'+'3s'+'h'+'h'+str(data_info[1])+'s',data,0) 
                event_id = event_data[2] 
                message_string = event_data[3].decode().strip() 
                message_string = message_string[:-1]
                js = json.loads(message_string)
                if event_id == rcon_event.rcon_ping.value:
                    send_packet(sock, "1", rcon_receive.ping.value)
            if len(buffer) > SIZE_LIMIT:
                buffer = b''


def send_packet(sock, packetData, packetEnum):
    packet_message = packetData+"\00"
    packet_size = len(bytes(packet_message, 'utf-8'))
    s = struct.Struct('h'+str(packet_size)+'s')
    packet = s.pack(packetEnum, packet_message.encode('utf-8'))
    sock.send(packet)


def send_request(sock, requestID, packetData, packetEnum):
    packet_message = '"' + requestID + '" "' + packetData + '"'
    send_packet(sock, packet_message, packetEnum)


def login(ip, port, password):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    send_packet(s, password, rcon_receive.login.value)
    return s


def initialize_sockets(game_servers):
    """
    Takes the game server list and
    returns a dictionary of sockets
    mapped to their channel id
    """
    socket_dict = {}
    for game_server in game_servers:
        socket_dict[game_server['discord_channel_id']] = login(
            game_server['game_server_ip'],
            game_server['port'],
            game_server['password']
        )
    return socket_dict


def initialize_threads(sockets):
    """
    Takes a list of sockets and creates daemon threads to keep them alive
    """
    thread_list = []
    for socket in sockets:
        thread_list.append(threading.Thread(
            target = refresh_connection,
            args = (socket, ),
            daemon = True
        ))
    return thread_list
    


def rawsay(socket, username, message):
    send_packet(socket, 
        'rawsay "[{}]: {}" "{}"'.format(username, message, MESSAGE_COLOR),
        rcon_receive.command.value
    )
