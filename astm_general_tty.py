#!/usr/bin/python3
import sys

#args=sys.argv
#print ('Number of arguments:', len(args), 'arguments.')
#print ('Argument List:', args)

#defaults###############

#tty#uncoment as needed
#connection_type='tty'
#input_tty='/dev/ttyS2'

#tcp#uncomment as needed
connection_type='tcp'
host_address='127.0.0.1'
host_port='11111'
s=None
logfile_name='/var/log/elitepro.log'
output_folder='/root/elite/' #remember ending/

#Something I tend to forget####################
#to try various tty#
#tty=input("Which tty?")
#input_tty='/dev/ttyS'+tty
#print(input_tty)

#For testing
#socat -d -d - pty,raw,echo=0
#see output of socat to find correct pty
#input_tty='/dev/pts/2'
################################################


#ensure logging module is imported
try:
  import logging
except ModuleNotFoundError:
  exception_return = sys.exc_info()
  print(exception_return)
  print("Generally installed with all python installation. Refere to python documentation.")
  quit()
#ensure that log file is created/available
try:
  logging.basicConfig(filename=logfile_name,level=logging.DEBUG)
  print("See log at {}".format(logfile_name))
except FileNotFoundError:
  exception_return = sys.exc_info()
  print(exception_return)  
  print("{} can not be created. Folder donot exist? No permission?".format(logfile_name))
  quit()
try:
  import signal
  import datetime
  import time
except ModuleNotFoundError:
  exception_return = sys.exc_info()
  logging.debug(exception_return) 
  logging.debug("signal, datetime and serial modules are required. Install them")
  quit()   

if(connection_type=='tty'):
  try:
    import serial 
  except ModuleNotFoundError:
    exception_return = sys.exc_info()
    logging.debug(exception_return) 
    logging.debug("serial module (apt install python3-serial) is required. Install them")
    quit()   
elif(connection_type=='tcp'):
  try:
    import socket
  except ModuleNotFoundError:
    exception_return = sys.exc_info()
    logging.debug(exception_return) 
    logging.debug("socket module is required. Generally installed with basic python installation.")
    quit()   

def get_filename():
  dt=datetime.datetime.now()
  return output_folder+dt.strftime("%Y-%m-%d-%H-%M-%S-%f")

def get_port():
  if(connection_type=='tty'):
    port = serial.Serial(input_tty, baudrate=9600)
    return port
  elif(connection_type=='tcp'):
    global s 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host_address,int(host_port)))	#it is a tuple
    logging.debug('post-bind pre-listen')
    s.listen(1)
    
    logging.debug('Listening Socket (s) details below:')
    logging.debug(s)    
 
    logging.debug('Waiting for connection from a client....')   
    conn_tuple = s.accept()
    
    logging.debug('Client request received. Listening+ Accepting Socket (conn_tuple) details below:')
    logging.debug(conn_tuple)
    
    return conn_tuple[0]
  
def my_read(port):
  if(connection_type=='tty'):
    return port.read(1)
  elif(connection_type=='tcp'):
    return port.recv(1)

def my_write(port,byte):
  if(connection_type=='tty'):
    return port.write(byte)
  elif(connection_type=='tcp'):
    return port.send(byte)
#main loop##########################

port=get_port()

byte=b'd'									#Just to enter the loop
byte_array=[]								#initialized to ensure that first byte can be added

#while byte!=b'':
while True:
  byte=my_read(port)
  if(byte==b''):
    logging.debug('<EOF> reached. Connection broken: details below')
    logging.debug('(Broken) Listening Socket (s) details below:')
    logging.debug(s)
    try:
      port=get_port()
    except OSError:
      exception_return = sys.exc_info()
      logging.debug(exception_return) 
      logging.debug('Some problem reconnecting, sleeping for 10 sec')
      time.sleep(10)
  else:
    byte_array=byte_array+[chr(ord(byte))]	#add everything read to array
    
    
  if(byte==b'\x05'):
    byte_array=[]							#empty array      
    my_write(port,b'\x06');
    cur_file=get_filename()					#get name of file to open
    x=open(cur_file,'w')					#open file    
    logging.debug('<ENQ> received. <ACK> Sent. Name of File opened to save data:'+str(cur_file))
  elif(byte==b'\x0a'):
    my_write(port,b'\x06');
    try:
      x.write(''.join(byte_array))			#write to file everytime LF received, to prevent big data memory problem
      byte_array=[]							#empty array      
    except Exception as my_ex:
      logging.debug(my_ex)
    logging.debug('<LF> received. <ACK> Sent. array written to file. byte_array zeroed')
    
  elif(byte==b'\x04'):
    x.write(''.join(byte_array))			#write last byte(EOF) to file
    byte_array=[]							#empty array      
    x.close()								#close file
    logging.debug('<EOT> received. array( only EOF remaining ) written to file. File closed:')
