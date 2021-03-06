global_host_address = ()
global_host_page = ''
local_host_address = ()
LOCAL_HOST_PORT = 59998
local_network_adapters = []
adfly_user_data_location = "C://adfly_user_data"
start_time  = ''
link_viewer_token = ''
def run(img_dict):
    from os import remove
    remove('instance.py')
    global start_time, link_viewer_token
    import socket
    from time import time, sleep
    from random import choice, randrange
    from threading import Thread
    from platform import system
    from os import system as system_caller
    from PIL import Image
    import pyautogui
    from ping3 import ping
    from requests import get
    print('instance')
    sleep(5)

    def verify_global_host_address():
        global global_host_address, global_host_page
        text = get('https://bhaskarpanja93.github.io/AllLinks.github.io/').text.split('<p>')[-1].split('</p>')[0].replace('‘', '"').replace('’', '"').replace('“', '"').replace('”', '"')
        link_dict = eval(text)
        global_host_page = choice(link_dict['adfly_host_page_list'])
        host_ip, host_port = choice(link_dict['adfly_user_tcp_connection_list']).split(':')
        host_port = int(host_port)
        global_host_address = (host_ip, host_port)

    def fetch_and_update_local_host_address():
        global local_network_adapters
        instance_token = eval(open(f"{adfly_user_data_location}/adfly_user_data", 'rb').read())['token']
        u_name = eval(open(f"{adfly_user_data_location}/adfly_user_data", 'rb').read())['u_name'].strip().lower()
        connection = force_connect_global_host()
        data_to_send = {'purpose': 'fetch_network_adapters', 'u_name': str(u_name), 'token': str(instance_token)}
        __send_to_connection(connection, str(data_to_send).encode())
        response = __receive_from_connection(connection)
        if response[0] == 123 and response[-1] == 125:
            response = eval(response)
            if response['status_code'] == 0:
                local_network_adapters = response['network_adapters']
                if not local_network_adapters:
                    print("Local host not found! Please run and login to the user_host file first.")
                    sleep(10)
                    fetch_and_update_local_host_address()
                for ip in local_network_adapters:
                    Thread(target=try_pinging_local_host_connection, args=(ip,)).start()
                for _ in range(10):
                    if local_host_address:
                        break
                    else:
                        sleep(1)
                else:
                    print("Please check if local host is working and reachable.")
            else:
                print("Please restart this VM and re-login")
                __restart_host_machine()

    def try_pinging_local_host_connection(ip):
        global local_host_address
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection.connect((ip, LOCAL_HOST_PORT))
            data_to_send = {'purpose': 'ping'}
            __send_to_connection(connection, str(data_to_send).encode())
            received_data = __receive_from_connection(connection)
            if received_data[0] == 123 and received_data[-1] == 125:
                received_data = eval(received_data)
                if received_data['ping'] == 'ping':
                    local_host_address = (ip, LOCAL_HOST_PORT)
                    return True
            else:
                return False
        except:
            pass

    def force_connect_global_host():
        global global_host_address, global_host_page
        while True:
            try:
                if type(ping('8.8.8.8')) == float:
                    break
            except:
                print("Please check your internet connection")
        while True:
            try:
                connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                connection.connect(global_host_address)
                break
            except:
                verify_global_host_address()
        return connection

    def force_connect_local_host():
        global global_host_address, global_host_page
        while True:
            try:
                connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                connection.connect(local_host_address)
                break
            except:
                fetch_and_update_local_host_address()
        return connection

    def __send_to_connection(connection, data_bytes: bytes):
        connection.sendall(str(len(data_bytes)).zfill(8).encode() + data_bytes)

    def __receive_from_connection(connection):
        data_bytes = b''
        length = b''
        for _ in range(12000):
            if len(length) != 8:
                length += connection.recv(8 - len(length))
                sleep(0.01)
            else:
                break
        else:
            return b''
        if len(length) == 8:
            length = int(length)
            for _ in range(12000):
                data_bytes += connection.recv(length - len(data_bytes))
                sleep(0.01)
                if len(data_bytes) == length:
                    break
            else:
                return b''
            return data_bytes
        else:
            return b''


    def __close_chrome_forced():
        if os_type == 'Linux':
            system_caller("pkill chrome")
        elif os_type == 'Windows':
            system_caller('taskkill /F /IM "chrome.exe" /T')


    def __close_chrome_safe():
        for sign in ['chrome close region 1', 'chrome close region 2']:
            chrome_close_region = __find_image_on_screen(img_name=sign, confidence=0.8)
            if chrome_close_region:
                coordinates = __find_image_on_screen(img_name='chrome close', region=chrome_close_region, confidence=0.9)
                if coordinates:
                    __click(coordinates)
                    break


    def __find_image_on_screen(img_name, all_findings=False, confidence=1.0, region=None, img_dict=img_dict):
        if img_name in img_dict:
            version = img_dict[img_name]['version']
        else:
            version = -1
        try:
            sock = force_connect_local_host()
            data_to_send = {'purpose': 'image_request', 'image_name': img_name, 'version': version}
            __send_to_connection(sock, str(data_to_send).encode())
            response = __receive_from_connection(sock)
            if response[0] == 123 and response[-1] == 125:
                response = eval(response)
                if response['image_name'] == img_name:
                    if 'image_data' in response:
                        img_dict[img_name] = {'img_data': response['image_data'], 'version': response['version'], 'img_size': response['image_size']}
                    else:
                        pass
            try:
                img_bytes = Image.frombytes(mode="RGBA", size=img_dict[img_name]['img_size'], data=img_dict[img_name]['img_data'], decoder_name='raw')
            except:
                img_bytes = Image.frombytes(mode="RGB", size=img_dict[img_name]['img_size'], data=img_dict[img_name]['img_data'], decoder_name='raw')
            if all_findings:
                return pyautogui.locateAllOnScreen(img_bytes, confidence=confidence, region=region)
            else:
                return pyautogui.locateOnScreen(img_bytes, confidence=confidence, region=region)
        except Exception as e:
            print(repr(e))
            return __find_image_on_screen(img_name, all_findings, confidence, region, img_dict)


    def __click(location, position='center'):
        if location:
            x, y, x_thick, y_thick = location
            if position == 'center':
                x = x + x_thick // 2
                y = y + y_thick // 2
                pyautogui.moveTo(x, y, mouse_movement_speed)
                pyautogui.click(x, y)
            elif position == 'top_right':
                x = x + x_thick
                pyautogui.moveTo(x, y, mouse_movement_speed)
                pyautogui.click(x, y)
            elif position == 'bottom_right':
                x = x + x_thick
                y = y + y_thick
                pyautogui.moveTo(x, y, mouse_movement_speed)
                pyautogui.click(x, y)
            elif position == 'bottom_center':
                x = x + x_thick // 2
                y = y + y_thick
                pyautogui.moveTo(x, y, mouse_movement_speed)
                pyautogui.click(x, y)


    def __restart_host_machine(duration=5):
        if os_type == 'Linux':
            system_caller('systemctl reboot -i')
        elif os_type == 'Windows':
            system_caller(f'shutdown -r -f -t {duration}')


    def restart_if_slow_instance():
        global start_time
        start_time = time()
        while not success and not failure:
            sleep(10)
            if int(time() - start_time) >= 800:
                __restart_host_machine()
                break


    def get_link():
        def fetch_main_link():
            while get(f"{global_host_page}/ping").text != 'ping':
                verify_global_host_address()
            return global_host_page

        def fetch_side_link():
            global link_viewer_token
            instance_token = eval(open(f"{adfly_user_data_location}/adfly_user_data", 'rb').read())['token']
            sock = force_connect_global_host()
            data_to_send = {'purpose': 'link_fetch', 'token': instance_token}
            __send_to_connection(sock, str(data_to_send).encode())
            received_data = __receive_from_connection(sock)
            if received_data[0] == 123 and received_data[-1] == 125:
                received_data = eval(received_data)
                link_viewer_token = received_data['link_viewer_token']
                side_link = received_data['suffix_link']
                return side_link

        while True:
            try:
                side_link = fetch_side_link()
                if '?' in side_link:
                    break
            except:
                pass
        while True:
            try:
                main_link = fetch_main_link()
                if 'http' in main_link:
                    break
            except:
                pass
        return str(main_link + side_link)


    pyautogui.FAILSAFE = False

    os_type = system()
    start_time = time()
    link = ''
    success = False
    failure = False
    Thread(target=restart_if_slow_instance).start()
    clear_chrome = (randrange(0,50) == 1)
    current_screen_condition = last_change_condition = sign = comment = ''
    mouse_movement_speed = 0.4
    typing_speed = 0.06

    try:
        possible_screen_conditions = {
            'clear_chrome_cookies': ['reset settings'],
            'enable_extensions': ['enable extensions'],
            'enable_popups': ['sites can send popups'],
            'allow_ads':['sites can show ads'],
            'google_captcha': ['google captcha'],
            'blank_chrome': ['search box 1', 'search box 2', 'search box 3', 'search box 4'],
            'ngrok_direct_open': ['ngrok direct link initial 1', 'ngrok direct link initial 2'],
            'force_click_bottom_right': ['click ok to continue 1', 'wants to send notifications 1', 'wants to send notifications 2', 'wants to send notifications 3', 'wants to send notifications 4'],
            'force_click_bottom_center': ['click ok to continue 2'],
            'adfly_skip': ['adfly skip 1', 'adfly skip 2'],
            'click_allow_to_continue': ['click allow to continue'],
            'force_close_chrome_success': ['yt logo 1', 'yt logo 2'],
            'youtube_proxy_detected': ['before you continue to youtube en'],
            'click_here_to_continue': ['click here to continue'],
            'force_close_chrome_neutral': ['ngrok wrong link', 'ngrok service unavailable'],
            'force_close_chrome_failure': ['cookies not enabled', 'site cant be reached'],
            'force_click': ['adfly continue'],
            'chrome_restore': ['chrome restore 1'],
            'nothing_opened': ['chrome icon'],
            'chrome_push_ads': ['chrome push ads region']
        }
        nothing_opened_counter = 1
        while not success and not failure:
            sleep(5)
            coordinates = [0, 0, 0, 0]
            condition_found = False
            if 'force_close_chrome' not in current_screen_condition:
                for condition in possible_screen_conditions:
                    if not condition_found:
                        for sign in possible_screen_conditions[condition]:
                            coordinates = __find_image_on_screen(img_name=sign, confidence=0.8)
                            if coordinates:
                                current_screen_condition = condition
                                condition_found = True
                                break
            if current_screen_condition:
                if current_screen_condition != last_change_condition:
                    last_change_condition = current_screen_condition
                if current_screen_condition == 'chrome_push_ads':
                    push_ad_close = __find_image_on_screen('chrome push ads', region=coordinates, all_findings=False, confidence=0.8)
                    start_time += 1
                    if push_ad_close:
                        __click(push_ad_close)
                        pyautogui.move(30,30)
                elif current_screen_condition == 'clear_chrome_cookies':  #####
                    __click(coordinates)
                    __close_chrome_safe()
                    link = 'chrome://extensions/'
                    clear_chrome = False
                    start_time = time()
                elif current_screen_condition == 'enable_extensions':
                    finish_counter = 0
                    while True:
                        coordinates = __find_image_on_screen('enable extensions', all_findings=False, confidence=0.8)
                        if finish_counter >= 5:
                            break
                        elif coordinates:
                            finish_counter = 0
                            __click(coordinates)
                        else:
                            finish_counter += 1
                            pyautogui.scroll(-500)
                    __close_chrome_safe()
                    link = 'chrome://settings/content/popups'
                    start_time = time()
                elif current_screen_condition == 'enable_popups':
                    __click(coordinates)
                    __close_chrome_safe()
                    link = 'chrome://settings/content/ads'
                    start_time = time()
                elif current_screen_condition == 'allow_ads':
                    __click(coordinates)
                    __close_chrome_safe()
                    link = ''
                    start_time = time()
                elif current_screen_condition == 'force_click_bottom_right':
                    __click(coordinates, position='bottom_right')
                elif current_screen_condition == 'force_click_bottom_center':
                    __click(coordinates, position='bottom_center')
                elif current_screen_condition == 'force_click':
                    __click(coordinates)
                elif current_screen_condition == 'chrome_restore':
                    __click(coordinates, position='top_right')
                elif current_screen_condition == 'nothing_opened':
                    if nothing_opened_counter>=1:
                        pyautogui.press('f5')
                        sleep(1)
                        __click(coordinates)
                        nothing_opened_counter = 0
                    else:
                        nothing_opened_counter += 1
                elif current_screen_condition == 'blank_chrome':
                    __click(coordinates)
                    sleep(1)
                    if clear_chrome:
                        link = 'chrome://settings/resetProfileSettings'
                    elif not link:
                        link = get_link()
                    pyautogui.typewrite(link, typing_speed)
                    sleep(1)
                    pyautogui.press('enter')
                elif current_screen_condition == 'google_captcha':
                    failure = True
                    comment = 'change_ip'
                elif current_screen_condition == 'youtube_proxy_detected':
                    __click(coordinates)
                    success = True
                    start_time = time()
                    break
                elif current_screen_condition == 'ngrok_direct_open':
                    available_links = []
                    for sign in ['ngrok direct link initial 1', 'ngrok direct link initial 2']:
                        if __find_image_on_screen(img_name=sign, all_findings=False, confidence=0.8):
                            for link_coords in __find_image_on_screen(img_name=sign, all_findings=True, confidence=0.8):
                                available_links.append(link_coords)
                    if len(available_links) > 0:
                        __click(choice(available_links))
                elif current_screen_condition == 'adfly_skip':
                    __click(coordinates)
                    sleep(10)
                elif current_screen_condition == 'click_allow_to_continue':
                    for sign in ['popup allow 1', 'popup allow 2']:
                        coordinates = __find_image_on_screen(img_name=sign, confidence=0.8)
                        if coordinates:
                            __click(coordinates)
                elif current_screen_condition == 'click_here_to_continue':
                    __click(coordinates)
                elif current_screen_condition == 'force_close_chrome_neutral':
                    start_time = time()
                    break
                elif current_screen_condition == 'force_close_chrome_success':
                    success = True
                    start_time = time()
                    if link_viewer_token:
                        success_ack_con = force_connect_global_host()
                        data_to_send = {'purpose': 'view_accomplished', 'link_view_token':str(link_viewer_token)}
                        __send_to_connection(success_ack_con, str(data_to_send).encode())
                    start_time = time()
                    break
                elif current_screen_condition == 'force_close_chrome_failure':
                    if sign == 'site cant be reached':
                        pyautogui.hotkey('browserback')
                    failure = True
                    break
            else:
                continue
        __close_chrome_safe()
    except:
        success = False
        failure = True
        comment = ''
    return [int(success), comment, img_dict]
