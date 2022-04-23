host_ip, host_port = str, int
comment = current_ip = last_ip = ''
BUFFER_SIZE = 1024 * 100
host_cpu = host_ram = success = failure = uptime = 0
img_dict = {}
connection_enabled = True
total_instances = ['ngrok_direct']
available_instances = ['ngrok_direct']
genuine_ip = None
print('runner')
def run(host_ip, host_port, user_id):
    global genuine_ip, success, failure, comment, available_instances, img_dict, host_cpu, host_ram
    from PIL import ImageGrab
    from pyautogui import size
    from ping3 import ping
    from psutil import cpu_percent as cpu
    from psutil import virtual_memory
    from random import randrange, choice
    from time import sleep, time
    from os import popen
    from os import system as system_caller
    from threading import Thread
    import socket
    from platform import system

    from os import remove
    remove('runner.py')



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
                print(host_ip, host_port)
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


    def restart_if_connection_missing():
        counter = 1
        while True:
            if connection_enabled:
                sleep(1)
                counter = 1
            else:
                sleep(1)
                counter += 1
                if counter >= 120:
                    Thread(target=send_debug_data, args=('connection_missing_restart  counter >= 1000',)).start()
                    __restart_host_machine()
                    input()


    def send_debug_data(text, additional_comment: str = ''):
        try:
            print(f'{text}-{additional_comment}'.encode())
            ss = ImageGrab.grab().tobytes()
            x, y = size()
            debug_connection = force_connect_server('tcp')
            __send_to_connection(debug_connection, b'3')
            __send_to_connection(debug_connection, f'{text}-{additional_comment}'.encode())
            __send_to_connection(debug_connection, str((x, y)).encode())
            __send_to_connection(debug_connection, ss)
        except:
            pass


    def __restart_host_machine(duration=5):
        if os_type == 'Linux':
            system_caller('systemctl reboot -i')
        elif os_type == 'Windows':
            system_caller(f'shutdown -r -f -t {duration}')


    def __shutdown_host_machine(duration=5):
        if os_type == 'Linux':
            system_caller("shutdown now -h")
        elif os_type == 'Windows':
            system_caller(f'shutdown -s -f -t {duration}')


    def __connect_vpn():
        if os_type == 'Linux':
            locations = ['HK', 'GB', 'CH', 'RO', 'NO', 'NL', 'DE', 'FR', 'CA-W', 'CA', 'US-W', 'US', 'US-C']
            loc = choice(locations)
            system_caller(f'windscribe connect {loc}')
        elif os_type == 'Windows':
            locations = ['mountain', 'ranch', 'cub', 'snow', 'vice', 'empire', 'precedent', 'dogg', 'cobain', 'montreal', 'toronto', 'vancouver', 'paris', 'amsterdam', 'zurich', 'london']
            #locations = ['mountain', 'ranch', 'cub', 'snow', 'vice', 'empire', 'precedent', 'dogg', 'cobain']  # US only
            loc = choice(locations)
            system_caller(f'windscribe-cli connect {loc}')


    def __disconnect_all_vpn():
        if os_type == 'Linux':
            system_caller('windscribe disconnect')
        elif os_type == 'Windows':
            system_caller('windscribe-cli disconnect')


    def __get_global_ip():
        for _ in range(10):
            try:
                if type(ping('8.8.8.8')) == float:
                    break
            except:
                pass
            finally:
                sleep(1)
        else:
            return ''
        try:
            return popen("curl http://checkip.dyndns.org").read().split(': ', 1)[1].split('</body></html>', 1)[0]
        except:
            try:
                return eval(popen("curl https://jsonip.com/").read())["ip"]
            except:
                try:
                    popen('curl https://whatismyipaddress.com/').read().split("Your IP</span>: ")[-1].split("</span>")[0]
                except:
                    try:
                        tokens = {'bhaskarpanja91': '1c2b2492f5a877',
                                  'bhaskarpanja93': '1f7618d92d4e2a',
                                  'bhaskarpanja94': 'cd9ab345f3808f',
                                  'bhaskarphilippines': '0a7ccd07fc681e',
                                  'abhixitdwivedi': 'ab1ebf3eadd073',
                                  'mrbhindiyt': '9962cf0bb58406',
                                  'townthreeone': '80680bd2126db9',
                                  'townthreetwo': '320f04c218efc6',
                                  'townthreethree': 'c09284712fb9bf',
                                  'townthreefour': 'b6b15de8d6b57d',
                                  'townthreefive': 'd485675cb2fa9b',
                                  'townthreesix': 'cf1d7004288741',
                                  'townthreeseven': '226b5f51917215',
                                  'townthreeeight': '8490ecefbd6cd3',
                                  'townthreenine': '49455ef8931ebc',
                                  'townthreeten': 'b6fbe34547c0b3',
                                  'townthreeeleven': '9e39df3ddc5496',
                                  'townthreetwelve': 'c17e8bbfc9452d',
                                  'umarsumaiya1106': '965f9effaccc57',
                                  'bebqueenhere': '4848f4807a3adb',
                                  'ranajitbagti': '771e5d76de0edd',
                                  'ranajitbagti91': '3c1d90e97b0d57',
                                  'mitalipanja91': '72fad79fdbfbea',
                                  'mitalipanja93': 'f13675a0178340',
                                  'payelpanja91': '3cab6aa6ee3efd'
                                  }
                        return eval(popen(f"curl https://ipinfo.io/json?token={choice(list(tokens.values()))}").read())["ip"]
                    except:
                        return ''


    def run_instance(instance_name):
        global available_instances, success, failure, comment, img_dict
        try:
            instance_connection = force_connect_server('tcp',)
            __send_to_connection(instance_connection, b'2')
            __send_to_connection(instance_connection, instance_name.encode())
            open('instance.py', 'wb').close()
            with open('instance.py', 'ab') as instance_file:
                instance_file.write(__receive_from_connection(instance_connection))
                instance_file.close()
            instance_connection.close()
            del instance_connection
            import instance
            instance_name, s, f, comment, img_dict = instance.run(host_ip=host_ip, host_port=host_port, img_dict=img_dict)
            del instance
            success += s
            failure += f
            available_instances.append(instance_name)
        except Exception as e:
            Thread(target=send_debug_data, args=(repr(e), 'run_instance',)).start()


    def update_current_ip():
        global current_ip
        current_ip = __get_global_ip()


    def update_cpu_ram():
        global host_cpu, host_ram
        host_cpu = int(cpu(percpu=False))
        host_ram = int(virtual_memory()[2])


    def restart_vpn_recheck_ip(required=False):
        global current_ip, genuine_ip, last_ip, connection_enabled
        _ = 1
        while True:
            update_current_ip()
            if (not current_ip or current_ip == genuine_ip) and not required:
                if _ <= 6:
                    sleep(5)
                    _ += 1
                else:
                    vpn_issue_connection = force_connect_server('tcp')
                    __send_to_connection(vpn_issue_connection, b'10')
                    code = __receive_from_connection(vpn_issue_connection)
                    if code == b'rs':
                        __restart_host_machine()
                        input()
                    elif code == b'sd':
                        __shutdown_host_machine()
                        input()
            elif genuine_ip != current_ip != last_ip and not required:
                break
            else:
                last_ip = current_ip
                connection_enabled = False
                if os_type == "Windows":
                    system_caller('windscribe-cli firewall off')
                __disconnect_all_vpn()
                __connect_vpn()
                connection_enabled = True
                required = False


    def uptime_calculator():
        global uptime
        working_seconds = time() - start_time
        if working_seconds < 0:
            __restart_host_machine()
        hours = working_seconds // 3600
        minutes = (working_seconds - (hours * 3600)) // 60
        seconds = working_seconds - (hours * 3600) - (minutes * 60)
        uptime = ""
        if hours != 0:
            uptime += f"{int(hours)}h"
        uptime += f"{int(minutes)}m {int(seconds)}s"




    def send_data():
        send_data_connection = force_connect_server('tcp')
        __send_to_connection(send_data_connection, b'100')
        __send_to_connection(send_data_connection, user_id)
        send_data_connection.settimeout(60)
        while True:
            try:
                website_img_size = __receive_from_connection(send_data_connection).decode()
                if website_img_size == "":
                    pass
                else:
                    update_cpu_ram()
                    uptime_calculator()
                    current_data = {'public_ip': current_ip, 'success': success, 'failure': failure, 'cpu': host_cpu, 'ram': host_ram, 'uptime': uptime}
                    __send_to_connection(send_data_connection, str(current_data).encode())
            except:
                break
        send_data()


    genuine_ip = __get_global_ip()
    start_time = time()
    Thread(target=restart_if_connection_missing).start()
    Thread(target=send_data).start()
    next_ip_reset = 0


    while True:
        while True:
            if (success + failure >= next_ip_reset) or comment == 'change_ip':
                restart_vpn_recheck_ip(True)
                comment = ''
                next_ip_reset += randrange(1, 3)
            update_cpu_ram()
            if len(available_instances) == len(total_instances) and host_cpu <= 90 and host_ram <= 90 and type(ping('8.8.8.8')) == float:
                try:
                    instance = choice(available_instances)
                    available_instances.remove(instance)
                    system_caller('cls')
                    Thread(target=run_instance, args=(instance,)).start()
                except Exception as e:
                    Thread(target=send_debug_data, args=(repr(e), 'runner main loop',)).start()
            else:
                sleep(2)
