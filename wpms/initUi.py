import threading
import sys
import os
import traceback
import json
import serial
import serial.tools.list_ports
import schedule

from wpms.barcode import Barcode
from conf.logconfig import logger
from wpms.socketClient import SocketClient


class InitWindow():
    timer = None
    isRunClient = False  # 소켓 클라 연결 상태
    isConBardoe = False  # 바코드 연결 상태
    clientThread = None
    barcodeThread =None
    barcodeAlias= ''
    keepMsg = ''
    
    def __init__(self):
        #super().__init__()
        logger.info('program start')
        try:
            current_script_path = os.path.dirname(os.path.abspath(__file__))
            project_path = os.path.dirname(current_script_path)
            confFile = project_path + '\config.json'

            logger.info('config file path :: '+confFile)

            with open(confFile, 'r') as file:
                data = json.load(file)

            # JSON 데이터 출력
            logger.info(str(data['SDOP_IP']))

            ip = data['SDOP_IP']
            port = data['SDOP_PORT']
            serial_port = data['SERIAL_PORT']
            reconSec = data['RECON_SEC']
            procCd = data['PROC_CD']
            lineCd = data['LINE_CD']
            alias = data['ALIAS']
            keepSec = data['KEEP_SEC']
            self.barcodeAlias = alias.ljust(10, ' ')+lineCd.ljust(4, ' ')+procCd.ljust(4, ' ')
            self.keepMsg = 'KEEPALIVE'.ljust(10, ' ') + lineCd.ljust(4, ' ') + procCd.ljust(4, ' ')

            logger.info(ip+'//'+port+'//'+str(serial_port))
            logger.info("사용 가능한 COM 포트:"+str(self.find_com_port()))

            self.barcodeThread = Barcode(serial_port,reconSec, self) # main 인스턴스도 함께 넘김
            #self.barcodeThread.daemon = True
            self.barcodeThread.start()

            self.clientThread = SocketClient(ip, port, self) # main 인스턴스도 함께 넘김
            self.clientThread.daemon = True
            self.clientThread.start()

            schedule.every(int(keepSec)).seconds.do(self.keepAlive)
            # step4.스캐쥴 시작
            while True:
                schedule.run_pending()

        except:
            logger.info(str(traceback.print_exc()))
            traceback.print_exc()

    def keepAlive(self):
        if self.isRunClient:
            self.clientThread.sendMsg(''.ljust(10, ' ').encode('utf-8'), self.keepMsg)
            logger.info('KEEPALIVE SEND')
        # if self.isRun and self.client_socket != None:
        #     logger.info('wwwwww')
        #     byte_array_output_stream = bytearray()
        #     byte_array_output_stream.extend('KEEPALIVE'.encode('utf-8')) # 9자리
        #     # byte_array_output_stream.extend(msg.encode('utf-8'))
        #     byte_array_output_stream.append(0)  # null 처리
        #     # 바이트 배열로 변환
        #     byte_array = bytes(byte_array_output_stream)
        #     self.client_socket.send(byte_array)



    def reciveBarcodeData(self, barcodeData):
        try:
            logger.info('barcodeData ::'+str(barcodeData))
            logger.info('isRunClient ::' + str(self.isRunClient))
            if(self.isRunClient):
                self.clientThread.sendMsg(barcodeData,self.barcodeAlias)
            else:
                logger.info('Client is not connected')
        except:
            self.clientThread.initClient()
            traceback.print_exc()

    def reciveSocketData(self,byteMsg):
        logger.info('reciveSocketData data ::'+ str(byteMsg))


    def find_com_port(self):
        available_ports = serial.tools.list_ports.comports()
        com_ports = [port.device for port in available_ports if 'COM' in port.device.upper()]
        if not com_ports:
            logger.info("사용 가능한 COM 포트를 찾을 수 없습니다.")
            return ' COM 포트를 찾을 수 없습니다.'
            #raise Exception("사용 가능한 COM 포트를 찾을 수 없습니다.")
        return com_ports






