import json
import socket
import emoji

class da_serv:
    def __init__(self, host=socket.gethostname(), port=12345):
        self.addresses = []
        self.users = {} #  handle:ip_address pairs
        self.groupchats = {} # groupchat_name:[ip_address list] pairs
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))

    def wait(self, buffer=1024): # Listen for client requests
        try:
            req, ip_add = self.sock.recvfrom(buffer)
            req = self.deserialize(req)
            print(f'Client {ip_add} sent: {req}') # Can remove
            return req, ip_add
        except socket.error as err:
            print('Socket error:', err)
            return {'command':'error', 'message': 'Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.'}

    def respond(self, message, ip_add): # Send reply to client
        resp = self.serialize(self.parse_cmd(message, ip_add))
        self.sock.sendto(resp, ip_add)

    def join(self):
        if ip_add not in self.addresses:
            self.addresses.append(ip_add)
        print('Addresses connected to server:', self.addresses) # Can remove
        message = {'command':'join', 'message':'Connection to the Message Board Server is successful.'}
        return message
    
    def leave(self):
        user = None
        for key, value in self.users.items():
            if value == ip_add:
                user = key
        if user: 
            self.users.pop(user)
        self.addresses.remove(ip_add)
        message = {'command':'leave', 'message':'Connection closed. Thank you!'}
        return message

    def register(self, username):
        if username not in self.users:
            self.users.update({username: ip_add})
            print('Current registered users:', self.users) # Can remove
            return {'command':'register', 'message': f'Welcome {username}!'}
        else:
            return {'command':'error', 'message':'Error: Registration failed. Handle or alias already exists.'}

    def msg(self, sender, recipient, message):
        rcvr = self.users.get(recipient)
        splitted_msg = message.split()
        for i, word in enumerate(splitted_msg):
            if word[0] == ':' and word[-1] == ':':
                splitted_msg[i] = emoji.emojize(word)
        message = ' '.join(splitted_msg)
        if rcvr:
            send_it = {'command': 'message', 'message': f'[From {sender}]: {message}'}
            self.sock.sendto(self.serialize(send_it), rcvr)
            return {'command': 'msg', 'message': f'[To {recipient}]: {message}'}
        else:
            return {'command': 'error', 'message':'Error: Handle or alias not found.'}

    def msgall(self, sender, message):
        splitted_msg = message.split()
        for i, word in enumerate(splitted_msg):
            if word[0] == ':' and word[-1] == ':':
                splitted_msg[i] = emoji.emojize(word)
        message = ' '.join(splitted_msg)
        send_it = {'command': 'all', 'message': f'{sender}: {message}'}
        for rcvr in self.users:
            if rcvr != sender:
                self.sock.sendto(self.serialize(send_it), self.users.get(rcvr))
        return send_it
    
    def create_gc(self, name):
        if name in list(self.groupchats.keys()):
            return {'command':'error', 'message': f'Error: Groupchat {name} already exists.'}
        self.groupchats.update({name: []})
        print('Current groupchats:', self.groupchats) # Can remove
        return {'command':'create_gc', 'message': f'Groupchat {name} created.'}

    def join_gc(self, name):
        if name in list(self.groupchats.keys()):
            print('ip add of joiner:', ip_add)
            group_chat = self.groupchats.get(name)
            if ip_add not in group_chat:
                group_chat.append(ip_add)
                print('Current groupchats after joingc:', self.groupchats) # Can remove
                return {'command':'join_gc', 'message': f'You have joined groupchat {name}.'}
            else:
                return {'command':'error', 'message': f'Error: You are already in groupchat {name}.'}
        else:
            return {'command':'error', 'message': f'Error: Groupchat {name} does not exist.'}

    def leave_gc(self, name):
        users_in_gc = self.groupchats.get(name)
        if name in list(self.groupchats.keys()):
            if ip_add in users_in_gc:
                users_in_gc.remove(ip_add)
                return {'command':'leave_gc', 'message': f'You have left groupchat {name}.'}
            else:
                return {'command':'error', 'message': f'Error: You are not in groupchat: {name}.'}
        else:
            return {'command':'error', 'message': f'Error: Groupchat {name} does not exist.'}

    def msg_gc(self, name, message):
        sender = None
        for key, value in self.users.items():
            if value == ip_add:
                sender = key
        splitted_msg = message.split()
        for i, word in enumerate(splitted_msg):
            if word[0] == ':' and word[-1] == ':':
                splitted_msg[i] = emoji.emojize(word)
        message = ' '.join(splitted_msg)
        if name in list(self.groupchats.keys()):
            group_chat = self.groupchats.get(name)
            if ip_add in group_chat:
                for rcvr in group_chat:
                    if rcvr != ip_add:
                        send_it = {'command': 'message', 'message': f'[GC: {name}, Sender: {sender}]: {message}'}
                        self.sock.sendto(self.serialize(send_it), rcvr)
                return {'command': 'msg_gc', 'message': f'[{sender} to {name}]: {message}'}
            else:
                return {'command':'error', 'message': f'Error: You are not in groupchat {name}.'}
        else:
            return {'command':'error', 'message': f'Error: Groupchat {name} does not exist.'}

    def list_gc(self):
        gcs = list(self.groupchats.keys())
        message = 'Available Groupchats:\n' + '\n'.join(gcs)
        return {'command':'list_gc', 'message': message}

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
            return self.msg(sender, req.get('handle'), req.get('message'))
        elif cmd == 'all':
            sender = None
            for key, value in self.users.items():
                if value == ip_add:
                    sender = key
                    break
            return self.msgall(sender, req.get('message'))
        elif cmd == 'create_group':
            return self.create_gc(req.get('name'))
        elif cmd == 'join_group':
            return self.join_gc(req.get('name'))
        elif cmd == 'leave_group':
            return self.leave_gc(req.get('name'))
        elif cmd == 'msg_group':
            return self.msg_gc(req.get('name'), req.get('message'))
        elif cmd == 'list_groups':
            return self.list_gc()
        else:
            return {'command':'error', 'message':'Error: Command not found.'}

    def serialize(self, dict): # Turns JSON into bytes
        val = bytes(json.dumps(dict), 'utf-8')
        return val

    def deserialize(self, data): # Turns bytes into JSON
        val = json.loads(data.decode('utf-8'))
        return val

if __name__ == '__main__':
    server = da_serv(host='localhost')
    print('Server running at {}:{}'.format(server.sock.getsockname()[0], server.sock.getsockname()[1])) # I want this here, off my case
    while True:
        msg, ip_add = server.wait()
        server.respond(msg, ip_add)
