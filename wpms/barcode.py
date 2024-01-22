import threading
from threading import Event
import serial
import serial.tools.list_ports
import traceback
import time
from conf.logconfig import logger


event = Event()

class Barcode(threading.Thread):

    isRun = False
    serial = ''
    socketClient = None
    client_list = []
    serialTarget = None
    tryCount= 0
    reconSec = 5  # 재연결시도 시간
    maininstance = None



    def __init__(self, serial,reconSec, maininstance):
        super().__init__()
        self.serial = serial
        self.reconSec = reconSec
        self.maininstance = maininstance


    def run(self):
        self.isRun = True
        self.runBarcode()
          # print("Server thread start ", threading.current_thread())

    def runBarcode(self):
        try:
            self.serialTarget = serial.Serial(self.serial, 115200, timeout=1)  # COM 9에 115200으로 serial port open
            if self.serialTarget.isOpen():
                self.tryCount = 0
                self.maininstance.isConBardoe = True
                self.isRun = True
                logger.info('Barcode Connected :: '+ self.serial)

            while self.isRun:
                rx = self.serialTarget.readline().decode('ascii')  # 아스키 타입으로 읽음
                if(rx != ''):
                    #print("Receive Data: ", rx)
                    self.maininstance.reciveBarcodeData(rx)
        except:
            logger.info('Barcode DisConnected')
            self.maininstance.isConBardoe = False
            self.isRun = False
            self.tryCount = self.tryCount+1
            logger.info('barcode connect try count :: ' + str(self.tryCount))
            time.sleep(self.reconSec)
            #traceback.print_exc()
            self.runBarcode() # 시리얼에 붙을때 까지 재시도












