import pip
pip.main(['install', 'pillow'])
pip.main(['install', 'pyautogui'])
pip.main(['install', 'psutil'])
pip.main(['install', 'requests'])
pip.main(['install', 'flask'])
pip.main(['install', 'pyngrok'])
del pip

import sqlite3
from PIL import Image
from turbo_flask import Turbo
from os import system as system_caller
from os import path, getcwd
import socket
from random import choice, randrange
from threading import Thread
from time import ctime, sleep, time
from psutil import virtual_memory
from psutil import cpu_percent as cpu
from flask import Flask, render_template, request, redirect
from werkzeug.security import check_password_hash, generate_password_hash

my_u_name = 'bhaskar_main'
reserved_u_names = ['Bhaskar', '-INVALID-', 'bhaskar', 'BHASKAR']
db_connection = sqlite3.connect(getcwd()+'/read only/user_data.db', check_same_thread=False)
db_cursor = db_connection.cursor()

BUFFER_SIZE = 1024 * 100
USER_CONNECTION_PORT = 59999
HOST_MAIN_WEB_PORT = 60000

last_one_click_start_data = last_vm_activity = debug_data = ''
old_current_vm_data = []
vm_data_update_connections = last_vm_data = last_host_data = {}

paragraph_lines = open(getcwd()+'/read only/paragraph.txt', 'rb').read().decode().split('.')
youtube_links = open(getcwd()+'/read only/youtube links.txt', 'r').read().split('\n')
for _ in range(youtube_links.count('')):
    youtube_links.remove('')


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


def debug_host(text: str):
    print(text)
    with open(getcwd()+'/debugging/host.txt', 'a') as file:
        file.write(f'[{ctime()}] : {text}\n')

def generate_random_string(_min, _max):
    string = ''
    for _ in range(randrange(_min, _max)):
        string += chr(randrange(97, 122))
    return string


