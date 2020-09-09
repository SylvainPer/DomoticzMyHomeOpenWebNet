#!/usr/bin/env python3
# coding: utf-8 -*-
#
# Author: Deufo
#

"""
<plugin key="MyHome" name="MyHome plugin" author="Deufo" version="0.10" wikilink="https://" externallink="https://github.com/sylvainper">
    <description>
        <h2> Plugin MyHome for Domoticz with Legrand/Bticino USB dongle</h2><br/>
        <h3> Short description </h3>
           This plugin allow Domoticz to access to the MyHome (Zigbee based) worlds of devices.<br/>
           Only Lights are supported.<br/>
           USB zigbee key:<br/>
           <ul style="list-style-type:square">
            <li>Bticino 3578: https://catalogo.bticino.it/BTI-3578-IT</li>
            <li>legrand 088328</li>
            </ul>
    </description>
    <params>
        <param field="SerialPort" label="Serial Port" width="150px" required="true" default="/dev/ttyUSB0"/>
        <param field="Mode1" label="Time between refreshs in s" width="75px" required="true" default="300" />
    </params>
</plugin>
"""

import Domoticz
from datetime import datetime
import time


class BasePlugin:
    enabled = False

    def __init__(self):

        self.internalHB = 0
        self._HBRate = 1
        self._NbDevicesNetwork = 0
        self._scannedDevice = None
        
        # Communication/Transport link attributes
        self._connection = None  # connection handle
        self._ReqRcv = bytearray()  # on going receive buffer
        self._transp = None  # Transport mode USB or Wifi
        self._serialPort = None  # serial port in case of USB
        
        self._joinedNetwork = None #join network needed
        self._scanningNetwork = None
        self._scannedNetwork = None
        self._lastCmd = None
        self._lastTargetUnit = None
        
        
    def onStart(self):
        Domoticz.Status("onStart")
        self._joinedNetwork = False
        self._scanningNetwork = False
        self._scannedNetwork = False
    
        # loggingPlugin( self, 'Debug', "ListOfDevices : " )
        # for e in self.ListOfDevices.items(): 
            # loggingPlugin( self, 'Debug', " "+str(e))
        id = 255
        if id not in Devices:
            Domoticz.Device(Name = "Switch all off",  Unit = id, TypeName = "Push Off").Create()
            Domoticz.Status("Device Switch all created.")
            
        self._serialPort=Parameters["SerialPort"]
        
        
        if self._connection is not None:
            del self._connection
            self._connection = None


        if self._serialPort.find('/dev/') != -1 or self._serialPort.find('COM') != -1:
            Domoticz.Status("Connection...")
            BAUDS = 19200
            self._connection = Domoticz.Connection(Name="MyHome", Transport="Serial", Protocol="None",
                                                   Address=self._serialPort, Baud=BAUDS)
                                                   
        if self._connection:
            self._connection.Connect()
        else:
            Domoticz.Error("openConn _connection note set!")
            
            
    def onStop(self):
        Domoticz.Debug("onStop")
        
        
    
    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect")
        
        if self._connection.Connected():
            Domoticz.Status("Connected to Name: MyHome, Transport: Serial, Address: %s" % (self._serialPort))
            self._lastCmd = "join"
            self._connection.Send("*13*60##")

 
    
    def onCommand(self, Unit, Command, Level, Color):
        Domoticz.Debug("onCommand called: Unit=" + str(Unit) + ", Parameter=" + str(Command) + ", Level=" + str(Level))
       
        cmd = "*1*"
        if str(Command) == "On":
            cmd += "1*"
            nValue = 1
        else:
            cmd += "0*"
            nValue = 0
            
        if Unit == 255: #Switch All
            cmd += "0#"
        else:
            cmd += str(int(Devices[Unit].DeviceID,16))
        
        cmd += "01#9##"
        
        Domoticz.Debug("Send: " + cmd)
        self._lastCmd = str(Command)
        self._lastTargetUnit = Unit
        self._connection.Send(cmd)        
        
    
    def onHeartbeat(self):
        self.internalHB +=1
        if (self.internalHB % self._HBRate != 0):
            return
        
        Domoticz.Debug("onHeartbeat")
        
        if not self._connection.Connected():                
            Domoticz.Error("Not connected")
            self._connection.Connect()
            return
        
        if self._joinedNetwork == False :
            self._lastCmd = "join"
            self._connection.Send("*13*60*##")
            return
        
        if self._scannedNetwork == False: 
            return    
        
        now = time.time()
        for unit in Devices:
            LUpdate = Devices[unit].LastUpdate
            try:
                LUpdate = time.mktime(time.strptime(LUpdate, "%Y-%m-%d %H:%M:%S"))
            except:
                Domoticz.Error("Something wrong to decode Domoticz LastUpdate " %LUpdate)
                break
            if (now - LUpdate) > int(Parameters["Mode1"]):
                cmd = "*#1*" + str(int(Devices[unit].DeviceID,16)) + "01#9##"
                self._lastCmd = "UpdateStatus"
                self._lastTargetUnit = unit
                self._connection.Send(cmd) 
                return
                

    def onDeviceRemoved( self,Unit ):
        Domoticz.Debug("onDeviceRemoved")
        
    def onDisconnect(self,Connection):
        Domoticz.Debug("onDisconnect")
        
    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage")
        if Data is not None:
            Domoticz.Status("Rcv: " + repr(Data) )
            if chr(Data[0]) != '*' :
                Domoticz.Error("Received frame format is not correct.")
            else:
                decode_Data(self,Data)

