import json
import socket
import threading
from tkinter import *

COMMANDS = '\n'.join(['/join <server_ip_add> <port>', '/leave', '/register <handle>', '/all <message>', '/msg <handle> <message>', 
                    '/creategc <group_name>', '/joingc <group_name>', '/msggc <group_name> <message>', '/leavegc <group_name>', '/listgc', '/emojis'])
EMOJIS = '\n'.join([':blue_heart:', ':red_heart:', ':green_heart:', ':yellow_heart:', ':purple_heart:', ':broken_heart:', ':star:'])

class da_client:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = None
        self.port = None
        self.serv = False
        self.acc = False
        self.thread_running = False
        self.receiver_thread = threading.Thread(target=self.receiver)

    def receiver(self):
        while True and self.thread_running==True:
            try:
                data, addr = self.sock.recvfrom(1024)
                data = self.deserialize(data)
                message = data['message'] if data else "Connection closed. Thank you!" # If data is empty, connection has been closed
                print(message)
                if message.startswith('Welcome'):
                    self.acc = True
                elif message.startswith('Connection to the Message Board'):
                    self.serv = True
            except socket.error as err:
                print(f'Error: Server has been closed')
                break

    def request(self, message):
        try:
            self.sock.settimeout(2)
            self.sock.sendto(message, (self.host, self.port))
            response, ip_add = self.sock.recvfrom(1024)
            return self.deserialize(response)
        except socket.error:
            return None

    def join(self, host, port):
        try:
            self.host = host
            self.port = port
            self.sock.connect((self.host, self.port))
            response = self.request(self.serialize({'command': 'join'}))
            if response and response['command'] == 'join':
                print('Connection to the Message Board Server is successful!')
                self.serv = True
                self.sock.settimeout(None)
                if not self.thread_running:
                    self.thread_running = True
                    self.receiver_thread.start()
            else:
                print('Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.')
        except socket.timeout:
            print('Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.')
        except socket.error as e:
            print(f'Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.')
        except Exception as e:
            print(f'Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.')

    def leave(self):
        if self.serv:
            self.sock.sendto(self.serialize({'command': 'leave'}), (self.host, self.port))
            self.serv = False
            self.acc = False
            self.thread_running = False
            self.sock.shutdown(socket.SHUT_RDWR)
            self.host = None
            self.port = None
        else:
            print('Error: Disconnection failed. Please connect to the server first.')

    def register(self, handle):
        self.sock.sendto(self.serialize({'command': 'register', 'handle': handle}), (self.host, self.port))

    def msg(self, handle, message):
        self.sock.sendto(self.serialize({'command': 'msg', 'handle': handle, 'message': message}), (self.host, self.port))

    def msg_all(self, message):
        self.sock.sendto(self.serialize({'command': 'all', 'message': message}), (self.host, self.port))

    def msg_group(self, name, message):
        self.sock.sendto(self.serialize({'command': 'msg_group', 'name': name, 'message': message}), (self.host, self.port))
    
    def create_group(self, group_name):
        self.sock.sendto(self.serialize({'command': 'create_group', 'name': group_name}), (self.host, self.port))
    
    def join_group(self, group_name):
        self.sock.sendto(self.serialize({'command': 'join_group', 'name': group_name}), (self.host, self.port))
    
    def leave_group(self, group_name):
        self.sock.sendto(self.serialize({'command': 'leave_group', 'name': group_name}), (self.host, self.port))
    
    def list_groups(self):
        self.sock.sendto(self.serialize({'command': 'list_groups'}), (self.host, self.port))
    
    def serialize(self, dict):
        val = bytes(json.dumps(dict), 'utf-8')
        return val

    def deserialize(self, data):
        val = json.loads(data.decode('utf-8'))
        return val

