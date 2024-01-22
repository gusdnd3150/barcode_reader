import threading
import sys
import os
import traceback
import json
import serial
import serial.tools.list_ports

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
            self.barcodeAlias = data['BARCODE_ALIAS']

            logger.info(ip+'//'+port+'//'+str(serial_port))
            logger.info("사용 가능한 COM 포트:"+str(self.find_com_port()))

            self.barcodeThread = Barcode(serial_port,reconSec, self) # main 인스턴스도 함께 넘김
            #self.barcodeThread.daemon = True
            self.barcodeThread.start()

            self.clientThread = SocketClient(ip, port, self) # main 인스턴스도 함께 넘김
            self.clientThread.daemon = True
            self.clientThread.start()

        except:
            logger.info(str(traceback.print_exc()))
            traceback.print_exc()


    def reciveBarcodeData(self, barcodeData):
        try:
            logger.info('barcodeData ::'+barcodeData)
            logger.info('isRunClient ::' + str(self.isRunClient))
            if(self.isRunClient):
                self.clientThread.sendMsg(barcodeData,self.barcodeAlias)
            else:
                logger.info('Client is not connected')
        except:
            self.clientThread.initClient()
            traceback.print_exc()

    def reciveSocketData(self,byteMsg):
        logger.info('socket data ::'+ str(byteMsg))


    def find_com_port(self):
        available_ports = serial.tools.list_ports.comports()
        com_ports = [port.device for port in available_ports if 'COM' in port.device.upper()]
        if not com_ports:
            logger.info("사용 가능한 COM 포트를 찾을 수 없습니다.")
            raise Exception("사용 가능한 COM 포트를 찾을 수 없습니다.")
        return com_ports






