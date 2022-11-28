import json
import socket
import threading
from tkinter import *

COMMANDS = '\n'.join(['/join <server_ip_add> <port>', '/leave', '/register <handle>', '/all <message>', '/msg <handle> <message>'])

class OurClient:
    def __init__(self, host=socket.gethostname(), port=12345):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Datagram
        self.handle = None
        self.isConnected = False #Cheap Fix
    
    def request(self, message):
        self.sock.sendto(message, (self.host, self.port))
        response, ip_add = self.sock.recvfrom(1024)
        return self.deserialize(response)
    
    def join(self, host, port):
        self.host = host
        self.port = port
        self.sock.connect((self.host, self.port))

    def leave(self): # TODO this doesn't disconnect the client
        self.sock.close()
    
    def register(self, handle):
        resp = self.request(self.serialize({'command': 'register', 'handle': handle}))
        if resp.get('message') == f'Welcome {handle}!':
            self.handle = handle
        return resp
    
    def msg_all(self, sender, message):
        return self.request(self.serialize({'command': 'all', 'sender': sender, 'message': message})).get('message')
    
    def msg(self, sender, recipient, message):
        return self.request(self.serialize({'command': 'msg', 'sender': sender, 'recipient': recipient, 'message': message})).get('message')

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
            elif self.isConnected==True: #Cheap Fix
                self.join(args[0], int(args[1]))
                ans = self.request(self.serialize({'command': 'join'}))
                print(ans.get('message'))
                return True if ans.get('message') == 'Connection to the Message Board Server is successful.' else False
            else: #Cheap Fix
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
            print(self.msg(self.handle, args[0], ' '.join(args[1:])))
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
                print('Error: You must join a server first.')
            elif cmd.startswith('/join') and not serv:
                client = OurClient()
                yes = client.read_cmd(cmd)
                if yes: 
                    serv = True
            elif cmd.startswith('/leave') and serv and acc:
                yes = client.read_cmd(cmd)
                if yes: 
                    serv = False
                    client.isConnected=False #Cheap Fix
            elif client:
                client.isConnected=True
                if not acc and not cmd.startswith('/register'):
                    print('Error: You must register a handle first.')
                else:
                    client.read_cmd(cmd)
                    if client.handle: acc = True
        except socket.error as err:
            print(f'Error: {err}')