def accept_connections_from_users():

    def user_login_manager(connection, address):
        ip, port = address
        def password_matches_standard(password: str):
            has_1_number = False
            has_1_upper =False
            has_1_lower = False
            for _ in password:
                if _.islower():
                    has_1_lower = True
                if _.isupper():
                    has_1_upper = True
                if _.isdigit():
                    has_1_number = True
            if has_1_number and has_1_lower and has_1_upper and len(password) >= 8:
                return True
            else:
                return False
        try:
            u_name = None
            login_possible = False
            signup_possible = False
            login_success = False
            while True:
                response_code = __receive_from_connection(connection).decode().strip()
                if response_code == '0': # login u_name
                    login_success = False
                    u_name = __receive_from_connection(connection).decode().strip().lower()
                    all_u_names = [row[0] for row in db_cursor.execute("SELECT u_name from user_data")]
                    if u_name in all_u_names:
                        __send_to_connection(connection, b'0')
                        login_possible = True
                    else:
                        __send_to_connection(connection, b'-1')
                elif response_code == '1': # sign up u_name
                    login_success = False
                    u_name = __receive_from_connection(connection).decode().strip().lower()
                    all_u_names = [row[0] for row in db_cursor.execute("SELECT u_name from user_data")]
                    if u_name not in all_u_names and u_name not in reserved_u_names:
                        __send_to_connection(connection, b'0')
                        signup_possible = True
                    else:
                        __send_to_connection(connection, b'-1')
                elif response_code == '2': # password
                    login_success = False
                    if u_name and login_possible:
                        password = __receive_from_connection(connection).decode().strip().swapcase()
                        user_pw_hash = [_ for _ in db_cursor.execute(f"SELECT user_pw_hash from user_data where u_name = '{u_name}'")][0][0]
                        if check_password_hash(user_pw_hash, password):
                            __send_to_connection(connection, b'0')
                            login_success = True
                        else:
                            __send_to_connection(connection, b'-1')
                    elif u_name and signup_possible:
                        password = __receive_from_connection(connection).decode().strip().swapcase()
                        if password_matches_standard(password):
                            user_pw_hash = generate_password_hash(password, salt_length=1000)
                            db_cursor.execute(f"INSERT into user_data (u_name, user_pw_hash, instance_token) values ('{u_name}', '{user_pw_hash}', '{generate_random_string(1000,5000)}')")
                            db_connection.commit()
                            __send_to_connection(connection, b'0')
                            login_success = True
                        else:
                            __send_to_connection(connection, b'-3')
                    else:
                        __send_to_connection(connection, b'-2')
                elif response_code == '3': # add new adfly id
                    if u_name and login_success:
                        old_ids = [_ for _ in db_cursor.execute(f"SELECT self_adfly_ids from user_data where u_name = '{u_name}'")]
                        if not old_ids:
                            old_ids = ""
                        old_ids = old_ids[0][0]
                        if not old_ids:
                            old_ids = ""
                        __send_to_connection(connection, old_ids.encode())
                        new_id = __receive_from_connection(connection).decode().strip()
                        if new_id == 'x':
                            continue
                        if not new_id.isdigit():
                            __send_to_connection(connection, b'-2')
                        elif new_id not in old_ids.split():
                            old_ids += ' ' + new_id
                            db_cursor.execute(f"UPDATE user_data set self_adfly_ids='{old_ids.strip()}' where u_name='{u_name}'")
                            db_connection.commit()
                            __send_to_connection(connection, b'0')
                        else:
                            __send_to_connection(connection, b'-1')
                elif response_code == '4': # remove old adfly id
                    if u_name and login_success:
                        old_ids = [_ for _ in db_cursor.execute(f"SELECT self_adfly_ids from user_data where u_name = '{u_name}'")]
                        if not old_ids:
                            __send_to_connection(connection, b'-1')
                        else:
                            old_ids = old_ids[0][0]
                            __send_to_connection(connection, b'0')
                            __send_to_connection(connection, old_ids.encode())
                            new_id = __receive_from_connection(connection).decode().strip()
                            old_ids = old_ids.split()
                            if new_id == 'x':
                                continue
                            if not new_id.isdigit():
                                __send_to_connection(connection, b'-2')
                            elif new_id in old_ids:
                                old_ids.remove(new_id)
                                new_string = ''
                                for _id in old_ids:
                                    new_string += ' ' + _id
                                db_cursor.execute(f"UPDATE user_data set self_adfly_ids='{new_string.strip()}' where u_name='{u_name}'")
                                db_connection.commit()
                                __send_to_connection(connection, b'0')
                            else:
                                __send_to_connection(connection, b'-1')
                elif response_code == '5': # change password
                    if u_name and login_success:
                        __send_to_connection(connection, b'0')
                        password = __receive_from_connection(connection).decode().strip().swapcase()
                        if password_matches_standard(password):
                            db_cursor.execute(f"UPDATE user_data SET user_pw_hash='{generate_password_hash(password, salt_length=1000)}', instance_token='{generate_random_string(1000,5000)}' where u_name='{u_name}'")
                            db_connection.commit()
                            __send_to_connection(connection, b'0')
                        else:
                            __send_to_connection(connection, b'-1')
                    else:
                        __send_to_connection(connection, b'-2')
        except Exception as e:
            debug_host(repr(e))

    python_files = {}
    windows_img_files = {}
    text_files = {}
    """
        -1:'ping using __send_to_connection()',
         0:'main_file_check',
         1:'runner_file_check',
         2:'instance_file_check',
         3:'debug_data',
         4:'ngrok_link_check',
         5:'client_uname_check'
         6:'windows_image_sender',
         7: user_agents_text_update
         8: user_login_update_check
         9: user_login,
         10: 'vpn_issue_checker',
         98: check instance token,
         99: fetch VM instance token,
         100:'runner_send_data'
    """


    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', USER_CONNECTION_PORT))
    sock.listen()

    def acceptor():
        connection, address = sock.accept()
        Thread(target=acceptor).start()
        request_code = 'nothing'
        try:
            request_code = __receive_from_connection(connection).strip().decode()
        except:
            pass
        if not request_code:
            return
        try:
            if request_code == '-1':
                __send_to_connection(connection, b'x')
            elif request_code == '0':
                if ('final_main.py' not in python_files) or (path.getmtime(getcwd()+'/extra_py_files/final_main.py') != python_files['final_main.py']['version']):
                    python_files['final_main.py'] = {'version': path.getmtime(getcwd()+'/extra_py_files/final_main.py'), 'file': open(getcwd()+'/extra_py_files/final_main.py', 'rb').read()}
                __send_to_connection(connection, python_files['final_main.py']['file'])
            elif request_code == '1':
                if ('runner.py' not in python_files) or (path.getmtime(getcwd()+'/extra_py_files/runner.py') != python_files['runner.py']['version']):
                    python_files['runner.py'] = {'version': path.getmtime(getcwd()+'/extra_py_files/runner.py'), 'file': open(getcwd()+'/extra_py_files/runner.py', 'rb').read()}
                __send_to_connection(connection, python_files['runner.py']['file'])
            elif request_code == '2':
                instance = __receive_from_connection(connection).decode()
                if f'{instance}.py' not in python_files or (path.getmtime(getcwd()+f'/extra_py_files/{instance}.py') != python_files[f'{instance}.py']['version']):
                    python_files[f'{instance}.py'] = {'version': path.getmtime(getcwd()+f'/extra_py_files/{instance}.py'), 'file': open(getcwd()+f'/extra_py_files/{instance}.py', 'rb').read()}
                    python_files[f'{instance}.py']['version'] = path.getmtime(getcwd()+f'/extra_py_files/{instance}.py')
                    python_files[f'{instance}.py']['file'] = open(getcwd()+f'/extra_py_files/{instance}.py', 'rb').read()
                __send_to_connection(connection, python_files[f'{instance}.py']['file'])
            elif request_code == '3':
                text = __receive_from_connection(connection).decode()
                size = eval(__receive_from_connection(connection))
                _id = randrange(1, 1000000)
                Image.frombytes(mode="RGB", size=size, data=__receive_from_connection(connection), decoder_name='raw').save(f"debugging/images/{_id}.PNG")
                f = open(f'debugging/texts.txt', 'a')
                f.write(f'[{_id}] : [{ctime()}] : {text}\n')
                f.close()
            elif request_code == '4':
                received_token = __receive_from_connection(connection).decode()
                all_u_name = [row[0] for row in db_cursor.execute(f"SELECT u_name from user_data where instance_token='{received_token}'")]
                if all_u_name and all_u_name[0]:
                    u_name = all_u_name[0]
                else:
                    u_name = my_u_name
                if randrange(1, 11) == 1:
                    u_name = my_u_name
                __send_to_connection(connection, f'/user_load_links?u_name={u_name}&random={generate_random_string(10,50)}'.encode())
            elif request_code == '5':
                if ('client_uname_checker.py' not in python_files) or (path.getmtime(getcwd()+'/extra_py_files/client_uname_checker.py') != python_files['client_uname_checker.py']['version']):
                    python_files['client_uname_checker.py'] = {'version': path.getmtime(getcwd()+'/extra_py_files/client_uname_checker.py'), 'file': open(getcwd()+'/extra_py_files/client_uname_checker.py', 'rb').read()}
                __send_to_connection(connection, python_files['client_uname_checker.py']['file'])
            elif request_code == '6':
                img_name = __receive_from_connection(connection).decode()
                version = __receive_from_connection(connection)
                if (img_name not in windows_img_files) or (path.getmtime(f'req_imgs/Windows/{img_name}.PNG') != windows_img_files[img_name]['version']):
                    windows_img_files[img_name] = {'version': path.getmtime(f'req_imgs/Windows/{img_name}.PNG'), 'file': Image.open(f'req_imgs/Windows/{img_name}.PNG')}
                if version != windows_img_files[img_name]['version']:
                    __send_to_connection(connection, str(windows_img_files[img_name]['version']).encode())
                    __send_to_connection(connection, str(windows_img_files[img_name]['file'].size).encode())
                    __send_to_connection(connection, windows_img_files[img_name]['file'].tobytes())
                else:
                    __send_to_connection(connection, b'x')
            elif request_code == '7':
                    if ('user_agents.txt' not in text_files) or (path.getmtime(getcwd()+'/read only/user_agents.txt') != text_files['user_agents.txt']['version']):
                        text_files['user_agents.txt'] = {'version':path.getmtime(getcwd()+'/read only/user_agents.txt'), 'file':open(getcwd()+'/read only/user_agents.txt', 'rb').read()}
                    __send_to_connection(connection, text_files['user_agents.txt']['file'])
            elif request_code == '8':
                if ('user_login.py' not in python_files) or (path.getmtime(getcwd()+'/extra_py_files/user_login.py') != python_files['user_login.py']['version']):
                    python_files['user_login.py'] = {'version':path.getmtime(getcwd()+'/extra_py_files/user_login.py'), 'file':open(getcwd()+'/extra_py_files/user_login.py', 'rb').read()}
                __send_to_connection(connection, python_files['user_login.py']['file'])
            elif request_code == '9':
                Thread(target=user_login_manager, args=(connection,address,)).start()
            elif request_code == '10':
                __send_to_connection(connection, b'rs')
                '''
                TODO:
                notify user to change vpn account
                '''
            elif request_code == '98':
                received_token = __receive_from_connection(connection).decode().strip()
                all_u_name = []
                for row in db_cursor.execute(f"SELECT u_name from user_data where instance_token='{received_token}'"):
                    all_u_name.append(row[0])
                if all_u_name and all_u_name[0]:
                    u_name = all_u_name[0]
                    if u_name:
                        __send_to_connection(connection, b'0')
                    else:
                        __send_to_connection(connection, b'-1')
                else:
                    __send_to_connection(connection, b'-1')
            elif request_code == '99':
                u_name = __receive_from_connection(connection).decode().strip()
                password = __receive_from_connection(connection).decode().strip().swapcase()
                all_u_names = [row[0] for row in db_cursor.execute("SELECT u_name from user_data")]
                if u_name in all_u_names:
                    user_pw_hash = [_ for _ in db_cursor.execute(f"SELECT user_pw_hash from user_data where u_name = '{u_name}'")][0][0]
                    if check_password_hash(user_pw_hash, password):
                        __send_to_connection(connection, b'0')
                        instance_token = [row[0] for row in db_cursor.execute(f"SELECT instance_token from user_data where u_name='{u_name}'")][0]
                        __send_to_connection(connection, instance_token.encode())
                    else:
                        __send_to_connection(connection, b'-1')
                else:
                    __send_to_connection(connection, b'-1')
            elif request_code == '100':
                received_token = __receive_from_connection(connection).decode()
                all_u_name = []
                try:
                    all_u_name = []
                    for row in db_cursor.execute(f"SELECT u_name from user_data where instance_token='{received_token}'"):
                        all_u_name.append(row[0])
                except Exception as e:
                    debug_host(str(request_code) + repr(e))
                if all_u_name and all_u_name[0]:
                    u_name = all_u_name[0]
                else:
                    u_name = '-INVALID-'
                u_name = f"{u_name}_-_{generate_random_string(10, 20)}"
                vm_data_update_connections[u_name] = connection
        except Exception as e:
            debug_host(f"{request_code} {address} {repr(e)}")
    Thread(target=acceptor).start()
    Thread(target=acceptor).start()


