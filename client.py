import json
import socket
import threading
from tkinter import *

COMMANDS = '\n'.join(['/join <server_ip_add> <port>', '/leave', '/register <handle>', '/all <message>', '/msg <handle> <message>'])

class OurClient:
    def __init__(self, host=socket.gethostname(), port=12345):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Datagram
        self.handle = None
    
    def request(self, message):
        self.sock.sendto(message, (self.host, self.port))
        response, ip_add = self.sock.recvfrom(1024)
        return self.deserialize(response)
    
    def join(self, host, port):
        self.host = host
        self.port = port
        self.sock.settimeout(3)
        self.sock.connect((self.host, self.port))

    def leave(self):
        self.sock.close()
    
    def register(self, handle):
        resp = self.request(self.serialize({'command': 'register', 'handle': handle}))
        if resp.get('message') == f'Welcome {handle}!':
            self.handle = handle
        return resp
    
    def msg_all(self, sender, message):
        return self.request(self.serialize({'command': 'all', 'sender': sender, 'message': message})).get('message')
    
    def msg(self, recipient, message):
        return self.request(self.serialize({'command': 'msg', 'recipient': recipient, 'message': message})).get('message')

    def serialize(self, dict):
        val = bytes(json.dumps(dict), 'utf-8')
        return val

    def deserialize(self, data):
        val = json.loads(data.decode('utf-8'))
        return val
    
    def read_cmd(self, command):
        cmd, *args = command.split(' ')
        params_err = 'Error: Command parameters do not match or is not allowed.'
        if cmd == '/?':
            if args: print(params_err)
            else: print('\n'.join(COMMANDS))
        elif cmd == '/join':
            if len(args) != 2: 
                print(params_err)
                return False
            elif not self.handle: 
                self.join(args[0], int(args[1]))
                ans = self.request(self.serialize({'command': 'join'}))
                print(ans.get('message'))
                return True if ans.get('message') == 'Connection to the Message Board Server is successful.' else False
            else:
                print("You're already connected")
                return False
        elif cmd == '/leave':
            if args: 
                print(params_err)
                return False
            else: 
                ans = self.request(self.serialize({'command': 'leave'}))
                print(ans.get('message'))
                return True if ans.get('message') == 'Connection closed. Thank you!' else False
        elif cmd == '/register':
            if len(args) != 1: 
                print(params_err)
                return False
            else: 
                ans = self.register(args[0])
                print(ans.get('message'))
                return True if ans.get('message') == f'Welcome {args[0]}!' else False
        elif cmd == '/all':
            print(self.msg_all(self.handle, ' '.join(args)))
        elif cmd == '/msg':
            print(self.msg(args[0], ' '.join(args[1:])))
        else:
            print('Error: Command not found.')

if __name__ == '__main__':
    serv, acc = False, False
    print('Use /? for a list of commands.')
    client = None

    while True:
        try:
            cmd = input('Enter a command: ')
            if cmd == '/?':
                print(COMMANDS)
            elif not serv and not cmd.startswith('/join'):
                print('Error: Disconnection failed. Please connect to the server first.')
            elif cmd.startswith('/join') and not serv:
                try:
                    _, *args = cmd.split(' ')
                    client = OurClient(args[0], int(args[1]))
                    yes = client.read_cmd(cmd)
                    if yes: 
                        serv = True
                except socket.error:
                    client = None
                    print('Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.')
            elif cmd.startswith('/leave') and serv:
                yes = client.read_cmd(cmd)
                if yes: 
                    serv = False
                    client.handle= None
            elif client:
                if not acc and not cmd.startswith('/register'):
                    print('Error: You must register a handle first.')
                else:
                    client.read_cmd(cmd)
                    if client.handle: acc = True
        except socket.error as err:
            print(f'Error: {err}')