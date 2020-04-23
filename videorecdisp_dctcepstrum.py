#Program to capture a video from the default camera (0) and display it live on the screen
#Gerald Schuller, October 2014
#for cv2 install opencv with: pip install pyopencv
import cv2
import scipy.fftpack
import numpy as np

cap = cv2.VideoCapture(1)

"""
Typical Resolutions:
1920 x 1080
1600 x 900
1366 x 768
1280 x 720
1024 x 576
"""

#cap.set(3,1920) #sets horizontal resolutio to other value than 640
#cap.set(4, 1080) #sets vertical resolution
w=cap.get(3) #get horizintal resolution
h=cap.get(4) #get vertical resolution
#cap.set(5, 30)      #set frame rate
framerate=cap.get(5)
print(w,h, "framerate=", framerate)

#countermatrix: index matrix, with index pair as complex number:
countermatrix=np.zeros((int(h), int(w)))*(1+1j)
for r in range(int(w)):
   for i in range(int(h)):
      countermatrix[i,r]=r+1j*i

while(True):
    # Capture frame-by-frame
    [retval, frame] = cap.read() 
    #keep the green component:
    currframe=np.array(frame[:,:,1],dtype=float)
    #Find center of mass of frequency components:
    #A=np.abs(scipy.fftpack.dct(currframe,axis=1))
    #A sort of cepstrum, horizontally and vertically:
    A=(scipy.fftpack.dct(currframe,axis=1))
    A=np.abs(scipy.fftpack.dct(A,axis=0))
    #remove DC:
    #A[0,0]=0
    #take the "inverse" dct (identical to forward dct):
    #Take inner 100 rows and cols for cepstrum:
    A=(scipy.fftpack.dct(A[0:100,0:100],axis=1))
    A=np.abs(scipy.fftpack.dct(A,axis=0))
    A=A/np.max(A)
    #Center of mass, distance from the origin:
    Acenter=np.abs(np.sum(A* countermatrix[0:100,0:100]) /np.sum(A))  
    #Write the Center of mass number on display:
    cv2.putText(A, str(Acenter), (10,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (100
,100,100),1) 
    # Display the resulting frame
    cv2.imshow('DCT Cepstrum',A)
    #Keep window open until key 'q' is pressed:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
