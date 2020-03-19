import shutil, os

def main():
    #clean cropped plates folder
    shutil.rmtree('CroppedPlates')
    os.makedirs('CroppedPlates')
    #clean original frames folder
    shutil.rmtree('OriginalFrames')
    os.makedirs('OriginalFrames')
    #clean VehiclesWithValidParkingTicket folder
    shutil.rmtree('VehiclesWithValidParkingTicket')
    os.makedirs('VehiclesWithValidParkingTicket')
    #clean VehiclesWithNoParkingTicket folder
    shutil.rmtree('VehiclesWithNoParkingTicket')
    os.makedirs('VehiclesWithNoParkingTicket')
    #clean VehiclesWithExpiredParkingTicket folder
    shutil.rmtree('VehiclesWithExpiredParkingTicket')
    os.makedirs('VehiclesWithExpiredParkingTicket')
    #clean NoMatches folder
    shutil.rmtree('NoMatches')
    os.makedirs('NoMatches')
    print('Done!')

def createFolder():
    if os.path.isdir('CroppedPlates') == False:
        os.makedirs('CroppedPlates')


if __name__ == '__main__':
    main()
