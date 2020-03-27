# ----------------------------------------------------------------------------
#    Method       EK80 generic v1.0
#    Description  Subscribes to EK80 data depending on the config.xml file and report data.
#                 Comunicate with the EK80/EK60/EK15
#    By:          Kongsberg Maritime AS, Terje Nilsen 2020
#-----------------------------------------------------------------------------
import socket
import time
import datetime
import binascii
import threading
import sys
import requests

import xmltodict
import xml.etree.ElementTree as ET
from struct import *
from collections import namedtuple
from pprint import pprint

# PS: Enabling debug output might in som cases delay the handling and cause errors.
# If you start to get lost messages, disable debug and retest.
# If this helps, then remove some output messages in the EK80_data function.
# The EK80_data function is time critical...
DEBUG   = False   # Adds extra print statments...

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# BELOW THIS LINE SHOULD NORMALLY NOOT NEED CHANGES::::::
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class t9ek80:
#----------------------------------------------------------------------------
#   Method       report
#   Description  User defined REPORT function, this is to be adapter to individual needs.
#                It receives a list for parameters and meta data to process...
#-----------------------------------------------------------------------------
# For motion simulation only, to be removed...
    def __init__(self, argv):

        self.error = 0  # Class Error handler...
        
        # Data that will be read from the xml file...
        # PS: These walues will be overwritten...
        self.UDP_IP = "127.0.0.1"
        self.UDP_PORT = 37655
        self.UDP_DATA = 0
        self.desimate = 0
      
        self.NMEA_DATA = 0  # Will be set by the XML handler...
       
        # KDI_TCP_IP = "127.0.0.1"
        # KDI_TCP_PORT = 55035
        # USEKOGNIFAI =  0 #True

        self.Status_Command = 1  
        self.Status_Data = 2
        self.Status_NMEA = 4
        self.Status_Done = 8
        self.Status_Running = 16

        # globale variable
        self.client_seq_no = 1
        self.mtypeName = ""
        self.itypeVal = ""
        self.itypeSize = 0
        self.EK_req = ""
        self.EK_Value = 0
        self.EK_Type = ""
        self.desimated = 0
        self.finale_data = b""
        self.mtype = ""
        self.running = 0 # 0x1FF when all prosesses running...
        self.totalbytes = 0
        
        self.config = "config.xml"
        self.busy = 0
        self.mode = -1
        self.cont = False

        # Get extra parameters...
        if len(argv) == 3:
            self.mode = int(argv[2])
            self.cont = True
       
        # count the arguments
        if len(argv) < 2:
            print("Usage: python3 tescast.py config.xml [transponder]")
            self.error = -1
        else:
            print("Initializes config file: "+argv[1])
            arguments = len(argv)
            if arguments >= 2:
                config = argv[1]

            # Open the default channel...
            tree = ET.parse(config)
            root = tree.getroot()
             
            for table in root.iter('Configuration'):
                for child in table:
                    if child.tag == 'EK80':
                        for child2 in child:
                            if child2.tag == 'EK80_IP':
                                self.UDP_IP = child2.text
                            if child2.tag == 'EK80_PORT':
                                self.UDP_PORT = int(child2.text)
                            if child2.tag == 'EK80_DATA':
                                self.UDP_DATA = int(child2.text)
                            if child2.tag == 'NMEA_DATA':
                                self.NMEA_DATA = int(child2.text)
                            if child2.tag == 'DESIMATE':
                                self.desimate = int(child2.text)
                                
                    # if child.tag == 'Cloud':
                        # for child2 in child:
                            # if child2.tag == 'KDI_TCP_IP':
                                # self.KDI_TCP_IP = child2.text
                            # if child2.tag == 'KDI_TCP_PORT':
                                # self.KDI_TCP_PORT = int(child2.text)
                            # if child2.tag == 'USEKOGNIFAI':
                                # self.USEKOGNIFAI = int(child2.text)
                                
                    if child.tag == 'Request':
                        for child2 in child:
                            if child2.tag == 'req':
                                self.EK_req = child2.text
                            if child2.tag == 'req2':
                                self.EK_Value = child2.text
                            if child2.tag == 'req3':
                                self.EK_Type = child2.text
                            if child2.tag == 'res':
                                self.mtypeName = child2.text
                            if child2.tag == 'resi':
                                self.itypeVal = child2.text
                            if child2.tag == 'ress':
                                self.itypeSize = int(child2.text)
                            if child2.tag == 'type':
                                self.mtype = child2.text
           
    #----------------------------------------------------------------------------

    # Do the reporting stuff...
    def report(Payload,Decode, timenow, mtype, desimate):
        if DEBUG == True:
            print("Missing interface module...")


    def NMEAdecode(self,data):
        if DEBUG == True:
            print("Missing NMEA interface module...")

    # ----------------------------------------------------------------------------
    #    Method       Convert a byte string to int(16) 
    #    Description  
    #-----------------------------------------------------------------------------
    def bytes_to_int(self,bytes):
        result = int(bytes[0])
        result = result + int(bytes[1]*256)
        return result

    # ----------------------------------------------------------------------------
    #    Method       Prepare subscription...
    #    Description  Adds the JSON subscription to the EK80 subscriptor.
    #                 Can create og change a subscription...
    #-----------------------------------------------------------------------------
    def subscribe(self, sock, ApplicationID, transponder, create):
        self.EK_req = self.EK_req.replace("?", transponder)
        if DEBUG == True:
            print(self.EK_req)
            
        if create == True:
            self.CreateSubscription(sock, ApplicationID, self.UDP_DATA,self.EK_req);
        else:
            self.ChangeSubscription(sock, ApplicationID, self.UDP_DATA,self.EK_req);

    # ----------------------------------------------------------------------------
    #    Method       GetParameterValue
    #    Description  Get a set of parameters...
    #-----------------------------------------------------------------------------
    def GetParameterValue(self, sock, ApplicationID, transponder, parameter_name ):
        parameter_name = parameter_name.replace("?", transponder)
        
        tmp = "REQ\0{:d},1,1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0".format(self.client_seq_no)
        tmp = tmp[0:26]
        tmp2 = "<request>" \
            "<clientInfo>" \
            "<cid>{:d}</cid>" \
            "<rid>{:d}</rid>" \
            "</clientInfo>" \
            "<type>invokeMethod</type>" \
            "<targetComponent>ParameterServer</targetComponent>" \
            "<method>" \
            "<GetParameter>" \
            "<paramName>{:s}</paramName>" \
            "<time>0</time>" \
            "</GetParameter>" \
            "</method>" \
            "</request>\0".format(ApplicationID,self.client_seq_no,parameter_name)
        request = tmp + tmp2
        
        # Send the request and increase the sequence number
        request = bytes(request,encoding='utf-8')
        sock.send(request);
        self.client_seq_no=self.client_seq_no + 1;

    # ----------------------------------------------------------------------------
    #    Method       SetParameter
    #    Description  Set a set of parameterrs...
    #-----------------------------------------------------------------------------
    def SetParameter(self, sock, ApplicationID, transponder, parameter_name, parameter_value, parameter_type ):
        parameter_name = parameter_name.replace("?", transponder)
        
        tmp = "REQ\0{:d},1,1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0".format(self.client_seq_no)
        tmp = tmp[0:26]
        tmp2 = "<request>" \
            "<clientInfo>" \
            "<cid>{:d}</cid>" \
            "<rid>{:d}</rid>" \
            "</clientInfo>" \
            "<type>invokeMethod</type>" \
            "<targetComponent>ParameterServer</targetComponent>" \
            "<method>" \
            "<SetParameter>" \
            "<paramName>{:s}</paramName>" \
            "<paramValue>{:s}</paramValue>" \
            "<paramType>{:s}</paramType>" \
            "<time>0</time>" \
            "</SetParameter>" \
            "</method>" \
            "</request>\0".format(ApplicationID,self.client_seq_no,parameter_name,parameter_value,parameter_type)
        request = tmp + tmp2

        # Send the request and increase the sequence number
        request = bytes(request,encoding='utf-8')
        sock.send(request);
        self.client_seq_no=self.client_seq_no + 1;

    #----------------------------------------------------------------------------
    #    Method       CreateSubscription
    #    Description  Creates a subscritopn to EK80...
    #-----------------------------------------------------------------------------
    def CreateSubscription(self, sock, ApplicationID, port, parameter_name):
        tmp = "REQ\0{:d},1,1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0".format(self.client_seq_no)
        tmp = tmp[0:26]
        tmp2 = "<request>" \
            "<clientInfo>" \
            "<cid>{:d}</cid>" \
            "<rid>{:d}</rid>" \
            "</clientInfo>" \
            "<type>invokeMethod</type>" \
            "<targetComponent>RemoteDataServer</targetComponent>" \
            "<method>" \
            "<Subscribe>" \
            "<requestedPort>{:d}</requestedPort>" \
            "<dataRequest>{:s}</dataRequest>" \
            "</Subscribe>" \
            "</method>" \
            "</request>\0".format(ApplicationID,self.client_seq_no,port,parameter_name)
        request = tmp + tmp2
        
        # Send the request and increase the sequence number
        request = bytes(request,encoding='utf-8')
        sock.send(request);
        self.client_seq_no=self.client_seq_no + 1;

    #----------------------------------------------------------------------------
    #    Method       ChangeSubscription
    #   Description   Changes an existing subscription to EK80...
    #-----------------------------------------------------------------------------
    def ChangeSubscription(self, sock, ApplicationID, port, parameter_name):
        tmp = "REQ\0{:d},1,1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0".format(self.client_seq_no)
        tmp = tmp[0:26]
        tmp2 = "<request>" \
            "<clientInfo>" \
            "<cid>{:d}</cid>" \
            "<rid>{:d}</rid>" \
            "</clientInfo>" \
            "<type>invokeMethod</type>" \
            "<targetComponent>RemoteDataServer</targetComponent>" \
            "<method>" \
            "<ChangeSubscription>>" \
            "<subscriptionID>{:d}</subscriptionID>" \
            "<dataRequest>{:s}</dataRequest>" \
            "</ChangeSubscription>>" \
            "</method>" \
            "</request>\0".format(ApplicationID,self.client_seq_no,ApplicationID,parameter_name)
        request = tmp + tmp2

        # Send the request and increase the sequence number
        request = bytes(request,encoding='utf-8')
        sock.send(request);
        self.client_seq_no=self.client_seq_no + 1;

    #----------------------------------------------------------------------------
    #    Method       EK80_comunicate
    #   Description   Initiate a communication and data channel to the EK80...
    #-----------------------------------------------------------------------------
    def EK80_comunicate(self, port, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((self.UDP_IP, port))
        sock.settimeout(5.0)
        self.running = self.running |self. Status_Command

        while self.running & self.Status_Running:

            if len(data) >= 3:
                if data[:3] == b'SI2':
                    msg = bytearray(b'CON\0Name:Simrad;Password:\0')
                    sock.send(msg)  # Send connect...
                    
                elif data[:3] == b'RES':
                    if data[4:7] == b'CON':
                        if data[30:45] == b'ResultCode:S_OK':
                            print('Connected...')
                            data2 = data[46:].replace(b'AccessLevel:',b' ')
                            data2 = data2.replace(b'ClientID:',b' ')
                            data2 = data2.replace(b'}',b' ')
                            data2 = data2.replace(b',',b' ')
                            data3 = data2.split()
                            ApplicationID = int(data3[1].decode())
                            if DEBUG == True:
                                print("Get Param");
                            self.GetParameterValue(sock,ApplicationID, "", "TransceiverMgr/Channels" )
                            
                        else: # If failed the retry...
                            print('Connection failed!')
                            msg = bytearray(b'CON\0Name:Simrad;Password:\0')
                            sock.send(msg)  # Send connect...

                    elif data[4:7] == b'REQ':
                        if DEBUG == True:
                            print('RES REQ received...')
                        msg = data[30:].decode("utf-8").rstrip("\0")
                        root = ET.fromstring(msg)
                        
                        element=""
                        for table in root.iter('GetParameterResponse'):
                            for child in table:
                                for child2 in child:
                                    if child2.tag == 'value':
                                        element = child2.text.split(',')

                        if len(element) > 0:
                            if self.mode == -1:         # If we already got a mode from command line parameter...
                                print('\n\rTransponder to use:')
                                i = 0
                                for e in element:
                                    print('{:d}: '.format(i) + e)
                                    i = i+1
                            
                                # If there are only one head, then select it, no question...
                                if len(element) == 1:   # If there is only one option...
                                    self.mode = 0
                                else:                   # Else let the user select...
                                    self.mode = -1
                                    while self.mode < 0 or self.mode > len(element):
                                        try:
                                            self.mode=int(input('Select Transponder: '))
                                        except ValueError:
                                            print ("Not a number")
                            else:
                                print('{:d}: '.format(self.mode) + element[self.mode])

                            transponder = element[self.mode]
                            print(self.mtype)
                            
                            if self.mtype == "Set_Param":
                                self.SetParameter(sock, ApplicationID, transponder, self.EK_req, self.EK_Value, self.EK_Type )
                                self.running =  self.running | self.Status_Done
                                break
                            else:
                                self.subscribe(sock, ApplicationID,transponder, True)
                            
                        else:
                            if DEBUG == True:
                                print("Received Status...")
                            self.running =  self.running | self.Status_Command
                        
                    else:
                        print('Unknown response...')
                                
                elif data[:3] == b'ALI':
                    msg = 'ALI\0ClientID:{:d},SeqNo:{:d}\0'.format(ApplicationID,self.client_seq_no)    
                    msg = bytes(msg,encoding='utf-8')
                    sock.send(msg)  # Send connect...
                    if DEBUG == True:
                        print('.')

                elif data[:3] == b'RTR':
                    if DEBUG == True:
                        print('RTR received...')
                        print(data);

                elif data[:3] == b'REQ':
                    if DEBUG == True:
                        print('REQ received...')
                    
                elif data[:3] == b'PRD':
                    if DEBUG == True:
                        print('PRD received...')
                        print(data);
                    
                else:
                    if DEBUG == True:
                        print("Wrong data...")
            else:
                print("EK80 error...")

                
            try:
                data = sock.recv(20000)
            except socket.timeout:
                continue
              
        print("Closing command handler...")
        self.running = self.running & ~self.Status_Command
        msg = bytearray(b'DIS\0Name:Simrad;Password:\0')
        sock.send(msg)  # Send connect...

        sock.settimeout(None)
        sock.close()

    #----------------------------------------------------------------------------
    #    Method       EK80_data
    #   Description   The subscription data handler...
    #                 Data is parsed according to the XML file...
    #-----------------------------------------------------------------------------
     
    def EK80_data(self,a,b):
        time = 0
        
        # Open the default channel...
        if DEBUG == True:
            print("Setting up data channel...")
            
        datasock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        datasock.bind(("0.0.0.0", self.UDP_DATA))
        self.UDP_DATA = datasock.getsockname()[1]
        datasock.settimeout(5.0)
        print('EK80data  listening on port:', self.UDP_DATA)
        self.running = self.running | self.Status_Data
        
        # Data can in some case be received in frame sets, we then need to make shure that we start with the first frame in the set.
        # Some time we are a bit slow hens the Busy structure...
        while self.running & self.Status_Running:
            try:
                data = datasock.recv(50000)
            except socket.timeout:
                continue
                
            Decode = unpack('<4siiHHH',data[0:18])
            
            if self.busy == 0 and Decode[4] == Decode[3]:
                self.busy = 2 # Ready from next...
            else:    
                self.finale_data = self.finale_data+data[18:]
                self.totalbytes = self.totalbytes + Decode[5]

                if Decode[4] == Decode[3]:
                    self.busy = 1  #Busy...
                    
                    if DEBUG == True:
                        print("\n\rHeader:     ".format(Decode[0].decode('utf-8')))
                        print(Decode[0])
                        print("SeqNo:      {:d}".format(Decode[1]))
                        print("SubID:      {:d}".format(Decode[2]))
                        print("CurrentMsg: {:d}".format(Decode[3]))
                        print("TotalMsg:   {:d}".format(Decode[4]))
                        print("NoOfBytes:  {:d}".format(Decode[5]))
                
                    if self.itypeSize > 0:
                        tmp = unpack("<Q"+self.mtypeName,self.finale_data[0:10])
                        timenow = datetime.datetime.utcfromtimestamp((tmp[0]/10000000)- 11644473600).strftime('%Y-%m-%dT%H:%M:%SZ')
                        self.finale_data = self.finale_data[10:]
                        Payload = []
                        if tmp[1] > 0:
                            for loop in range(0,tmp[1]):
                                start = loop*self.itypeSize
                                end = (loop*self.itypeSize)+self.itypeSize
                                dta = self.finale_data[start:end]
                                Payload.append(unpack("<"+self.itypeVal,self.finale_data[start:end]))
                                
                        if DEBUG == 2:
                            for element in Payload:
                                for elements in element:
                                    print("Value:     {:f}".format(elements))
                            
                    else:
                        Payload = unpack("<Q"+self.mtypeName,self.finale_data[0:self.totalbytes])
                        timenow = datetime.datetime.utcfromtimestamp((Payload[0]/10000000)- 11644473600).strftime('%Y-%m-%dT%H:%M:%SZ')
                        
                        # if DEBUG == True:
                            # for element in Payload:
                                # print("Value:     {:f}".format(element))
                    
                    self.report(Payload,Decode, timenow, self.mtype, self.desimate)

                    self.finale_data = b""
                    self.totalbytes = 0
                    self.busy = 0  # Ready to find next header...
          
        print("Closing data subscriber...")
        self.running = self.running & ~self.Status_Data
        datasock.settimeout(None)
        datasock.close()

    #----------------------------------------------------------------------------
    #   Method       man function, entry point
    #   Description  Parse the XML and get started...
    #-----------------------------------------------------------------------------
    def NMEA_data(self,a,b):
        time = 0
        
        # Open the default channel...
        if DEBUG == True:
            print("Setting up NMEA")
            
        if int(self.NMEA_DATA) > 0:
            datasock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            datasock.bind(("0.0.0.0", int(self.NMEA_DATA)))
            self.NMEA_DATA = datasock.getsockname()[1]
            datasock.settimeout(5.0)
            print('NMEA listening on port:', self.NMEA_DATA)
            data = b""
            self.running = self.running | Status_NMEA

            while self.running & self.Status_Running:
                try:
                    data = datasock.recv(20000)
                except socket.timeout:
                    continue
                    
                self.NMEAdecode(data)

            print("NMEA Closed...")
            datasock.settimeout(None)
            datasock.close()
            
        else:
            print("NMEA Not used...")
        
        self.running = self.running & ~self.Status_NMEA
        
    #----------------------------------------------------------------------------
    #   Method       man function, entry point
    #   Description  Parse the XML and get started...
    #-----------------------------------------------------------------------------
    def main(self):
        # Request an port number from the EK80 to use for future comunictions. 
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((self.UDP_IP, self.UDP_PORT))
        sock.settimeout(5.0)
        sock.send('RSI\0'.encode())  # Send reset...
        try:
            data = sock.recv(8000)
        except socket.timeout:
            print ("No Equipment found, make shure the IP:port is set to: {:s}:{:d}".format(self.UDP_IP,self.UDP_PORT))
            sock.close()
            return

        # Print status so far....
        print('Unit: ', data[4:8])
        print('ID:   ',data[272:283])
        port = self.bytes_to_int(data[264:266])

        # Close and reopen a new channel...
        sock.settimeout(None)
        sock.close()

        #----------------------------------------------------------------------------
        # Start comunication...
        if len(data) > 3:
        
            self.running = self.Status_Running # Start running...

            if DEBUG == True:
                print("Start NMEA thread...")
            thread3= threading.Thread(target = self.NMEA_data, args = (0,0))
            thread3.start()

            if DEBUG == True:
                print("Start Data thread...")
            thread2= threading.Thread(target = self.EK80_data, args = (0,0))
            thread2.start()
            
            if DEBUG == True:
                print("Awaiting Data handler ready...")
            while (self.running & self.Status_Data) == 0:
                time.sleep(1)
                if thread2.isAlive() == 0:
                    break

            # If the data thread is running (should always be...)
            if self.running & self.Status_Data:
                if DEBUG == True:
                    print("Start Command thread...")
                thread1 = threading.Thread(target = self.EK80_comunicate, args = (port, data))
                thread1.start()
               
                while (self.running & self.Status_Command) == 0 and (self.running & self.Status_Done) == 0:
                    time.sleep(1)
                    if thread1.isAlive() == 0:
                        break


            # Do data handle until enter i pressed...
            if self.running & self.Status_Command and self.cont == False:
                input('Enter to exit...')

            # Exit grasefully... 
            print('Stopping')
            time.sleep(4)
            self.running = self.running & ~self.Status_Running;
            while self.running & ~self.Status_Done:
                time.sleep(1)
           
        time.sleep(2)
        print('Stoped')

