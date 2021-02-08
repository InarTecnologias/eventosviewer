import socketio
import os
from os import listdir
from os.path import isfile, join
import psutil
import configparser
import signal 
import time

sio = socketio.Client()
path = "/home/pi/rpi-rgb-led-matrix/examples-api-use/"
config = configparser.ConfigParser()
config.read(path + 'config.ini')


scroll_ms1= config['time']['scroll_ms1']
scroll_ms2= config['time']['scroll_ms2']
scroll_ms3= config['time']['scroll_ms3']
scroll_ms4= config['time']['scroll_ms4']
duration = config['time']['duration2']
static_all = int(config['setting']['static_all'])
   
def processKill(name): 
	try:   
	# iterating through each instance of the proess 
		print(name)
		for line in os.popen("ps aux | grep " + name + " | grep -v grep"):  
			
			print(line)
			fields = line.split()
			print(fields) 
			  
			# extracting Process ID from the output 
			pid = fields[1]  
			  
			# terminating process  
			os.kill(int(pid), signal.SIGTERM)  
			print("Process Successfully terminated") 

	except Exception as error: 
		print("Error Encountered while running script")
		print(error)

def stringCreator(mypath, onlyfiles):
	s=""
	for img in onlyfiles:
		s =s + " " + mypath + "/" + img
	
	return s
		
	
def eventHandler(s, scroll_ms):
	onlyfiles = [f for f in listdir(path + s) if isfile(join(path + s, f))]
	static = 0
	if len(onlyfiles)==1 and static_all==0:
		static = 1
	os.system(path + 
	"demo -m " + scroll_ms + " -t " + duration + " -n " + str(static)
	+  " --led-chain=4 -D 2" + 
	stringCreator(path + s, onlyfiles))

@sio.event
def connect():
	print('connection established')

@sio.event
def recibido(data):
	event = data["data"]
	entrar = "light" in event or "audio" in event or "substrate" in event or "water" in event
	if entrar == True:
		print('recibo un mensaje')
		print(data)
		try:
			processKill("\"python3 /home/pi/reposo/reposo.py\"")
			processKill(path + "demo")
		except Exception:
			pass
		time.sleep(0.2)
		if "light" in event:
			eventHandler("Luz", scroll_ms1)
		elif "audio" in event:
			eventHandler("Audio", scroll_ms2)
		elif "substrate" in event:
			eventHandler("Sustrato", scroll_ms3)
		elif "water" in event:
			eventHandler("Water", scroll_ms4)

@sio.event
def disconnect():
	print('disconnected from server')


connected = False
while connected == False:
	try:
		sio.connect('http://192.168.0.171:8080')
		sio.wait()
	except Exception as error:
		print(error)
		print("Posiblemente el servidor este desconectado")
	else:
		connected = True
