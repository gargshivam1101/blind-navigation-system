    
# import the necessary packages
#from picamera import PiCamera
#from picamera.array import PiRGBArray
from picamera import * 
import time
import cv2
import pyttsx3
import threading
import RPi.GPIO as GPIO
import sys


engine = pyttsx3.init()
newVoiceRate =200 
engine.setProperty('rate' , newVoiceRate)
# Python program to illustrate the concept 
# of threading 
# importing the threading module 
def distance_calculator(a,b): 
    
    TRIG1 = a
    ECHO1 = b
    
    
    GPIO.setmode(GPIO.BOARD)
    
    GPIO.setup(TRIG1,GPIO.OUT)
    GPIO.setup(ECHO1,GPIO.IN)

    GPIO.output(TRIG1,False)
    time.sleep(1)


    GPIO.output(TRIG1,True)
    time.sleep(0.00001)
    GPIO.output(TRIG1,False)


    while GPIO.input(ECHO1)==0:
        pulse_start1 = time.time()
    
    while GPIO.input(ECHO1)==1:
        pulse_end1 = time.time()

    pulse_duration1 = pulse_end1 - pulse_start1

    distance1 = pulse_duration1 * 17150
    distance1 = round(distance1,2)

    print ("Distance ",distance1,"cm")

    GPIO.cleanup()
    return int(distance1)

dstraight=0
dleft=0
dright=0

def distance():
    global dstraight
    global dright
    global dleft
    dstraight = distance_calculator(16,18)
    dleft = distance_calculator(40,38)
    dright = distance_calculator(31,33)
    print(str(dleft)+"   "+str(dstraight)+"   "+str(dright))


answer_l= ""
answer_c = ""
answer_r = ""
# Pretrained classes in the model
classNames = {0: 'background',
              1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane', 6: 'bus',
              7: 'train', 8: 'truck', 9: 'boat', 10: 'traffic light', 11: 'fire hydrant',
              13: 'stop sign', 14: 'parking meter', 15: 'bench', 16: 'bird', 17: 'cat',
              18: 'dog', 19: 'horse', 20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear',
              24: 'zebra', 25: 'giraffe', 27: 'backpack', 28: 'umbrella', 31: 'handbag',
              32: 'tie', 33: 'suitcase', 34: 'frisbee', 35: 'skis', 36: 'snowboard',
              37: 'sports ball', 38: 'kite', 39: 'baseball bat', 40: 'baseball glove',
              41: 'skateboard', 42: 'surfboard', 43: 'tennis racket', 44: 'bottle',
              46: 'wine glass', 47: 'cup', 48: 'fork', 49: 'knife', 50: 'spoon',
              51: 'bowl', 52: 'banana', 53: 'apple', 54: 'sandwich', 55: 'orange',
              56: 'broccoli', 57: 'carrot', 58: 'hot dog', 59: 'pizza', 60: 'donut',
              61: 'cake', 62: 'chair', 63: 'couch', 64: 'potted plant', 65: 'bed',
              67: 'dining table', 70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse',
              75: 'remote', 76: 'keyboard', 77: 'cell phone', 78: 'microwave', 79: 'oven',
              80: 'toaster', 81: 'sink', 82: 'refrigerator', 84: 'book', 85: 'clock',
              86: 'vase', 87: 'scissors', 88: 'teddy bear', 89: 'hair drier', 90: 'toothbrush'}


def id_class_name(class_id, classes):
    for key, value in classes.items():
        if class_id == key:
            return value
model = cv2.dnn.readNetFromTensorflow('/home/pi/Downloads/ExploreOpencvDnn-master/models/frozen_inference_graph.pb',
                                      '/home/pi/Downloads/ExploreOpencvDnn-master/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')


def image_processing_c():
    image = cv2.imread("solver.jpeg")
    image = cv2.resize(image , (480 , 300))
    image=image[0:300,120:360]
    #cv2.imwrite("image_c.jpeg",image)
    model.setInput(cv2.dnn.blobFromImage(image, size=(160, 300), swapRB=True))
    output = model.forward()
# print(output[0,0,:,:].shape)

    global answer_c
    answer_c = " "
    for detection in output[0, 0, :, :]:
        confidence = detection[2]
        if confidence > .5:
            class_id = detection[1]
            class_name=id_class_name(class_id,classNames)
        
            #print(str(str(class_id) + " " + str(detection[2])  + " " + class_name))
            newvar = class_name + "  "
            answer_c += newvar
            

while(1):

    camera = PiCamera()
    camera.rotation = 270     


    camera.capture('solver.jpeg')
    
    camera.close()
    t1 = threading.Thread(target=image_processing_c)
    t2 = threading.Thread(target=distance)
   
    t1.start()
    t2.start()
    
    t1.join()
    
    t2.join()
    

   
 
    if(answer_c == " "):
        answer_c = "unknown object"
    print("answer_c= "+answer_c)

    if(dstraight <= 100):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(29 , GPIO.OUT)
        GPIO.output(29,GPIO.HIGH)
        #time.sleep(1)
       
        if(dleft <=100 and dright <= 100):
            engine.say(answer_c + " infront of you Stop Moving")
            engine.runAndWait()
        if(dleft <= dright):
            engine.say(answer_c + " infront of you Move Right")
            engine.runAndWait()
        else:
            engine.say(answer_c + " infront of you Move Left")
            engine.runAndWait()
        GPIO.output(29,GPIO.LOW)
        GPIO.cleanup()
    else:
            engine.say(" Keep Moving ")
            engine.runAndWait()
   
