try:
    user_id = open('user_id', 'r').read()
except:
    user_id = input('enter user id: ')
    open('user_id', 'w').write(user_id)


BUFFER_SIZE = 1024*100
host_ip, host_port = str, int
import pip
pip.main(['install', 'pillow'])
pip.main(['install', 'ping3'])
pip.main(['install', 'pyautogui'])
pip.main(['install', 'opencv_python'])
pip.main(['install', 'psutil'])
pip.main(['install', 'requests'])
del pip


import socket
from os import system as system_caller
from platform import system
import pyautogui
from PIL import Image, ImageGrab
pyautogui.FAILSAFE = False

system_caller('cls')
os_type = system()


def force_connect_server(type_of_connection):
    global host_ip, host_port
    if type_of_connection == 'tcp':
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
        connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            connection.connect((host_ip, host_port))
            break
        except:
            from requests import get
            text = get('https://bhaskarpanja93.github.io/AllLinks.github.io/').text.split('<p>')[-1].split('</p>')[0].replace('‘', '"').replace('’', '"').replace('“', '"').replace('”', '"')
            link_dict = eval(text)
            host_ip, host_port = link_dict['adfly_user_tcp_connection'].split(':')
            host_port = int(host_port)
    return connection


def __send_to_connection(connection, data_bytes: bytes):
    data_byte_length = len(data_bytes)
    connection.send(str(data_byte_length).encode())
    if connection.recv(1) == b'-':
        connection.send(data_bytes)
    if connection.recv(1) == b'-':
        return


def __receive_from_connection(connection):
    length = int(connection.recv(BUFFER_SIZE))
    connection.send(b'-')
    data_bytes = b''
    while len(data_bytes) != length:
        data_bytes += connection.recv(BUFFER_SIZE)
    connection.send(b'-')
    return data_bytes


def __shutdown_host_machine(duration=5):
    system_caller(f'shutdown -s -f -t {duration}')


def __close_all_chrome():
    system_caller('taskkill /F /IM "chrome.exe" /T')


def __find_image_on_screen(img_name, all_findings=False, confidence=1.0, region=None):
    sock = force_connect_server('tcp')
    try:
        sock.settimeout(10)
        __send_to_connection(sock, b'6')
        __send_to_connection(sock, img_name.encode())
        size = eval(__receive_from_connection(sock))
        img_data = __receive_from_connection(sock)
        try:
            img_data = Image.frombytes(mode="RGBA", size=size, data=img_data, decoder_name='raw')
        except:
            img_data = Image.frombytes(mode="RGB", size=size, data=img_data, decoder_name='raw')
        if all_findings:
            return pyautogui.locateAllOnScreen(img_data, confidence=confidence, region=region)
        else:
            return pyautogui.locateOnScreen(img_data, confidence=confidence, region=region)
    except:
        return __find_image_on_screen(img_name, all_findings, confidence, region)


def __click(location, position='center'):
    x, y, x_thick, y_thick = location
    if position == 'center':
        x = x + (x_thick // 2)
        y = y + (y_thick // 2)
        pyautogui.moveTo(x, y)
        pyautogui.click(x, y)
    elif position == 'top_right':
        x = x + x_thick
        pyautogui.moveTo(x, y)
        pyautogui.click(x, y)


def send_debug_data(text, additional_comment: str = ''):
    try:
        print(f'{text}-{additional_comment}'.encode())
        ss = ImageGrab.grab().tobytes()
        x, y = pyautogui.size()
        debug_connection = force_connect_server('tcp')
        __send_to_connection(debug_connection, b'3')
        __send_to_connection(debug_connection, f'{text}-{additional_comment}'.encode())
        __send_to_connection(debug_connection, str((x, y)).encode())
        __send_to_connection(debug_connection, ss)
    except:
        pass


connection = force_connect_server('tcp')
__send_to_connection(connection, b'0')
main_data = __receive_from_connection(connection)
if open('final_main.py', 'rb').read() != main_data:
    with open('final_main.py', 'wb') as main_file:
        main_file.write(main_data)
    system_caller('final_main.py')
else:
    connection = force_connect_server('tcp')
    __send_to_connection(connection, b'1')
    open('runner.py', 'wb').close()
    runner_file = open('runner.py', 'ab')
    runner_file.write(__receive_from_connection(connection))
    runner_file.close()
    connection.close()
    import runner
    runner.run(host_ip, host_port, user_id)
