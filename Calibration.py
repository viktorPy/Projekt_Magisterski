# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import imutils

from datetime import datetime
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 60
#camera.contrast = 50
camera.brightness = 50
rawCapture = PiRGBArray(camera, size=(640, 480))

 
# allow the camera to warmup
time.sleep(0.1)

now = datetime.now()
 
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array

    #get time
    now = datetime.now()
    current_time = now.strftime('%d-%m-%Y_%H-%M-%S-%f')

    #all necessary operations for plate detection
    
    image = imutils.resize(image, width=500)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray,11,70,70)
    edged = cv2.Canny(gray, 100, 200)
    
    cv2.namedWindow('canny', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('canny', 250, 250)
    cv2.imshow('canny', edged)
    
    
    #find contours based on edges
    cnts, new = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    img1 = image.copy()
    cv2.drawContours(img1, cnts, -1, (0,255,255),3)
    
    #cv2.imshow('frame', img1)
    
    #sprt contours based on their area keeping minimum required area as '30' (anything smaller than this will not be considered)
    cnts=sorted(cnts, key=cv2.contourArea, reverse=True)[:40]
    
    img2 = image.copy()
    cv2.drawContours(img2, cnts, -1, (0,255,0),2)
    
    cv2.namedWindow('Top 30', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Top 30', 250, 250)
    cv2.imshow("Top 30", img2)
    
    #cv2.imshow('frame', img2) 
    
    NumberPlateCnt = None #we currently have no number plate contour

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4: #select the contour with 4 corners
            NumberPlateCnt = approx
            x, y, w, h = cv2.boundingRect(c)
            new_img = image[y:y + h, x:x + w]  #create new image
            cv2.imwrite('CroppedPlates/licensePlate.jpg', new_img)
            #cv2.imwrite('CroppedPlates/'+current_time+'.jpg', new_img)     #store new image
            break

    if NumberPlateCnt is not None:
        #drawing the selected contour on the original image
        cv2.drawContours(image, [NumberPlateCnt], -1, (0,255,0), 3)
        cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Output', 250, 250)
        cv2.imshow("Output", image)
        #show the cropped license plate
        croppedLicensePlate = cv2.imread('CroppedPlates/licensePlate.jpg')
        #croppedLicensePlate = cv2.imread('CroppedPlates/'+current_time+'.jpg')
        cv2.imshow('License plate', croppedLicensePlate)    

    else:
        cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Output', 250, 250)
        cv2.imshow("Output", image)

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    #sleep every 100 miliseconds
    #time.sleep(0.1)
 
    # if the `q` key was pressed, break from the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

    if cv2.waitKey(1) & 0xFF == ord('d'):
        cv2.destroyAllWindows()
        break

