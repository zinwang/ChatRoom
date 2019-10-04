# -*- coding: utf-8 -*-
import socket,threading
flag = 0
msg = ''
lock = threading.Lock()

#host = '127.0.0.1'
#port = 5002
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
client_socket.setblocking(0)
client_socket.settimeout(3)


class InputThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global flag, msg
        while 1:
            msg = input()
            if len(msg):
                lock.acquire()
                flag = 1
                lock.release()

class ClientThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global flag
        global msg
        while 1:
            try:
                data = client_socket.recv(4096).decode()
                if len(data):
                    print(data)
            except:
                pass
            if flag:
                try:
                    client_socket.send(msg.encode())
                except socket.error as e:
                    pass
                    #print(e)
                lock.acquire()
                flag = 0
                lock.release()


if __name__=='__main__':
    host=input("host:")
    port=int(input("port:"))
    

    try:
        client_socket.connect((host,port))
        print("success!\nwelcome to the room!")
        while(1):
            nickname=input("nickname:")
            client_socket.send(nickname.encode())
            if client_socket.recv(4096).decode()=="false":
                print(nickname+" has been already used!")
            else:
                print(client_socket.recv(4096).decode())
                break
    except socket.error as e:
        pass
        #print(e)

    t1 = InputThread()
    t2 = ClientThread()
    t1.start()
    t2.start()