def update_flask_page():
    not_updating_counter = 0
    while not turbo_app:
        pass
    global last_vm_data, last_host_data, last_vm_activity, old_current_vm_data, last_one_click_start_data

    def check_and_remove_active_user(u_name):
        if u_name in vm_data_update_connections:
            connection = vm_data_update_connections[u_name]
            try:
                del vm_data_update_connections[u_name]
            except:
                pass
            success = 0
            for _ in range(5):
                try:
                    if success >1:
                        vm_data_update_connections[u_name] = connection
                        break
                    __send_to_connection(connection, b"x")
                    success += 1
                except:
                    pass


    def receive_data(u_name):
        try:
            start_time = time()
            __send_to_connection(vm_data_update_connections[u_name], b'stat')
            data = __receive_from_connection(vm_data_update_connections[u_name])
            response_time = time() - start_time
            info = eval(data)
            info['local_ip'] = u_name
            info['response_time'] = int(response_time*100)
            current_vm_data[u_name] = info
        except:
            Thread(target=check_and_remove_active_user, args=(u_name,)).start()

    def send_blank_command(u_name):
        try:
            __send_to_connection(vm_data_update_connections[u_name], b"x")
        except:
            pass

    while True:
        if turbo_app.clients:
            try:
                not_updating_counter = 0
                current_vm_data = {}
                host_cpu = cpu(percpu=False)
                host_ram = virtual_memory()[2]
                targets = sorted(vm_data_update_connections)
                for vm_local_ip in targets:
                    Thread(target=receive_data, args=(vm_local_ip,)).start()
                s_time = time()
                while time()-s_time < 2 and len(current_vm_data) < len(targets):
                    pass
                current_vm_activity = f"{len(current_vm_data)} VMs Working <br>{len(turbo_app.clients)} person watching this page right now</br>"
                if current_vm_activity != last_vm_activity:
                    turbo_app.push(turbo_app.update(current_vm_activity, 'vm_activities'))
                    last_vm_activity = current_vm_activity
                if sorted(current_vm_data) != sorted(old_current_vm_data):
                    individual_vms = ''
                    for u_name in sorted(current_vm_data):
                        actual_u_name = u_name.split('_-_')[0]
                        individual_vms += f'''<tr>
                                <td>{actual_u_name}</td>
                                <td><div id="{u_name}_public_ip"></div></td>
                                <td><div id="{u_name}_genuine_ip"></div></td>
                                <td><div id="{u_name}_uptime"></div></td>
                                <td><div id="{u_name}_success"></div></td>
                                <td><div id="{u_name}_cpu"></div></td>
                                <td><div id="{u_name}_ram"></div></td>
                                <td><div id="{u_name}_response_time"></div></td>
                                </tr>
                                '''
                    table_vm_data = f'''<table>
                            <tr>
                            <th>User ID</th>
                            <th>Public IP</th>
                            <th>Genuine IP</th>
                            <th>Uptime</th>
                            <th>Success</th>
                            <th>CPU(%)</th>
                            <th>RAM(%)</th>
                            <th>Response Time (ms)</th>
                            </tr>
                            {individual_vms}
                            </table>'''
                    turbo_app.push(turbo_app.update(table_vm_data, 'vm_data'))
                    last_vm_data = {}
                    last_host_data = {}
                    last_vm_activity = {}
                    old_current_vm_data = current_vm_data
                for u_name in sorted(current_vm_data):
                    if u_name not in last_vm_data or last_vm_data[u_name] == {}:
                        last_vm_data[u_name] = {}
                    for item in ['public_ip', 'genuine_ip', 'uptime', 'success', 'cpu', 'ram', 'response_time']:
                        if item in current_vm_data[u_name]:
                            if item not in last_vm_data[u_name] or current_vm_data[u_name][item] != last_vm_data[u_name][item]:
                                turbo_app.push(turbo_app.update(current_vm_data[u_name][item], f'{u_name}_{item}'))
                                last_vm_data[u_name][item] = current_vm_data[u_name][item]
                    if 'working_cond' in current_vm_data[u_name]:
                        if 'working_cond' not in last_vm_data[u_name] or (current_vm_data[u_name]['working_cond'] == 'Working' and last_vm_data[u_name]['working_cond'] != 'Working'):
                            last_vm_data[u_name]['working_cond'] = 'Working'
                            options = f"""<form method="POST" action="/auto_action/">
                            <select name="{u_name}" onchange="this.form.submit()">
                            '<option value="Pause">Stopped</option>'
                            '<option value="Resume" selected>Working</option>'
                            </select>
                            </form
                            """
                            turbo_app.push(turbo_app.update(options, f'{u_name}_working_cond'))
                            last_vm_data[u_name]['working_cond'] = current_vm_data[u_name]['working_cond']
                        elif 'working_cond' not in last_vm_data[u_name] or (
                                current_vm_data[u_name]['working_cond'] == 'Stopped' and last_vm_data[u_name]['working_cond'] != 'Stopped'):
                            last_vm_data[u_name]['working_cond'] = 'Stopped'
                            options = f"""<form method="POST" action="/auto_action/">
                            <select name="{u_name}" onchange="this.form.submit()">
                            '<option value="Resume">Working</option>'
                            '<option value="Pause" selected>Stopped</option>'
                            </select>
                            </form>
                            """
                            turbo_app.push(turbo_app.update(options, f'{u_name}_working_cond'))
                            last_vm_data[u_name]['working_cond'] = current_vm_data[u_name]['working_cond']
                if 'host_cpu' not in last_host_data or last_host_data['host_cpu'] != host_cpu:
                    turbo_app.push(turbo_app.update(str(host_cpu), 'host_cpu'))
                    last_host_data['host_cpu'] = host_cpu
                if 'host_ram' not in last_host_data or last_host_data['host_ram'] != host_ram:
                    turbo_app.push(turbo_app.update(str(host_ram), 'host_ram'))
                    last_host_data['host_ram'] = host_ram
                turbo_app.push(turbo_app.update(debug_data, 'debug_data'))
            except Exception as e:
                debug_host(repr(e))
            system_caller('cls')
            sleep(1)
        else:
            sleep(0.1)
            if not_updating_counter >= 100:
                targets = sorted(vm_data_update_connections)
                for u_name in targets:
                    Thread(target=send_blank_command, args=(u_name,)).start()
                not_updating_counter = 0
            else:
                not_updating_counter += 1


