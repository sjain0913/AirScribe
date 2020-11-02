import numpy as np
import cv2

# export GOOGLE_APPLICATION_CREDENTIALS="/Users/gursimransingh/Desktop/cv/project/AirScribe/HTR/airscribe-e7c8c3c8b9af.json"

print('\n ✍️  Welcome to AirScribe HTR \n :: Processing your image... \n \n')


def detect_text(path):
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    writing = ''

    for text in texts:
        writing+=' ' + text.description
    return  writing


path = "/Users/gursimransingh/Desktop/cv/project/AirScribe/HTR/test/test0.jpg"

print(detect_text(path))

print('\n \n')