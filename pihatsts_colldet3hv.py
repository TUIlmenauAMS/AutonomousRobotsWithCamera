#Program to compute the apparent optical "collision speed" with an object in front from the camera video
#to control Roomba
#Gerald Schuller, July 2016
#using the center of mass of frequencies of DCT, (or DCT of its magnitude, kind of a cepstrum) reduction in frequency is collision course.
#horizontal and vertical frequencies, for kind of a cepstrum

import cv2
import scipy.fftpack
import scipy.signal
import numpy as np
import time
import os
#import espeak
#from shiftdiffcomp import diffshiftfast
#import serial
#import serial.tools.list_ports
import explorerhat

"""
ports=serial.tools.list_ports.comports()
print "Ports: ", ports

#ser = serial.Serial('/dev/tty',115200)  #dummy for testing
#ser = serial.Serial('/dev/ttyUSB0',115200)  # open USB serial port, speed 115200 for Roomba 5xx
ser = serial.Serial('/dev/ttyAMA0',115200)  # open Raspi GPIO serial port, speed 115200 for Roomba 5xx
#ser = serial.Serial('/dev/ttyAMA0',57600)  # open Raspi GPIO serial port, speed 57600 for Roomba 3xx
print(ser.name)         # check which port was really used

#Start mode, page 27:
ser.write(b'\x80')
#ser.write(b'\x80')
#Control mode:
time.sleep(1)
ser.write(b'\x82')
time.sleep(2)
"""



cap = cv2.VideoCapture(0)
[retval, frame] = cap.read()  
currframe=np.array(frame[:,:,1],dtype=float)
#prevframe=currframe.copy()

rows, cols= currframe.shape
print("rows, cols =", rows, cols)

rows, cols= currframe.shape
print("rows, cols =", rows, cols)
countermatrix=np.zeros((rows, cols))*(1+1j)


"""
#Vacuum motors on:
ser.write(b'\x8a\x07')
time.sleep(0.2)
print "forward"
#ser.write(b'\x89\x00\xfa\x80\x00')     # write a string
#slower:
ser.write(b'\x89\x00\x80\x80\x00')
time.sleep(0.2)
"""
print("moving forward")
explorerhat.motor.one.forward(50)
explorerhat.motor.two.forward(50)
time.sleep(0.2)

zl=0
medfiltlen=3
collspeed=0 #np.zeros(medfiltlen)
collision=False

#countermatrix: index matrix, with index pair as complex number:
for r in range(cols):
   for i in range(rows):
      countermatrix[i,r]=r+1j*i



for n in range(20000):
    # Capture frame-by-frame
    

    zl+=1
    
    #Find center of mass of frequency components of previous frame:
    [retval, frame] = cap.read()  
    #keep the green component:
    currframe=np.array(frame[:,:,1],dtype=float)
    #Find center of mass of frequency components:
    #A=np.abs(scipy.fftpack.dct(currframe,axis=1))
    #A sort of cepstrum, horizontally and vertically:
    A=(scipy.fftpack.dct(currframe,axis=1))
    A=np.abs(scipy.fftpack.dct(A,axis=0))
    #remove DC:
    A[0,0]=0
    #Take inner 100 rows and cols for cepstrum:
    A=(scipy.fftpack.dct(A[0:100,0:100],axis=1))
    A=np.abs(scipy.fftpack.dct(A,axis=0))
    Acenterprev=np.sum(A*countermatrix[0:100,0:100])/np.sum(A)
    #wait for next frame:
    #time.sleep(0.1)
    #Find center of mass of frequency components of current frame:
    [retval, frame] = cap.read()  
    #keep the green component:
    currframe=np.array(frame[:,:,1],dtype=float)
    #Acenterprev=Acenter.copy()
    #Find center of mass of frequency components:
    
    #A sort of cepstrum, horizontally and vertically:
    A=(scipy.fftpack.dct(currframe,axis=1))
    A=np.abs(scipy.fftpack.dct(A,axis=0))
    #remove DC:
    A[0,0]=0
    #For detecting blurred image when close to something:
    HFcoeff=np.sum(A[40:,40:])/(rows*cols)
    #compute cepstrum:
    A=(scipy.fftpack.dct(A[0:100,0:100],axis=1))
    A=np.abs(scipy.fftpack.dct(A,axis=0))
    Acenter=np.sum(A*countermatrix[0:100,0:100])/np.sum(A)
    #print("a.shape =", a.shape)
    #If magnitude of frequencies (horisontal + j*vertical) reduces compared to pred frame, 
    #we have collision speed:
    #collspeed[zl%medfiltlen]= -np.abs(Acenterprev)+np.abs(Acenter)
    #collspeedfilt=scipy.signal.medfilt(collspeed)
    collspeedfilt=-np.abs(Acenterprev)+np.abs(Acenter)

    print("collspeedfilt= ", collspeedfilt)
    print("High Frequency Coeff.:", HFcoeff)
    if (collspeedfilt > 1.0) or (np.abs(collspeedfilt)<0.05) or (HFcoeff<1000):
    #if (collspeedfilt[1] > 0.4) or (HFcoeff<1000):
       if (collspeedfilt > 1.0):
          print("Collision")
       if (np.abs(collspeedfilt)<0.05):
          print("no movement")
       if (HFcoeff<1000):
          print("blurred")
       collision=True
    else:
       print("No collision")
       collision=False

    print("collision= ", collision)
    
