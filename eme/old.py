import json
import socket
import threading
from tkinter import *

COMMANDS = '\n'.join(['/join <server_ip_add> <port>', '/leave', '/register <handle>', '/all <message>', '/msg <handle> <message>'])

class OurClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Datagram
        self.handle = None
        self.gui_made = False
        self.running = True
        self.serv = False
        self.acc = False

        gui_thread = threading.Thread(target=self.gui_loop)
        recvr_thread = threading.Thread(target=self.recv_msg)

        gui_thread.start()
        recvr_thread.start()

    def recv_msg(self):
        while self.running:
            try:
                msgorig, _ = self.sock.recvfrom(1024)
                msg = self.deserialize(msgorig)
                print(msg)
                if self.gui_made:
                    self.text_area.configure(state='normal')
                    self.text_area.insert('end', msg.get('message') + '\n')
                    self.text_area.yview('end')
                    self.text_area.configure(state='disabled')
            except socket.error:
                pass

    def request(self, message):
        self.sock.sendto(message, (self.host, self.port))
        response, ip_add = self.sock.recvfrom(1024)
        return self.deserialize(response)
    
    def join(self, host=socket.gethostname(), port=12345):
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
    client = OurClient()
    # serv, acc = False, False
    # print('Use /? for a list of commands.')
    # while True:
    #     try:
    #         cmd = input('Enter a command: ')
    #         if cmd == '/?':
    #             print(COMMANDS)
    #         elif not serv and not cmd.startswith('/join'):
    #             print('Error: Disconnection failed. Please connect to the server first.')
    #         elif cmd.startswith('/join') and not serv:
    #             try:
    #                 yes = client.read_cmd(cmd)
    #                 if yes: 
    #                     serv = True
    #             except socket.error:
    #                 client = None
    #                 print('Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.')
    #         elif cmd.startswith('/leave') and serv:
    #             yes = client.read_cmd(cmd)
    #             if yes: 
    #                 serv = False
    #                 client.handle= None
    #         elif client:
    #             if not acc and not cmd.startswith('/register'):
    #                 print('Error: You must register a handle first.')
    #             else:
    #                 client.read_cmd(cmd)
    #                 if client.handle: acc = True
    #     except socket.error as err:
    #         print(f'Error: {err}')