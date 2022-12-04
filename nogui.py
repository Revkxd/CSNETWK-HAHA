import json
import socket
import threading
from tkinter import *

COMMANDS = '\n'.join(['/join <server_ip_add> <port>', '/leave', '/register <handle>', '/all <message>', '/msg <handle> <message>'])

class Client:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.handle = None
        self.host = None
        self.port = None

        # threading.Thread(target=self.gui_loop).start()

    def receiver(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            data = self.deserialize(data)
            message = data['message']
            print(message)

    def join(self, host, port):
        try:
            self.sock.connect((host, port))
            self.sock.sendto(self.serialize({'command': 'join'}), (host, port))
            self.host = host
            self.port = port
            threading.Thread(target=self.receiver).start() # Start receiver thread to wait for server responses
        except socket.error as e:
            print(e)

    def leave(self):
        self.sock.sendto(self.serialize({'command': 'leave'}), (self.host, self.port))
        self.sock.close()

    def register(self, handle):
        self.sock.sendto(self.serialize({'command': 'register', 'handle': handle}), (self.host, self.port))
        self.handle = handle

    def msg(self, recipient, message):
        self.sock.sendto(self.serialize({'command': 'msg', 'recipient': recipient, 'message': message}), (self.host, self.port))

    def msg_all(self, message):
        self.sock.sendto(self.serialize({'command': 'all', 'sender': self.handle, 'message': message}), (self.host, self.port))
    
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
            if args: 
                # print(params_err)
                self.text_area.configure(state='normal')
                self.text_area.insert('end', params_err + '\n')
                self.text_area.yview('end')
                self.text_area.configure(state='disabled')
            else: 
                # print('\n'.join(COMMANDS))
                self.text_area.configure(state='normal')
                self.text_area.insert('end', '\n'.join(COMMANDS) + '\n')
                self.text_area.yview('end')
                self.text_area.configure(state='disabled')
        elif cmd == '/join':
            if len(args) != 2: 
                # print(params_err)
                self.text_area.configure(state='normal')
                self.text_area.insert('end', params_err + '\n')
                self.text_area.yview('end')
                self.text_area.configure(state='disabled')
                return False
            elif not self.handle:
                if args[1] == ' ': args[1] = '0'
                self.join(args[0], int(args[1]))
                ans = self.request(self.serialize({'command': 'join'}))
                # print(ans.get('message'))
                self.text_area.configure(state='normal')
                self.text_area.insert('end', ans.get('message') + '\n')
                self.text_area.yview('end')
                self.text_area.configure(state='disabled')
                return True if ans.get('message') == 'Connection to the Message Board Server is successful.' else False
            else:
                # print("You're already connected")
                self.text_area.configure(state='normal')
                self.text_area.insert('end', "You're already connected\n")
                self.text_area.yview('end')
                self.text_area.configure(state='disabled')
                return False
        elif cmd == '/leave':
            if args: 
                # print(params_err)
                self.text_area.configure(state='normal')
                self.text_area.insert('end', params_err + '\n')
                self.text_area.yview('end')
                self.text_area.configure(state='disabled')
                return False
            else: 
                ans = self.request(self.serialize({'command': 'leave'}))
                # print(ans.get('message'))
                self.text_area.configure(state='normal')
                self.text_area.insert('end', ans.get('message') + '\n')
                self.text_area.yview('end')
                self.text_area.configure(state='disabled')
                return True if ans.get('message') == 'Connection closed. Thank you!' else False
        elif cmd == '/register':
            if len(args) != 1: 
                # print(params_err)
                self.text_area.configure(state='normal')
                self.text_area.insert('end', params_err + '\n')
                self.text_area.yview('end')
                self.text_area.configure(state='disabled')
                return False
            else: 
                ans = self.register(args[0])
                # print(ans.get('message'))
                self.text_area.configure(state='normal')
                self.text_area.insert('end', ans.get('message') + '\n')
                self.text_area.yview('end')
                self.text_area.configure(state='disabled')
                return True if ans.get('message') == f'Welcome {args[0]}!' else False
        elif cmd == '/all':
            # print(self.msg_all(self.handle, ' '.join(args)))
            self.text_area.configure(state='normal')
            self.text_area.insert('end', self.msg_all(self.handle, ' '.join(args)).get('message') + '\n')
            self.text_area.yview('end')
            self.text_area.configure(state='disabled')
        elif cmd == '/msg':
            # print(self.msg(args[0], ' '.join(args[1:])))
            self.text_area.configure(state='normal')
            self.text_area.insert('end', self.msg(args[0], ' '.join(args[1:])) + '\n')
            self.text_area.yview('end')
            self.text_area.configure(state='disabled')
        else:
            # print('Error: Command not found.')
            self.text_area.configure(state='normal')
            self.text_area.insert('end', 'Error: Command not found.')
            self.text_area.yview('end')
            self.text_area.configure(state='disabled')
    
    def on_submit(self):
        try:
            cmd = self.input_area.get('1.0', 'end').strip('\n')
            if cmd == '/?':
                print(COMMANDS)
            elif not self.serv and not cmd.startswith('/join'):
                print('Error: Disconnection failed. Please connect to the server first.')
            elif cmd.startswith('/join') and not self.serv:
                try:
                    yes = self.read_cmd(cmd)
                    if yes: 
                        self.serv = True
                except socket.error:
                    print('Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.')
            elif cmd.startswith('/leave') and self.serv:
                yes = self.read_cmd(cmd)
                if yes: 
                    self.serv = False
                    self.handle= None
            else:
                if not self.acc and not cmd.startswith('/register'):
                    print('Error: You must register a handle first.')
                else:
                    self.read_cmd(cmd)
                    if self.handle: self.acc = True
        except socket.error as err:
            print(f'Error: {err}')
        finally:
            self.input_area.delete('1.0', 'end')

    def exit_window(self):
        self.win.destroy()
        self.running = False
        self.leave()
        if self.serv:
            self.read_cmd('/leave')
        exit(0)
    
    def gui_loop(self):
        self.win = Tk()
        self.win.title('Message Board Client')
        self.win.resizable = (False, False)
        self.win.configure(bg='black')

        self.chat_label = Label(self.win, text='Responses:', bg='white', font=('Arial', 12))
        self.chat_label.pack()

        self.text_area = Text(self.win, bg='white', font=('Arial', 12), height=20, width=70)
        self.text_area.pack()
        self.text_area.config(state='disabled', wrap='word')

        self.msg_label = Label(self.win, text='Message:', bg='white', font=('Arial', 12))
        self.msg_label.pack()

        self.input_area = Text(self.win, height=3)
        self.input_area.pack()

        self.send_button = Button(self.win, text='Send', command=self.on_submit)
        self.send_button.pack()
        self.win.bind('<Return>', self.on_submit)
        self.win.protocol('WM_DELETE_WINDOW', self.exit_window)
        self.gui_made = True
        self.win.mainloop()

if __name__ == '__main__':
    client = Client()
    while True:
        cmd = input()
        if cmd.startswith('/join'):
            cmd = cmd.split()
            if len(cmd) == 3:
                client.join(cmd[1], int(cmd[2]))
            else:
                print('Invalid command. Try again.')
        elif cmd.startswith('/leave'):
            client.leave()
        elif cmd.startswith('/register'):
            cmd = cmd.split()
            if len(cmd) == 2:
                client.register(cmd[1])
            else:
                print('Invalid command. Try again.')
        elif cmd.startswith('/msg'):
            cmd = cmd.split()
            if len(cmd) >= 3:
                client.msg(cmd[1], ' '.join(cmd[2:]))
            else:
                print('Invalid command. Try again.')
        elif cmd.startswith('/all'):
            cmd = cmd.split()
            if len(cmd) >= 2:
                client.msg_all(' '.join(cmd[1:]))
            else:
                print('Invalid command. Try again.')
        elif cmd == '/help':
            print(COMMANDS)
        else:
            print('Invalid command. Try again.')