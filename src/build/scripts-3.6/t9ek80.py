# ----------------------------------------------------------------------------
#    Method EK80 generic v1.0 Description Subscribes to EK80 data depending on the config.xml file and report 
#    data.
#                 Comunicate with the EK80/EK60/EK15 By: Kongsberg Maritime AS, Terje Nilsen 2020 
#-----------------------------------------------------------------------------
import socket import time import datetime import binascii import threading import sys import requests import 
xmltodict import xml.etree.ElementTree as ET from struct import * from collections import namedtuple from pprint 
import pprint DEBUG = False # Ads extra print statments... BIOMASS = False TARGET = True
#----------------------------------------------------------------------------
#   Method report Description User defined REPORT function, this is to be adapter to individual needs.
#                It receives a list for parameters and meta data to process... 
#-----------------------------------------------------------------------------
# For motion simulation only, to be removed...
lat = 10.492231 lon = 59.375803 xpos = 0 ypos = 0 xval = 1 yval = 1 biomaslist = [] url = 
"https://n00262-proteus-backend.azurewebsites.net/api/GeoJson/Feature/ekdata/" skip= 0
# Do the reporting stuff...
def report(Payload,Decode, timenow):
    global USEKOGNIFAI
    global DESIMATE
    global desimated
    global lat
    global lon
    global xpos, ypos, xval, yval
    global biomaslist
    global skip
    global mType
    
    #----------------------------------------------------------------------------
    # If biomass mode...
    if mType == "Biomass":
   
        # Skip some frames asthe data comes too fast...
        skip=skip+1
        if skip >= 1:
            skip = 0
    
            # Do we send it up to the cloud...
            if USEKOGNIFAI == True:
        
                # Simulate motion...
                xpos = xpos + (0.0001 * xval)
                if xpos > 0.01:
                    xval = -1
                    ypost = ypos + (0.0001 * yval)
                if xpos < 0.00001:
                    xval = 1
                    ypost = ypos + (0.0001 * yval)
                    
                # Store temp data....
                biomaslist.append([lat+xpos, lon+ypos, Payload[1],timenow])
                
                # Should we send data now, or just store until later...
                if DESIMATE == 0 or desimated >= DESIMATE:
                    desimated = 0
                    # Single fram JSON file...
                    json1 = "{" \
                           " \"type\": \"FeatureCollection\", " \
                           "\"features\": [" \
                           "{" \
                           "\"type\": \"Feature\"," \
                           "\"properties\": {" \
                           "\"biomass\" : aaaaa," \
                           "\"time\": \"bbbbb\"}," \
                           "\"geometry\": {" \
                           "\"type\": \"Point\"," \
                           "\"coordinates\": [ " \
                           " ccccc," \
                           " ddddd" \
                           "]}}]}"
                    json1 = json1.replace("aaaaa", "{:f}".format(Payload[1]))
                    json1 = json1.replace("bbbbb", "{:s}".format(timenow))
                    json1 = json1.replace("ccccc", "{:f}".format(lat+xpos))
                    json1 = json1.replace("ddddd", "{:f}".format(lon+ypos))
                    
                    # # Multi fram JSON file...
                    # json1 = "{" \
                           # " \"type\": \"FeatureCollection\", " \ "\"features\": [" \ "{" \ "\"type\": 
                           # \"Feature\"," \ "\"properties\": {" \ "\"time\": [timex]}," \ "\"biomass\" : 
                           # [biox]," \ "\"geometry\": {" \ "\"type\": \"LineString\"," \ "\"coordinates\": [ " 
                           # \ "latlonx" \ "]}}]}"
                    
                    # biox="" latlonx="" timex = "" for lat1, lon1, biomass1, time1 in biomaslist:
                        # biox+="{:f},".format(biomass1) latlonx+="[{:f},{:f},{:f}],".format(lat1, lon1, 
                        # biomass1) timex+="\"{:s}\",".format(time1)
                        
                    # biox = biox[:-1] latlonx = latlonx[:-1] timex = timex[:-1] json1 = json1.replace("biox", 
                    # biox) json1 = json1.replace("latlonx", latlonx) json1 = json1.replace("timex", timex)
                    print(json1)
                    response = requests.post(url, data=json1,headers={"Content-Type": "application/json"})
        #            sid=response.json()['login']['sessionId'] # to extract the detail from response 
        #            print(response.text) print(sid)
                    print ("******************")
                    print("SeqNo: {:d} Response: {:d}".format(Decode[1],response.status_code))
                    print ("******************")
                    print ("headers:"+ str(response.headers))
                    print ("******************")
                    
                    # Flush...
                    biomaslist = []
                    
                desimated = desimated+1
    #----------------------------------------------------------------------------
    # If single target chirp mode...
    if mType == "SingleTargetChirp":
        print("------------------------------")
        print("SingleTargetChirp");
        for element in Payload:
            print("Time: {:s} Depth: {:f} Forward: {:f} Side: {:f} Sa: {:f}"\
                .format(timenow,element[0],element[3],element[4],element[5]))
        
    #----------------------------------------------------------------------------
    # If single target mode...
    if mType == "SingleTarget":
        print("------------------------------")
        print("SingleTarget");
        for element in Payload:
            print("Time: {:s} Depth: {:f} Forward: {:f} Side: {:f} Sa: {:f}"\
                .format(timenow,element[0],element[3],element[4],element[5]))
            
    #----------------------------------------------------------------------------
    # If TargetStrength mode...
    if mType == "TargetStrength":
        print("------------------------------")
        print("TargetStrength");
        
    #----------------------------------------------------------------------------
    # If NoiseSpectrum mode...
    if mType == "NoiseSpectrum":
        print("------------------------------")
        print("NoiseSpectrum");
    #----------------------------------------------------------------------------
    # If Echogram mode...
    if mType == "Echogram":
        print("------------------------------")
        print("Echogram");
    #----------------------------------------------------------------------------
    # If BottomDetection mode...
    if mType == "BottomDetection":
        print("------------------------------")
        print("BottomDetection");
