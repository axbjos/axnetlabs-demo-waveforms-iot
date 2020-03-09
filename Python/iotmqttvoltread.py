"""
   Waveforms SDK Integration with MQTT
   "IOT Mesurement" Example
   Author:  Joe Axberg
   Revision:  03-09-2020

   Requires:                       
       Python 3
   
   The program uses the Voltmeter capability 
   of the Analog Discovery to do simple voltage 
   measurement.  Just simple...

"""

from ctypes import *         #c compatible datatypes
from dwfconstants import *   #waveforms stuff
import time                  #to do sleep timers, etc.
import sys                   #used to check what platform the code is on
import paho.mqtt.client as mqtt

#the following section detects the operating system type (RaspberryPi would be libdwf linux style)
if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

#declare ctype variables
hdwf = c_int()
voltage1 = c_double()
voltage2 = c_double()

#declare MQTT variables
broker_address="localhost"

#print(DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#connect to message bus
print("Connecting to MQTT")
client = mqtt.Client("DWF")
client.connect(broker_address)

#
#open device
"Opening first device..."
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(szerr.value)
    print("failed to open device")
    quit()

#set up the channels
print("Preparing to read sample...")
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_bool(True)) 
dwf.FDwfAnalogInChannelOffsetSet(hdwf, c_int(0), c_double(0)) 
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5)) 
dwf.FDwfAnalogInConfigure(hdwf, c_bool(False), c_bool(False)) 

#sleep timer to wait for device
time.sleep(2)

for i in range(5):
    time.sleep(1)
    dwf.FDwfAnalogInStatus(hdwf, False, None) 
    dwf.FDwfAnalogInStatusSample(hdwf, c_int(0), byref(voltage1))
    dwf.FDwfAnalogInStatusSample(hdwf, c_int(1), byref(voltage2))
    print("Channel 1:  " + str(voltage1.value)+" V")
    print("Channel 2:  " + str(voltage2.value)+" V")
    client.publish("voltage", str(voltage1.value))

dwf.FDwfDeviceCloseAll()
