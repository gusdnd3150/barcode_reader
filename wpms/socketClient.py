import socket
import threading
import traceback
import time


#threading.Thread
from conf.logconfig import logger

class SocketClient(threading.Thread):
    ip = ''
    port = 0
    type = ''
    scType = ''
    isRun = False
    client_socket = None
    mainInstance = None
    tryCount = 0


    def __init__(self, ip, port, mainInstance):
        super().__init__()
        self.name = '{}:{}'.format(ip, port)# 스레드 명
        self.ip = ip
        self.port = int(port)
        self.mainInstance = mainInstance

    def run(self):
         self.initClient()

    def initClient(self):

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.ip, int(self.port)))
            self.tryCount= 0
            self.isRun = True
            self.mainInstance.isRunClient = True
            logger.info('Connection Success :: ip={}, port={}'.format(self.ip, self.port))
            # 서버로 부터 메세지 받기
            while self.isRun:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                byte_array = bytearray(data)
                self.mainInstance.reciveSocketData(byte_array)

        except:
            logger.info('Connection DisConnected')
            self.client_socket = None
            self.isRun = False
            self.mainInstance.isRunClient = False
            self.tryCount = self.tryCount + 1
            logger.info('client connect try count :: '+str(self.tryCount))
            time.sleep(5)
            self.initClient()
            traceback.print_exc()


    def sendMsg(self, msg, alsias):
        try:
            byte_array_output_stream = bytearray()
            # 바이트를 추가
            byte_array_output_stream.extend(alsias.encode('utf-8'))
            #byte_array_output_stream.extend(msg.encode('utf-8'))
            byte_array_output_stream.extend(msg)
            byte_array_output_stream.append(0) # null 처리
            # 바이트 배열로 변환
            byte_array = bytes(byte_array_output_stream)
            self.client_socket.send(byte_array)
        except:
            logger.info('send Message Fail')
            # self.isRun = False
            # self.mainInstance.isRunClient = False
            # self.initClient()
            traceback.print_exc()


    def closeSocket(self):
        self.client_socket.close()
        self.isRun = False
        logger.info('Connection DisConnected')
        self.mainInstance.isRunClient = False
        self.initClient()
        traceback.print_exc()
