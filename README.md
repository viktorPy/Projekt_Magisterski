# Projekt_Magisterski
The aim of the master thesis was to create the prototype of a system for verifying payments for parking vehicles and prove that clouding computing solutions
can be applied in various applications - especially for the license plate recognition.

The prototype has been created by using Raspberry Pi 4 board with attached camera and 7' display. 

The main application of the prototype is veryfining payments for parking vehicles, parked at the streets - especially in the parking paid zone.

The main flow can be presented into the following way:
1. Capture the frame from the camera
2. Preprocess the gathered frame, to find the license plate
3. Find the license plate
4. If found, cropp the image and store it in other folder - with cropped images. Store also the original frame in folder with original frames.
5. If not found, go back to first step

In parallel, another program is running, which is used for character recognition and parking ticket database verification. It works in the
following order (in the loop):

1. Select the cropped plate
2. Send request to Google Vision API to perform character recognition
3. Perform regex validation on Google Vision string response (to eliminate unecessary characters)
4. If validation returns 'no match', move the cropped plate into the folder 'no match'
5. If validation returns correct string, send request to the parking ticket database (Firestore database). 
6. Depending on the request response, the cropped image is then renamed - (ticket status, license plate and timestamp) - and moved to the dedicated folder,
according to the parking ticket status.

The whole code has been written in Python language. 
