#!/usr/bin/python3
import sys
args=sys.argv
print ('Number of arguments:', len(args), 'arguments.')
print ('Argument List:', args)


#ensure logging is enabled
try:
  import ldogging
except ModuleNotFoundError:
  exception_return = sys.exc_info()
  print(exception_return)
  print("Generally installed with all python installation. Refere to python documentation. I can not help")
  quit()
  
  
logging.basicConfig(filename='/var/log/elitepro.log',level=logging.DEBUG)

  
import signal
import datetime
  

import serial 
import socket



'''
with logging
This program reads all bytes and writes them to a file in /root/elite folder
first byte is ENQ last one is EOT
This help in capturing everything between ENQ and EOT and learn equipment specific need
'''

output_folder='/root/erba/' #remember ending/
input_tty='/dev/ttyUSB0'
#For testing
#socat -d -d - pty,raw,echo=0
#input_tty='/dev/pts/2'


def get_filename():
  dt=datetime.datetime.now()
  return output_folder+dt.strftime("%Y-%m-%d-%H-%M-%S-%f")


quit()

#Globals############################
byte_array=[]
byte=b'd'

#main loop##########################
#port = serial.Serial(input_tty, baudrate=9600)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('12.207.13.179',15300))
s.listen(1)
port, addr = s.accept()
print ('Connection address:', addr)


while byte!=b'':
  byte=port.recv(1)
  byte_array=byte_array+[chr(ord(byte))]	#add everything read to array
  if(byte==b'\x05'):
    port.send(b'\x06');
    cur_file=get_filename()					#get name of file to open
    x=open(cur_file,'w')					#open file    
    logging.debug('<ENQ> received. <ACK> Sent. Name of File opened to save data:'+str(cur_file))
  elif(byte==b'\x0a'):
    port.send(b'\x06');
    try:
      x.write(''.join(byte_array))			#write to file everytime LF received, to prevent big data memory problem
      byte_array=[]							#empty array      
    except Exception as my_ex:
      logging.debug(my_ex)
    logging.debug('<LF> received. <ACK> Sent. array written to file. byte_array zeroed')
    
  elif(byte==b'\x04'):
    print("<EOF>")
    x.write(''.join(byte_array))			#write last byte(EOF) to file
    byte_array=[]							#empty array      
    x.close()								#close file
    logging.debug('<EOF> received. array( only EOF remaining ) written to file. File closed:')

  #else:
    #byte_array=byte_array+[chr(ord(byte))]

