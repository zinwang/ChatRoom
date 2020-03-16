import sys
from PyQt5.QtWidgets import QDialog, QMainWindow, QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont
from frames import loginframe 
from frames import roomframe
from frames import errorframe
import socket
import time


msg = ''
host=""
port=0
nickname=""
welcome=''

client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

app = QApplication(sys.argv)

class ErrorWindow(QDialog):
	def __init__(self,errormsg):
		super().__init__()
		self.ui=errorframe.Ui_Dialog()
		self.ui.setupUi(self)
		self.ui.pushButton.clicked.connect(self.pushButton_Click)
		self.ui.label.setFont(QFont("Arial",8,0))
		self.ui.label.setText(errormsg)
		self.show()
	def pushButton_Click(self):
		self.hide()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = loginframe.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.pushButton_Click)
        self.show()

    def pushButton_Click(self):
    	global host,port,nickname,client_socket
    	host=self.ui.lineEdit.text()
    	portstr=self.ui.lineEdit_2.text()
    	nickname=self.ui.lineEdit_3.text()
    	if host=="" or portstr=="" or nickname=="":
    		self.next=ErrorWindow('Don\'t leave blank field!')
    		self.next.show()
    	else:
    		port=int(portstr)
    		try:
    			client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    			client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    			client_socket.setblocking(0)
    			client_socket.settimeout(3)
    			client_socket.connect((host,port))
    			
    			try:
    				client_socket.send(nickname.encode())
    				global welcome
    				time.sleep(1)
    				welcome=client_socket.recv(4096).decode()
    				if welcome=="false":
    					self.next=ErrorWindow(nickname+' has been used!')
    					self.next.show()
    					client_socket.shutdown(2)
    					client_socket.close()
    				else:
    					self.hide()
    					self.next=RoomWindow()
    					self.next.show()
    			except socket.timeout as e:
    				print(e)

    		except ConnectionRefusedError:
    			self.next=ErrorWindow('Cannot connect to the server!')
    			self.next.show()
    			client_socket.close()


class RoomWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = roomframe.Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.textEdit.setReadOnly(1)
		self.ui.textEdit.setFont(QFont("Arial",14,0))
		self.ui.textEdit.append('welcome to the room!\n'+welcome)
		self.ui.pushButton.clicked.connect(self.pushButton_Click)
		self.ui.pushButton_2.clicked.connect(self.pushButton2_Click)
		self.thread=ClientThread()
		self.thread.update_signal.connect(self.update_msg)
		self.thread.start()
		global app
		app.aboutToQuit.connect(self.close)
		self.show()

	def stop_work(self):
		self.thread.stop()
		self.thread.exit()

	def close(self):
		self.stop_work()
		sys.exit()


	def update_msg(self,msg):
		self.ui.textEdit.append(msg)


	def pushButton_Click(self):
		global msg
		global client_socket
		msg=self.ui.lineEdit.text()
		if msg!="":
			try:
				client_socket.send(msg.encode())
				self.ui.lineEdit.setText("")
			except ConnectionResetError:
				self.next=ErrorWindow('Cannot connect to the server!')
				self.next.show()

	def pushButton2_Click(self):
		self.stop_work()
		client_socket.shutdown(2)
		client_socket.close()
		self.hide()
		self.next=LoginWindow()
		self.next.show()


class ClientThread(QThread):
	def __init__(self):
		QThread.__init__(self)
		self.stop_flag=0

	update_signal=pyqtSignal(str)

	def run(self):
		while(not self.stop_flag):
			try:
				data = client_socket.recv(4096).decode()
				if data!="":
					self.update_signal.emit(data)
			except Exception as e:
				pass
				#print(e)

	def stop(self):
		self.stop_flag=1




w = LoginWindow()
w.show()
sys.exit(app.exec_())
