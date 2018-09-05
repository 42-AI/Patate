try:
    import cv2
except:
    print("run 'workon cv' before you start the script")
    exit(0)

import RPi.GPIO as GPIO
import time
from picamera import PiCamera
from picamera.array import PiRGBArray

import sys
import threading

#############################################

SPEED_NORMAL = 6.8 # 6.8
SPEED_FAST = 6.65   # 6.65

DIR_L_M = 5
DIR_L = 6.5
DIR_C = 7
DIR_R = 7.5
DIR_R_M = 9

class Controler(object):
    def __init__(self):
        
        if len(sys.argv) == 2:
            self.delay = float(sys.argv[1])
        else:
            print("usage : python Auto_datamining.py [delay in sec (float)]")

        self.label = [-1, 2]

        #init GPIO with BCM numberings
        GPIO.setmode(GPIO.BCM)
        #init every used pins
        GPIO.setup(23, GPIO.OUT)
        GPIO.setup(18, GPIO.OUT)
        #set controls
        self.POW = GPIO.PWM(18, 50)
        self.DIR = GPIO.PWM(23, 50)

        # Init speed
        self.speed = SPEED_NORMAL
        # Init direction
        self.direction = DIR_C
        
        # Setup Camera
        self.camera = PiCamera()
        self.camera.resolution = (160, 128)
        self.camera.framerate = 30
        self.camera.hflip = True
        self.camera.vflip = True
        self.rawCapture = PiRGBArray(self.camera, size = (160, 120))
        time.sleep(0.5)
        
        self.POW.start(0)
        self.DIR.start(0)
        
        self.key = -1

    # Loop over camera frames
    def videoLoop(self):
        start = time.time()
        for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            # convert img as Array
            image = frame.array
            # append label
            picname = "/home/pi/Documents/Patate/Pics/Auto/" + str(self.label[0]) + "_" + str(self.label[1]) + "_" + str(time.time()) + ".jpg"
            cv2.imshow("Auto DataSet Mining", image)
            # take a pic
            if self.label[0] != -1:
                if time.time() - start > self.delay:
                    cv2.imwrite(picname, image)
                    start = time.time()
                    print("snap : " + picname)
            # Clean image before the next comes
            self.rawCapture.truncate(0)
            
            # non blocking 'wait for key'
            self.key = cv2.waitKey(1) & 0xFF
            if self.key != 255:
                if self.key == ord('a'):
                    self.POW.stop()
                    self.DIR.stop()
                    print("Stop")
                    return
                self.controls()

    def controls(self):
        if self.key == ord("z"):
            #if stopped, go
            if self.label[0] == -1:
                self.label[0] = 0
                self.speed = SPEED_NORMAL
                self.label[1] = 2
            #if turning, go forward
            elif self.label[0] == 0 and self.label[1] != 2:
                self.label[1] = 2
            #if forward, speed up
            elif self.label[0] == 0 and self.label[1] == 2:
                self.label[0] = 1
                self.speed = SPEED_FAST
                
        elif self.key == ord("q"):
            self.label[0] = 0
            self.speed = SPEED_NORMAL
            #go left
            if self.label[1] > 0:
                self.label[1] -= 1
        
        elif self.key == ord("s"):
            if self.label[0] == 0:
                self.label[0] = -1
                self.speed = 0
            elif self.label[0] == 1:
                self.label[0] = 0
                self.speed = SPEED_NORMAL
                
        elif self.key == ord("d"):
            self.label[0] = 0
            self.speed = SPEED_NORMAL
            #go right
            if self.label[1] < 4:
                self.label[1] += 1
                            
        if self.label[1] == 0:
            self.direction = DIR_L_M
        elif self.label[1] == 1:
            self.direction = DIR_L
        elif self.label[1] == 2:
            self.direction = DIR_C
        elif self.label[1] == 3:
            self.direction = DIR_R
        elif self.label[1] == 4:
            self.direction = DIR_R_M
                        
        self.POW.ChangeDutyCycle(self.speed)
        self.DIR.ChangeDutyCycle(self.direction)

if __name__ == "__main__":
    print("Press Ctrl+C to start/stop...")
    try:
      while True:
        pass
    except KeyboardInterrupt:
      pass
    controler = Controler()
    controler.videoLoop()
    
    GPIO.cleanup()