#------------------------------------------------------------------------------- 
#------------------------------------------------------------------------------- 
#------------------------------------------------------------------------------- 
#-------------------------------------------------------------------------------
# BELOW THIS LINE SHOULD NORMALLY NOOT NEED CHANGES:::::: 
#------------------------------------------------------------------------------- 
#------------------------------------------------------------------------------- 
#------------------------------------------------------------------------------- 
#-------------------------------------------------------------------------------
# Data that will be read from the xml file... PS: These walues will be overwritten...
UDP_IP = "127.0.0.1" UDP_PORT = 37655 UDP_DATA = 0 KDI_TCP_IP = "127.0.0.1" KDI_TCP_PORT = 55035 USEKOGNIFAI = 0 
#True
DESIMATE = 0
# globale variable
client_seq_no = 1 running = 0 mtypeName = "" itypeVal = "" itypeSize = 0 EK_req = "" desimated = 0 finale_data = 
b"" mType = ""
# ----------------------------------------------------------------------------
#    Method Convert a byte string to int(16) Description 
#-----------------------------------------------------------------------------
def bytes_to_int(bytes):
    result = int(bytes[0])
    result = result + int(bytes[1]*256)
    return result
# ----------------------------------------------------------------------------
#    Method Prepare subscription... Description Adds the JSON subscription to the EK80 subscriptor.
#                 Can create og change a subscription... 
#-----------------------------------------------------------------------------
def subscribe( sock, ApplicationID, transponder, create):
    global EK_req
    EK_req = EK_req.replace("?", transponder)
    print(EK_req)
        
    if create == True:
        CreateSubscription(sock, ApplicationID, UDP_DATA,EK_req);
    else:
        ChangeSubscription(sock, ApplicationID, UDP_DATA,EK_req);
# ----------------------------------------------------------------------------
#    Method GetParameterValue Description Get a set of parameters... 
#-----------------------------------------------------------------------------
def GetParameterValue( sock, ApplicationID, parameter_name ):
    global client_seq_no
    tmp = "REQ\0{:d},1,1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0".format(client_seq_no)
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
        "</request>\0".format(ApplicationID,client_seq_no,parameter_name)
    request = tmp + tmp2
    
    # Send the request and increase the sequence number
    request = bytes(request,encoding='utf-8')
    sock.send(request);
    client_seq_no=client_seq_no + 1;
# ----------------------------------------------------------------------------
#    Method SetParameter Description Set a set of parameterrs... 
#-----------------------------------------------------------------------------
def SetParameter( socet, ApplicationID, parameter_name, parameter_value, parameter_type ):
    global client_seq_no
    tmp = "REQ\0{:d},1,1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0".format(client_seq_no)
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
        "</request>\0".format(ApplicationID,client_seq_no,parameter_name,parameter_value,parameter_type)
    request = tmp + tmp2
    # Send the request and increase the sequence number
    request = bytes(request,encoding='utf-8')
    sock.send(request);
    client_seq_no=client_seq_no + 1;