def scanNetworkDevices(self):
    if self._scannedDevice != 0:
        self._scannedDevice -= 1
        cmd = "*#13**66*" + str(self._scannedDevice) + "##"
        self._lastCmd = "product_information " + str(self._scannedDevice)
        self._connection.Send(cmd)
    else: #Scan finished
        self._scannedNetwork = True
        self._scanningNetwork = False
        self._HBRate = 2 #HeartBeat each 20s
        Domoticz.Status("Scan finished")

def decode_Data(self,Data):
    if chr(Data[1]) == '#' :
        if chr(Data[2]) == '*': #Nack
            checkNack(self,Data)
        else :
            if chr(Data[2]) == '1' and chr(Data[3]) == '3' and chr(Data[4]) == '*': #Gateway
                statusGateway(self,Data)
    elif chr(Data[1]) == '1' and chr(Data[2]) == '*': #Ligths
        nValue = int(chr(Data[3]))
        where = str(chr(Data[5]))
        i = 5
        while 1:
            i += 1
            if chr(Data[i+2]) == '#':
                break
            where += str(chr(Data[i]))
        Domoticz.Debug("Device found id: " + str(hex(int((where)))))
        unit = FindUnit(self,str(hex(int(where))))
        if unit is not None:
           Devices[unit].Update(nValue = nValue,sValue=str(nValue))
        
def FindUnit(self,where):
    for item in Devices:
        if Devices[item].DeviceID == where:
            return Devices[item].Unit
    return None
                
def checkNack(self, Data):
    if chr(Data[3]) == '0':
        Domoticz.Error("Nack on last command: " + self._lastCmd)
        if self._lastCmd == "join":
            self._connection.Send("*13*60*##",2)
    elif chr(Data[3]) == '1' :
        if self._lastCmd == "join" :
            self._joinedNetwork = True
            Domoticz.Status("Network joined, start communication.")
            self._lastCmd = "scan"
            self._connection.Send("*13*65*##")
        elif self._lastCmd == "scan" :
            Domoticz.Status("Scan network begin.")
            self._scanningNetwork = True
        elif self._lastCmd == "On":
            Devices[self._lastTargetUnit].Update(nValue = 1,sValue="1")
        elif self._lastCmd == "Off":
            Devices[self._lastTargetUnit].Update(nValue = 0,sValue="0")
            if self._lastTargetUnit == 255 : #All off
                for item in Devices:
                    Devices[item].Update(nValue = 0,sValue="0")
    else:
        Domoticz.Error("Unknown frame format")
                
def statusGateway(self,Data): # WHO = 13
    if chr(Data[5]) == '*':
        if chr(Data[6]) == '6' and chr(Data[7]) == '7' and chr(Data[8]) == '*':
            if chr(Data[10]) == '#':
                self._NbDevicesNetwork = int(chr(Data[9]))
                Domoticz.Status("The network contains " + str(self._NbDevicesNetwork) + " device(s).")
            elif chr(Data[11]) == '#':
                self._NbDevicesNetwork = int(str(chr(Data[9])) + str(chr(Data[10])))
                Domoticz.Status("The network contains " + str(self._NbDevicesNetwork) + " device(s).")
            else:
                return
            self._scannedDevice = self._NbDevicesNetwork # device nb to scan
            scanNetworkDevices(self)
    else:
        where = str(chr(Data[5]))
        i = 5
        while 1:
            i += 1
            if chr(Data[i+2]) == '#':
                break
            where += str(chr(Data[i]))
        Domoticz.Status("Device found id: " + str(hex(int((where)))))
        i = i+2 #jump Unit
        if chr(Data[i+7]) == '*' or chr(Data[i+7]) == '#':
            id = int(chr(Data[i+6]))
        else:
            id = int(str(chr(Data[i+6]))+str(chr(Data[i+7])))
        
        while 1:
            i += 1
            if chr(Data[i]) == '#':
                break
        if id not in Devices:
            if chr(Data[i-3]) == '2' and chr(Data[i-2]) == '5' and chr(Data[i-1]) == '6':
                Domoticz.Device(DeviceID = str(hex(int(where))), Name = "Switch" + str(id),  Unit = id, TypeName = "Switch").Create()
                Domoticz.Status("Device Switch " + str(id) + " with DeviceID " + str(hex(int(where))) + " created.")

        scanNetworkDevices(self)

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onDeviceRemoved( Unit ):
    global _plugin
    _plugin.onDeviceRemoved( Unit )

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
