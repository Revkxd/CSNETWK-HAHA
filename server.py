import json
import socket

class OurServer:
    def __init__(self, host=socket.gethostname(), port=12345):
        self.users = {} # Dictionary storing username:ip_address pairs
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Datagram
        self.sock.bind((host, port))

    def wait(self, buffer=1024): # Listen for client requests
        req, ip_add = self.sock.recvfrom(buffer)
        req = self.deserialize(req)
        print(f'Client {ip_add} sent: {req}') # Debug print, can remove after
        return req, ip_add

    def respond(self, message, ip_add): # Send response to client
        resp = self.serialize(self.parse_cmd(message))
        self.sock.sendto(resp, ip_add)

    def join(self):
        # TODO connect the ip of the client 
        
        return 'Connection to the Message Board Server is successful.'
    
    def leave(self):
        # TODO remove the ip of the client
        return 'Connection closed. Thank you!'

    def register(self, username): # Registers a user
        if username not in self.users:
            self.users.update({username: ip_add})
            print('Users:', self.users) # Debug print, remove after
            return f'Welcome {username}!'
        else:
            return 'Error: Registration failed. Handle or alias already exists.'

    def msg(self, sender, recipient, message):
        if message:
            rcvr = self.users.get(recipient)
            if rcvr:
                send_it = f'[From {sender}]: {message}'
                self.sock.sendto(self.serialize(send_it), rcvr)
                return f'[To {recipient}]: {message}'
            else:
                return 'Error: Handle or alias not found.'

    def msgall(self, sender, message):
        for rcvr in self.users:
            if rcvr != sender:
                send_it = f'{sender}: {message}'
                self.sock.sendto(self.serialize(send_it), self.users.get(rcvr))
        return f'{sender}: {message}'

    def parse_cmd(self, req):
        cmd = req.get('command')
        if cmd == 'join':
            return self.join()
        elif cmd == 'leave':
            return self.leave()
        elif cmd == 'register':
            return self.register(req.get('handle'))
        elif cmd == 'msg':
            return self.msg(req.get('sender'), req.get('recipient'), req.get('message'))
        elif cmd == 'all':
            return self.msgall(req.get('sender'), req.get('message'))
        else:
            return 'Error: Command not found.'

    def serialize(self, dict): # Turns JSON into bytes
        val = bytes(json.dumps(dict), 'utf-8')
        return val

    def deserialize(self, data): # Turns bytes into JSON
        val = json.loads(data.decode('utf-8'))
        return val

if __name__ == '__main__':
    server = OurServer()
    print('Server running at {}:{}'.format(server.sock.getsockname()[0], server.sock.getsockname()[1])) # I want this here, off my case
    while True:
        msg, ip_add = server.wait()
        server.respond(msg, ip_add)