##############################

  
    
    if collision==True:
       """
       #go backwards:
       rn=np.random.random(1)
       #print("nr =", rn)
       radius=int((rn[0]-0.5)*4000.0)
       if radius<0:
          radius+=2**16-1
       print("Radius= ", radius)
       #go backwards: 
       print("Backwards")
       ser.write(b'\x89\xff\x38'+chr(radius/256)+chr(radius%256))  
       time.sleep(0.8)
       """
       #Turn around in place:
       #ser.write(b'\x89\x00\x70\x00\x01')
       #time.sleep(2+2.5*(np.random.random(1)))
       #turn left 90 degrees:
       print("turn left about 90 degrees:")
       explorerhat.motor.two.backward(50)
       explorerhat.motor.one.forward(50)
       #time.sleep(1.0)
       time.sleep(0.6+0.8*(np.random.random(1)))
       
       #stop,speed 0::
       #ser.write(b'\x89\x00\x00\x00\x00')
       #time.sleep(0.5)
       #re-start camera to clear buffer, reduce delay:
       #formerly restart camera
       
       print("restart camera")
       cap.release()
       cap = cv2.VideoCapture(0)
       time.sleep(0.4)
       print("restarted camera")
       
       #go forward
       #ser.write(b'\x89\x00\xfa\x80\x00')    
       #slower:
       #ser.write(b'\x89\x00\x80\x80\x00') 
       explorerhat.motor.one.forward(50)
       explorerhat.motor.two.forward(50)
       #time.sleep(1)

       """
       rn=np.random.random(1)
       #print("nr =", rn)
       radius=int((rn[0]-0.5)*4000.0)
       if radius<0:
          radius+=2**16-1
       print("Radius= ", radius) 
       ser.write(b'\x89\x00\xfa'+chr(radius/256)+chr(radius%256)) 
       """
    if n%300==0:
       #go forward in random direction:
       rn=np.random.random(1)
       print("nr =", rn)
       """
       radius=int((rn[0]-0.5)*4000.0)
       if radius<0:
          radius+=2**16-1
       print("Radius= ", radius)
       """
       #go forward
       #ser.write(b'\x89\x00\xfa'+chr(radius/256)+chr(radius%256)) 
       #slower:
       #ser.write(b'\x89\x00\x80'+chr(radius/256)+chr(radius%256))  
       explorerhat.motor.one.forward(50-rn*20)
       explorerhat.motor.two.forward(50+rn*20)
       
       
    """
    #Keep window open until key 'q' is pressed:
    if cv2.waitKey(50) & 0xFF == ord('q'):
        break
    """
#stop,speed 0::
#ser.write(b'\x89\x00\x00\x00\x00')
explorerhat.motor.one.forward(0)
explorerhat.motor.two.forward(0)
#time.sleep(0.2)
#vacuum motors off:
#ser.write(b'\x8a\x00')
#time.sleep(0.2)
#os.system('espeak -vde -s 120 "Jetzt bin ich fertig. "');
#print "close"
#ser.close()  

# When everything done, release the capture
cap.release()
#cv2.destroyAllWindows()