#----------------------------------------------------------------------------
#    Method CreateSubscription Description Creates a subscritopn to EK80... 
#-----------------------------------------------------------------------------
def CreateSubscription(sock, ApplicationID, port, parameter_name):
    global client_seq_no
    tmp = "REQ\0{:d},1,1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0".format(client_seq_no)
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
        "</request>\0".format(ApplicationID,client_seq_no,port,parameter_name)
    request = tmp + tmp2
    
    # Send the request and increase the sequence number
    request = bytes(request,encoding='utf-8')
    sock.send(request);
    client_seq_no=client_seq_no + 1;
#----------------------------------------------------------------------------
#    Method ChangeSubscription Description Changes an existing subscription to EK80... 
#-----------------------------------------------------------------------------
def ChangeSubscription(sock, ApplicationID, port, parameter_name):
    global client_seq_no
    tmp = "REQ\0{:d},1,1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0".format(client_seq_no)
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
        "</request>\0".format(ApplicationID,client_seq_no,ApplicationID,parameter_name)
    request = tmp + tmp2
    # Send the request and increase the sequence number
    request = bytes(request,encoding='utf-8')
    sock.send(request);
    client_seq_no=client_seq_no + 1;
#----------------------------------------------------------------------------
#    Method EK80_comunicate Description Initiate a communication and data channel to the EK80... 
#-----------------------------------------------------------------------------
def EK80_comunicate(port, data):
    global running
    global client_seq_no
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((UDP_IP, port))
    sock.settimeout(5.0)
    while running <= 3:
        if len(data) >= 3:
            if data[:3] == b'SI2':
                msg = bytearray(b'CON\0Name:Simrad;Password:\0')
                sock.send(msg) # Send connect...
                
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
                        print("Get Param");
                        GetParameterValue(sock,ApplicationID, "TransceiverMgr/Channels" )
                        
                    else: # If failed the retry...
                        print('Connection failed!')
                        msg = bytearray(b'CON\0Name:Simrad;Password:\0')
                        sock.send(msg) # Send connect...
                elif data[4:7] == b'REQ':
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
                        print('\n\rTransponder to use:')
                        i = 0
                        for e in element:
                            print('{:d}: '.format(i) + e)
                            i = i+1
                            
                        mode = -1
                        while mode < 0 or mode > len(element):
                            try:
                                mode=int(input('Select Transponder: '))
                            except ValueError:
                                print ("Not a number")
                        
                        transponder = element[mode]
                        subscribe(sock, ApplicationID,transponder, True)
                        
                    else:
                        print("Received Status...")
                        running = 2
                    
                else:
                    print('Unknown response...')
                            
            elif data[:3] == b'ALI':
                msg = 'ALI\0ClientID:{:d},SeqNo:{:d}\0'.format(ApplicationID,client_seq_no)
                msg = bytes(msg,encoding='utf-8')
                sock.send(msg) # Send connect...
#                print('.')
            elif data[:3] == b'RTR':
                print('RTR received...')
                print(data);
            elif data[:3] == b'REQ':
                print('REQ received...')
                
            elif data[:3] == b'PRD':
                print('PRD received...')
                print(data);
                
            else:
                print("Wrong data...")
        else:
            print("EK80 error...")
            
        data = sock.recv(1024)
            
    running = 5
    msg = bytearray(b'DIS\0Name:Simrad;Password:\0')
    sock.send(msg) # Send connect...
    sock.settimeout(None)
    sock.close()
#----------------------------------------------------------------------------
#    Method EK80_data Description The subscription data handler...
#                 Data is parsed according to the XML file... 
#-----------------------------------------------------------------------------
 
