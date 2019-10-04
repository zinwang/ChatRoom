import socket 
import select
import time


def broadcast(sock,msg):
	#broadcast function
	for socket in connection_list:
		if socket!=server_socket and socket!=sock:
			try:
				socket.send(msg.encode())
			except Exception as e:
				pass
				


def leave(sock,name,addr):
	#diconnect function
	global log
	connection_list.remove(sock)
	name_list.remove(name)
	del name_dic[addr]
	message="\n[*]"+name+" left the room\n"
	log+=message
	print(addr,"disconnected")
	cnt="are"
	if (len(connection_list)-1)<=1:
		cnt="is"
	message+="[*]There {cnt} {num} people in the room\n[*]".format(cnt=cnt,num=len(connection_list)-1)
	for i in name_list:
		message+=i+", "
	message=message.strip(", ")
	message+=" {cnt} online\n".format(cnt=cnt)
	broadcast(sock,message)
	sock.close()

if __name__=='__main__':

	connection_list=[]
	name_dic={}
	name_list=[]
	log=""
	
	ans=input("do you want to run it on localhost?(y/n)").lower()
	if ans=="y" or ans=="yes":
		host='127.0.0.1'
	else:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		host=s.getsockname()[0]
		s.close()

	#print(host)

	port=int(input("port:"))
	
	server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	server_socket.bind((host,port))
	server_socket.listen(10)

	connection_list.append(server_socket)
	print("Chat server started on " +host+":"+str(port))
	
	while(1):
		r_list,w_list,e_list=select.select(connection_list,[],[])
		print(r_list)
		if len(log)>2048:
			log=""
		for sock in r_list:
			if sock==server_socket:
				connection,addr=server_socket.accept()
				flag=0
				
				name=connection.recv(4096).decode().strip()
				print(name,"t")
				for i in name_list:
					if name==i:
						connection.send("false".encode())
						flag=1
				

				if not flag:
					name_dic[str(connection.getpeername())]=name
					name_list.append(name)
					connection_list.append(connection)
					message="\n[*]"+name+" entered the room\n"
					notify=message
					print(str(addr)+" connected")
					cnt="are"
					if (len(connection_list)-1)<=1:
						cnt="is"
					message+="[*]There {cnt} {num} people in the room\n[*]".format(cnt=cnt,num=len(connection_list)-1)
					for i in name_list:
						message+=i+", "
					message=message.strip(", ")
					message+=" {cnt} online\n".format(cnt=cnt)
					broadcast(connection,message)
					time.sleep(3)
					connection.send((log+message).encode())
					log+=notify+"\n"
			else:
				addr=str(sock.getpeername())
				name=name_dic[addr]
				data=""
				try:
					data=sock.recv(4096).decode()
					if data!="":
						log+=name+":"+data+"\n"
						sock.send((name+":"+data).encode())
						broadcast(sock,name+":"+data)
						print(str(sock.getpeername())+":"+data)
				except ConnectionResetError as e:
					leave(sock,name,addr)
					continue
				else:
					if data=="":
						leave(sock,name,addr)
						continue
				continue

	server_socket.close()
