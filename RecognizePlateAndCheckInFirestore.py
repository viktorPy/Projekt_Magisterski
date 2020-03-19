from google.cloud import vision
from google.cloud.vision import types
import os, io
import shutil
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
from datetime import datetime, timedelta

from RecognizeLicensePlateNumber import sendRequestToGoogleVision
from SendRequestToFirestore import sendVehiclePlateToFirestore


directory = os.fsencode('/home/pi/Desktop/MGR_ParkingSystem/CroppedPlates')

# Use a service account
cred = credentials.Certificate(r'/home/pi/Desktop/MGR_ParkingSystem/Certificates/ServiceAccountToken.json')
firebase_admin.initialize_app(cred)

previousVehiclePlate = None

while True:
    if len(os.listdir('/home/pi/Desktop/MGR_ParkingSystem/CroppedPlates')) > 0:
        for file in os.listdir(directory):
            logFile = open('/home/pi/Desktop/MGR_ParkingSystem/output.log', 'a')
            filename = os.fsdecode(file)
            
            #get measurement time
            now = datetime.now()
            time_1 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
            print('1-StartCharacterRecognition,time: '+time_1, file=logFile)
            
            outVehiclePlate = sendRequestToGoogleVision('/home/pi/Desktop/MGR_ParkingSystem/CroppedPlates', filename)
            
            #get measurement time
            now = datetime.now()
            time_2 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
            print('2-RecognitionFinished,time: '+time_2, file=logFile)
            
            if (outVehiclePlate == 'no match'):
                                              
                print(outVehiclePlate+'_'+filename+'\n', file=logFile)
                newName = outVehiclePlate+'_'+filename
                newPath = shutil.move('/home/pi/Desktop/MGR_ParkingSystem/CroppedPlates/'+filename, '/home/pi/Desktop/MGR_ParkingSystem/NoMatches'+'/'+newName)
                
                #get measurement time
                now = datetime.now()
                time_3 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
                print('3-NoMatchDetected,time: '+time_3, file=logFile)
                
                logFile.close()
            else:
                
                if previousVehiclePlate is not None and outVehiclePlate == previousVehiclePlate:
                    os.unlink('/home/pi/Desktop/MGR_ParkingSystem/CroppedPlates/'+filename)                    
                else:                    
                    #get measurement time
                    now = datetime.now()
                    time_4 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
                    print('4-SendRequestToFirestone,time: '+time_4, file=logFile)
                                    
                    ticketStatus = sendVehiclePlateToFirestore(outVehiclePlate)
                    
                    #get measurement time
                    now = datetime.now()
                    time_5 = now.strftime('%d-%m-%Y_%H-%M-%S-%f')
                    print('5-ReceivedRequestFromFirestone,time: '+time_5, file=logFile)
                    
                    if (ticketStatus == 'ticket expired'):
                        ##send this plate to the folder 'vehiclesWithoutValidTicket'
                        print(outVehiclePlate+'_'+filename+'_'+ticketStatus+'\n', file=logFile)
                        newName = outVehiclePlate+'_'+ticketStatus+'_'+filename
                        newPath = shutil.move('/home/pi/Desktop/MGR_ParkingSystem/CroppedPlates/'+filename, '/home/pi/Desktop/MGR_ParkingSystem/VehiclesWithExpiredParkingTicket'+'/'+newName)
                        logFile.close()
                     
                    if (ticketStatus == 'ticket valid'):
                        ##send this plate to the folder 'vehiclesWithValidTicket'
                        print(outVehiclePlate+'_'+filename+'_'+ticketStatus+'\n', file=logFile)
                        newName = outVehiclePlate+'_'+ticketStatus+'_'+filename
                        newPath = shutil.move('/home/pi/Desktop/MGR_ParkingSystem/CroppedPlates/'+filename, '/home/pi/Desktop/MGR_ParkingSystem/VehiclesWithValidParkingTicket'+'/'+newName)
                        #os.unlink('CroppedPlates/'+filename)
                        logFile.close()

                    if (ticketStatus == 'no ticket'):
                        ##send this plate to the folder 'VehiclesWithoutTicket'
                        print(outVehiclePlate+'_'+filename+'_'+ticketStatus+'\n', file=logFile)
                        newName = outVehiclePlate+'_'+ticketStatus+'_'+filename
                        newPath = shutil.move('/home/pi/Desktop/MGR_ParkingSystem/CroppedPlates/'+filename, '/home/pi/Desktop/MGR_ParkingSystem/VehiclesWithNoParkingTicket'+'/'+newName)
                        #os.unlink('CroppedPlates/'+filename)
                        logFile.close()
                        
                    previousVehiclePlate == outVehiclePlate