def EK80_data(a,b):
    global running
    global UDP_DATA
    global itypeVal
    global finale_data
    
    time = 0
    
    # Open the default channel...
    print("Setting up data channel...")
    datasock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    datasock.bind(("0.0.0.0", UDP_DATA))
    UDP_DATA = datasock.getsockname()[1]
    datasock.settimeout(120.0)
    print('listening on port:', UDP_DATA)
    running = 1
    
    while running <= 2:
        data = datasock.recv(2048)
        Decode = unpack('<4siiHHH',data[0:18])
        
        if DEBUG == True:
            print("\n\rHeader: ".format(Decode[0].decode('utf-8')))
            print(Decode[0])
            print("SeqNo: {:d}".format(Decode[1]))
            print("SubID: {:d}".format(Decode[2]))
            print("CurrentMsg: {:d}".format(Decode[3]))
            print("TotalMsg: {:d}".format(Decode[4]))
            print("NoOfBytes: {:d}".format(Decode[5]))
        finale_data = finale_data+data[18:]
        if Decode[4] == Decode[3]:
            
            if itypeSize > 0:
                tmp = unpack("<Q"+mtypeName,finale_data[0:10])
                timenow = datetime.datetime.utcfromtimestamp((tmp[0]/10000000)- 
11644473600).strftime('%Y-%m-%dT%H:%M:%SZ')
                
                Payload = []
                if tmp[1] > 0:
                    for loop in range(0,tmp[1]):
                        Payload.append(unpack("<"+itypeVal,finale_data[10+(loop*itypeSize):10+(loop*itypeSize)+itypeSize]))
                        
                if DEBUG == 2:
                    for element in Payload:
                        for elements in element:
                            print("Value: {:f}".format(elements))
                    
            else:
                Payload = unpack("<Q"+mtypeName,finale_data[0:Decode[5]])
                timenow = datetime.datetime.utcfromtimestamp((Payload[0]/10000000)- 
11644473600).strftime('%Y-%m-%dT%H:%M:%SZ')
                
                if DEBUG == True:
                    for element in Payload:
                        print("Value: {:f}".format(element))
            
            report(Payload,Decode, timenow)
            finale_data = b""
      
    running = 4
    datasock.settimeout(None)
    datasock.close()
#----------------------------------------------------------------------------
#   Method man function, entry point Description Parse the XML and get started... 
#-----------------------------------------------------------------------------
config = "config.xml"
# count the arguments
arguments = len(sys.argv) if arguments == 2:
    config = sys.argv[1]
# Open the default channel...
tree = ET.parse(config) root = tree.getroot() for table in root.iter('Configuration'):
    for child in table:
        if child.tag == 'EK80':
            for child2 in child:
                if child2.tag == 'EK80_IP':
                    UDP_IP = child2.text
                if child2.tag == 'EK80_PORT':
                    UDP_PORT = int(child2.text)
                if child2.tag == 'EK80_DATA':
                    UDP_DATA = int(child2.text)
                if child2.tag == 'DESIMATE':
                    DESIMATE = int(child2.text)
                    
        if child.tag == 'Cloud':
            for child2 in child:
                if child2.tag == 'KDI_TCP_IP':
                    KDI_TCP_IP = child2.text
                if child2.tag == 'KDI_TCP_PORT':
                    KDI_TCP_PORT = int(child2.text)
                if child2.tag == 'USEKOGNIFAI':
                    USEKOGNIFAI = int(child2.text)
                    
        if child.tag == 'Request':
            for child2 in child:
                if child2.tag == 'req':
                    EK_req = child2.text
                if child2.tag == 'res':
                    mtypeName = child2.text
                if child2.tag == 'resi':
                    itypeVal = child2.text
                if child2.tag == 'ress':
                    itypeSize = int(child2.text)
                if child2.tag == 'type':
                    mType = child2.text
   
#----------------------------------------------------------------------------
# Request an port number from the EK80 to use for future comunictions.
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) sock.connect((UDP_IP, UDP_PORT)) sock.settimeout(5.0) 
sock.send('RSI\0'.encode()) # Send reset... data = sock.recv(1024)
# Print status so far....
print('Unit: ', data[4:8]) print('ID: ',data[272:283]) port = bytes_to_int(data[264:266]) print('Port: 
',hex(port))
# Close and reopen a new channel...
sock.settimeout(None) sock.close()
#----------------------------------------------------------------------------
# Start comunication...
if len(data) > 3:
    print("Start Data thread...")
    thread2= threading.Thread(target = EK80_data, args = (0,0))
    thread2.start()
    
    print("Awaiting Data handler ready...")
    while running == 0:
        time.sleep(1)
        if thread2.isAlive() == 0:
            break
    print("Start Command thread...")
    thread1 = threading.Thread(target = EK80_comunicate, args = (port, data))
    thread1.start()
   
    while running != 2:
        time.sleep(1)
        if thread1.isAlive() == 0:
            break
    # Do data handle until enter i pressed...
    if running == 2:
        input('Enter to exit...')
    # Exit grasefully...
    print('Stopping')
    running = 3;
    while running != 5:
        time.sleep(1)
        print(running)
        
print('Stoped')