if __name__ == '__main__':
    client = da_client()
    print('Use /? for the list of commands')
    while True:
        cmd = input()
        cmd, *args = cmd.split(' ')
        if cmd == '/?':
            if args: print('Error: Command parameters do not match or is not allowed.')
            else: print(COMMANDS)
        elif cmd == '/emojis':
            if args: print('Error: Command parameters do not match or is not allowed.')
            else: print(EMOJIS)
        elif cmd == '/join':
            if not args or len(args) != 2:
                print('Error: Command parameters do not match or is not allowed.')
            elif client.serv:
                print('Error: You are already connected to the server.')
            elif len(args) == 2:
                try:
                    client.join(args[0], int(args[1]))
                except ValueError:
                    print('Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.')
            else:
                print('Error: Command parameters do not match or is not allowed.')
        elif cmd == '/leave':
            if args:
                print('Error: Command parameters do not match or is not allowed.')
            else:
                client.leave()
                client = da_client()
        elif cmd == '/register':
            if not args or len(args) > 1:
                print('Error: Command parameters do not match or is not allowed.')
            elif not client.serv:
                print('Error: You must connect to the server first.')
            elif client.acc:
                print('Error: You are already registered.')
            elif len(args) == 1:
                client.register(args[0])
            else:
                print('Error: Command parameters do not match or is not allowed.')
        elif cmd == '/msg':
            if not args or len(args) < 2:
                print('Error: Command parameters do not match or is not allowed.')
            elif not client.serv:
                print('Error: You must connect to the server first.')
            elif not client.acc:
                print('Error: You must register a handle first.')
            elif len(args) >= 2:
                client.msg(args[0], ' '.join(args[1:]))
            else:
                print('Error: Command parameters do not match or is not allowed.')
        elif cmd == '/all':
            if not args:
                print('Error: Command parameters do not match or is not allowed.')
            elif not client.serv:
                print('Error: You must connect to the server first.')
            elif not client.acc:
                print('Error: You must register a handle first.')
            elif args:
                client.msg_all(' '.join(args[:]))
            else:
                print('Error: Command parameters do not match or is not allowed.')
        elif cmd == '/creategc':
            if not args or len(args) > 1:
                print('Error: Command parameters do not match or is not allowed.')
            elif not client.serv:
                print('Error: You must connect to the server first.')
            elif not client.acc:
                print('Error: You must register a handle first.')
            elif len(args) == 1:
                client.create_group(args[0])
            else:
                print('Error: Command parameters do not match or is not allowed.')
        elif cmd == '/joingc':
            if not args or len(args) > 1:
                print('Error: Command parameters do not match or is not allowed.')
            elif not client.serv:
                print('Error: You must connect to the server first.')
            elif not client.acc:
                print('Error: You must register a handle first.')
            elif len(args) == 1:
                client.join_group(args[0])
            else:
                print('Error: Command parameters do not match or is not allowed.')
        elif cmd == '/msggc':
            if not args or len(args) < 2:
                print('Error: Command parameters do not match or is not allowed.')
            elif not client.serv:
                print('Error: You must connect to the server first.')
            elif not client.acc:
                print('Error: You must register a handle first.')
            elif len(args) >= 2:
                client.msg_group(args[0], ' '.join(args[1:]))
            else:
                print('Error: Command parameters do not match or is not allowed.')
        elif cmd == '/leavegc':
            if not args or len(args) > 1:
                print('Error: Command parameters do not match or is not allowed.')
            elif not client.serv:
                print('Error: You must connect to the server first.')
            elif not client.acc:
                print('Error: You must register a handle first.')
            elif len(args) == 1:
                client.leave_group(args[0])
            else:
                print('Error: Command parameters do not match or is not allowed.')
        elif cmd == '/listgc':
            if args:
                print('Error: Command parameters do not match or is not allowed.')
            elif not client.serv:
                print('Error: You must connect to the server first.')
            elif not client.acc:
                print('Error: You must register a handle first.')
            else:
                client.list_groups()
        else:
            print('Error: Command not found.')