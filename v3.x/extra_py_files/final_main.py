host_ip, host_port = '192.168.1.2', 65499

from time import sleep
from os import system as system_caller
import socket

import pip
pip.main(['install','requests'])
pip.main(['install','pyautogui'])
pip.main(['install','opencv_python'])
pip.main(['install','psutil'])
pip.main(['install','ping3'])
pip.main(['install','pillow'])
del pip
BUFFER_SIZE = 1024*100


def force_connect_server():
    global host_ip, host_port
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.settimeout(10)
    while True:
        try:
            connection.connect((host_ip, host_port))
            break
        except:
            pass
    return connection


def __send_to_connection(connection, data_bytes: bytes):
    data_byte_length = len(data_bytes)
    connection.send(f'{data_byte_length}'.zfill(8).encode())
    connection.send(data_bytes)


def __receive_from_connection(connection):
    length = b''
    while len(length) != 8:
        length+=connection.recv(8-len(length))
    length = int(length)
    data_bytes = b''
    while len(data_bytes) != length:
        data_bytes += connection.recv(length-len(data_bytes))
    return data_bytes


def send_debug_data(text, additional_comment: str = '', trial = 0):
    trial += 1
    if trial < 3:
        try:
            print(f'{text}-{additional_comment}'.encode())
            debug_connection = force_connect_server()
            __send_to_connection(debug_connection, b'3')
            __send_to_connection(debug_connection, f'{text}-{additional_comment}'.encode())
        except:
            send_debug_data(text, additional_comment, trial)


updated = False
while True:
    try:
        connection = force_connect_server()
        __send_to_connection(connection, b'0')
        main_data = __receive_from_connection(connection)
        if open('final_main.py', 'rb').read() != main_data:
            with open('final_main.py', 'wb') as main_file:
                main_file.write(main_data)
                updated = True
        break
    except:
        pass
if updated:
    system_caller('final_main.py')
else:
    while True:
        sleep(5)
        try:
            instance_token_checked = eval(open("C:/adfly_user_data", 'rb').read())['checked']
            if instance_token_checked:
                break
        except:
            pass
    instance_token = eval(open("C:/adfly_user_data", 'rb').read())['token']
    while True:
        try:
            connection = force_connect_server()
            __send_to_connection(connection, b'1')
            runner_data = __receive_from_connection(connection)
            break
        except:
            pass
    with open('runner.py', 'wb') as runner_file:
        runner_file.write(runner_data)
    import runner
    runner.run(instance_token)