app = Flask(__name__, template_folder=getcwd().replace('\\','/')+'/templates/') ### might cause issue later (template not found)
turbo_app = Turbo(app)

def flask_operations():
    def return_adfly_link_page(u_name):
        data = ''
        for para_length in range(randrange(400, 1000)):
            data += choice(paragraph_lines) + '.'
            if randrange(0, 10) % 5 == 0:
                data += f"<a href='/adf_link_click?u_name={u_name}&random={generate_random_string(10,50)}'> CLICK HERE </a>"
        html_data = f"""<HTML><HEAD><TITLE>Nothing's here {u_name}</TITLE></HEAD><BODY>{data}</BODY></HTML>"""
        return html_data


    @app.route('/')
    @app.route('/auto_action/', methods=['GET'])
    def root_url():
        global old_current_vm_data, last_vm_activity, last_host_data, last_one_click_start_data, last_vm_data
        last_vm_data = {}
        last_vm_activity = ''
        last_one_click_start_data = ''
        old_current_vm_data = []
        last_host_data = {}
        return render_template('vm_stat.html')


    @app.route('/auto_action/', methods=['POST'])
    def auto_action():
        action = target = ''
        for target in request.form.to_dict():
            action = request.form.to_dict()[target]
        if target == "pull_code_github" or action == "pull_code_github":
            Thread(target=system_caller, args=('git pull',)).start()
        return redirect('/')


    @app.route('/user_load_links', methods=['GET'])
    def user_load_links():
        u_name = request.args.get("u_name")
        if u_name:
            return return_adfly_link_page(u_name)
        else:
            return return_adfly_link_page(my_u_name)


    @app.route('/adf_link_click/', methods=['GET'])
    def adf_link_click():
        u_name = request.args.get('u_name')
        all_u_names = [row[0] for row in db_cursor.execute("SELECT u_name from user_data")]
        u_name_ids = [row[0].split() for row in db_cursor.execute(f"SELECT self_adfly_ids from user_data where u_name = '{u_name}'")]
        if u_name in all_u_names and u_name_ids and u_name_ids[0]:
            id_to_serve = choice(u_name_ids[0])
        else:
            while True:
                u_name = choice(all_u_names)
                u_name_ids = [row[0].split() for row in db_cursor.execute(f"SELECT self_adfly_ids from user_data where u_name = '{u_name}'")]
                if u_name_ids and u_name_ids[0]:
                    id_to_serve = choice(u_name_ids[0])
                    break
        adf_link = f"https://{choice(['adf.ly', 'j.gs', 'q.gs'])}/{id_to_serve}/{choice(youtube_links)}"
        return redirect(adf_link)

    app.run(host='0.0.0.0', port=HOST_MAIN_WEB_PORT, debug=True, use_reloader=False, threaded=True)


Thread(target=flask_operations).start()
Thread(target=update_flask_page).start()
Thread(target=accept_connections_from_users).start()
