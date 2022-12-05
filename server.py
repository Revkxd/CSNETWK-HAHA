import json
import socket

class OurServer:
    def __init__(self, host=socket.gethostname(), port=12345):
        self.addresses = [] # Stores IP Address of connected clients
        self.users = {} # Dictionary storing username:ip_address pairs
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Datagram
        self.sock.bind((host, port))

    def wait(self, buffer=1024): # Listen for client requests
        req, ip_add = self.sock.recvfrom(buffer)
        req = self.deserialize(req)
        print(f'Client {ip_add} sent: {req}') # Debug print, can remove after
        return req, ip_add

    def respond(self, message, ip_add): # Send response to client
        resp = self.serialize(self.parse_cmd(message, ip_add))
        self.sock.sendto(resp, ip_add)

    def join(self):
        if ip_add not in self.addresses:
            self.addresses.append(ip_add)
        print('Addresses after join:', self.addresses) # Debug print, remove after
        message = {'response':'success', 'message':'Connection to the Message Board Server is successful.'}
        return message
    
    def leave(self):
        user = None
        for key, value in self.users.items():
            if value == ip_add:
                user = key
        if user: 
            self.users.pop(user)
        self.addresses.remove(ip_add)
        print('Users after leave:', self.users) # Debug print, remove after
        print('Addresses after leave:', self.addresses) # Debug print, remove after
        # message = {'response':'success', 'message':'Connection closed. Thank you!'}
        # return message

    def register(self, username):
        if username not in self.users:
            self.users.update({username: ip_add})
            print('Users after register:', self.users) # Debug print, remove after
            return {'response':'success', 'message': f'Welcome {username}!'}
        else:
            return {'response':'error', 'message':'Error: Registration failed. Handle or alias already exists.'}

    def msg(self, sender, recipient, message):
        rcvr = self.users.get(recipient)
        if rcvr:
            send_it = {'response': 'message', 'message': f'[From {sender}]: {message}'}
            self.sock.sendto(self.serialize(send_it), rcvr)
            return {'response': 'success', 'message': f'[To {recipient}]: {message}'}
        else:
            return {'response': 'error', 'message':'Error: Handle or alias not found.'}

    def msgall(self, sender, message):
        send_it = {'response': 'message', 'message': f'{sender}: {message}'}
        for rcvr in self.users:
            if rcvr != sender:
                self.sock.sendto(self.serialize(send_it), self.users.get(rcvr))
        return send_it

    def parse_cmd(self, req, ip_add):
        cmd = req.get('command')
        if cmd == 'join':
            return self.join()
        elif cmd == 'leave':
            self.leave()
        elif cmd == 'register':
            return self.register(req.get('handle'))
        elif cmd == 'msg':
            sender = None
            for key, value in self.users.items():
                if value == ip_add:
                    sender = key
                    break
            return self.msg(sender, req.get('recipient'), req.get('message'))
        elif cmd == 'all':
            sender = None
            for key, value in self.users.items():
                if value == ip_add:
                    sender = key
                    break
            return self.msgall(sender, req.get('message'))
        else:
            return {'response':'error', 'message':'Error: Command not found.'}

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
