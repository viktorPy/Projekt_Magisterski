# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import imutils
from datetime import datetime
import os

from google.cloud import vision
from google.cloud.vision import types
import os, io
import re
 
#initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 60
camera.brightness = 60
camera.contrast = 50
rawCapture = PiRGBArray(camera, size=(640, 480))
 
#allow the camera to warmup
time.sleep(0.1)

#set some parameters here
CroppingIsApplied = False #set true if cropping must be applied
ShowTheCannyEdge = True #set true if canny edge preview is required
SaveCroppedVehiclePlate = True #set true if cropped license plate must be saved
PassOnlyVehiclePlates = True #set true if noiseFiltering algorithm must be applied

#cv2.namedWindow('License plate', cv2.WINDOW_NORMAL)
#cv2.resizeWindow('License plate', 20, 40)
cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow("Frame", 600 , 300)

#capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    
    image_wholeCar = image.copy()
    
    #log file
    logFile = open('/home/pi/Desktop/MGR_ParkingSystem/logger.log', 'a')
    
    #get measurement time
    now = datetime.now()
    time_1 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
    print('***start***', file=logFile)
    print('1-StartCapturing,time: '+time_1, file=logFile)

    #crop frame to focus camera only on the middle part of the frame
    if CroppingIsApplied == True:
        x1=20
        y1=100
        h2=300
        w2=600
        image = image[y1:y1+h2, x1:x1+w2]
        
    #get measurement time
    now = datetime.now()
    time_2 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
    print('2-StartResizing,time: '+time_2, file=logFile)
    
    image = imutils.resize(image, width=500)
    
    #get measurement time
    now = datetime.now()
    time_3 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
    print('3-FinishResizing,StartGrayConversion,time: '+time_3, file=logFile)  
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    #get measurement time
    now = datetime.now()
    time_4 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
    print('4-FinishGrayConversion,StartBilateralFiltering,time: '+time_4, file=logFile)
    
    #gray = cv2.GaussianBlur(gray, (5,5), 0)
    
    gray = cv2.bilateralFilter(gray,11,17,17)
    
    #get measurement time
    now = datetime.now()
    time_5 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
    print('5-FinishBilateralFiltering,StartCannyEdgeDetection,time: '+time_5, file=logFile)  
        
    edged = cv2.Canny(gray, 130, 200)        

    if ShowTheCannyEdge == True:
        cv2.namedWindow('Canny', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Canny', 250, 250)
        cv2.imshow('Canny', edged)
        
    #get measurement time
    now = datetime.now()
    time_6 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
    print('6-FinishCannyEdgeDetection,StartFindContours,time: '+time_6, file=logFile)  

    #find contours based on edges
    cnts, new = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    #get measurement time
    now = datetime.now()
    time_7 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
    print('7-FinishFindContours,StartSortingContours,time: '+time_7, file=logFile)  
    
    #sprt contours based on their area keeping minimum required area as '30'
    cnts=sorted(cnts, key=cv2.contourArea, reverse=True)[:30]

    #get measurement time
    now = datetime.now()
    time_8 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
    print('8-FinishSortingContours,StartFindingPossiblePlate,time: '+time_8, file=logFile) 

    NumberPlateCnt = None

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        
        #select the contour with 4 corners
        if len(approx) == 4: 
            NumberPlateCnt = approx
            x, y, w, h = cv2.boundingRect(c)
            #create new image
            new_image = image[y:y + h, x:x + w]
            
            #get measurement time
            now = datetime.now()
            time_9 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
            print('9-FinishFindingPossiblePlate,StartPassingOnlyVehiclePlate,time: '+time_9, file=logFile)

            if PassOnlyVehiclePlates == True:
                #initialize the variables to check the size of detected object
                height_double = 0.0
                width_double = 0.0
                ratio = 0.0
                height_int = 0
                width_int = 0

                #threshold values
                heightMin = 28
                widthMin = 80
                ratioThresholdMin = 0.27
                ratioThresholdMax = 0.46

                dimensions = new_image.shape
                height_double = new_image.shape[0]
                height_int = new_image.shape[0]
                width_double = new_image.shape[1]
                width_int = new_image.shape[1]

                ratio = height_double / width_double

                if ratioThresholdMin <= ratio <= ratioThresholdMax:
                    if height_int >= heightMin:
                        if width_int >= widthMin:
                            if SaveCroppedVehiclePlate == True:
                                
                                #get measurement time
                                now = datetime.now()
                                time_10 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
                                print('10A-FinishPassingOnlyVehiclePlate,SaveFiles,time: '+time_10, file=logFile)
                                
                                #store new images
                                cv2.imwrite('/home/pi/Desktop/MGR_ParkingSystem/CroppedPlates/'+time_10+'.jpg', new_image)
                                cv2.imwrite('/home/pi/Desktop/MGR_ParkingSystem/OriginalFrames/'+time_10+'.jpg', image_wholeCar)                                
                                break
                        else:
                            NumberPlateCnt = None
                    else:
                        NumberPlateCnt = None                    
                else:
                    NumberPlateCnt = None

    if NumberPlateCnt is not None:
        #drawing the selected contour on the original image
        cv2.drawContours(image, [NumberPlateCnt], -1, (0,255,0), 3)
        cv2.imshow("Frame", image)
        
        #croppedLicensePlate = cv2.imread('CroppedPlates/'+current_time+'.jpg')
        #cv2.imshow('License plate', croppedLicensePlate)    

    else:
        cv2.imshow("Frame", image)
        
        #get measurement time
        now = datetime.now()
        time_11 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
        print('10B-FinishPassingOnlyVehiclePlate,NoPlateDetected,time: '+time_11, file=logFile)

        # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    #sleep every 50 miliseconds
    #time.sleep(0.05)
    
    #close log file
    logFile.close()
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        os.system("sudo pkill -f /home/pi/Desktop/MGR_ParkingSystem/RecognizePlateAndCheckInFirestore.py")
        logFile.close()
        break

    if cv2.waitKey(1) & 0xFF == ord('r'):
        #start the vision recognition
        os.system("nohup python3 /home/pi/Desktop/MGR_ParkingSystem/RecognizePlateAndCheckInFirestore.py > /home/pi/Desktop/MGR_ParkingSystem/output.log &")
        pass

    if cv2.waitKey(1) & 0xFF == ord('s'):
        #kill the process of vision recognition
        os.system("sudo pkill -f /home/pi/Desktop/MGR_ParkingSystem/RecognizePlateAndCheckInFirestore.py")
        pass  