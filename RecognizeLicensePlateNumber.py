from google.cloud import vision
from google.cloud.vision import types
import os, io
import re

def sendRequestToGoogleVision(input_folder, path):

    from google.cloud import vision
    from google.cloud.vision import types
    import os, io
    import re

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'/home/pi/Desktop/MGR_ParkingSystem/Certificates/ServiceAccountToken.json'
    client = vision.ImageAnnotatorClient()

    input_file = path

    with io.open(input_folder+'/'+input_file, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    objects = client.object_localization(image=image)

    texts = response.text_annotations

    out = ''

    for text in texts:
        out+=''+text.description
    
    if out == '':
        return 'no match'
    
    else:
        out.strip()
        validated = re.search(r".{4,9}", out)
        
        if validated:
            vehiclePlate = validated.group().replace(' ','')
            return vehiclePlate
        else:
            return 'no match'

        




    
