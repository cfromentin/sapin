#!/usr/bin/env python3
#############################################################################
# Filename    : decompte.py
# Description : Control 4_Digit_7_Segment_Display by 74HC595
# Author      : tom fromentin
# modification: 2020/12/18
########################################################################
import RPi.GPIO as GPIO
import time
import threading
endstr = time.strftime("24 Dec %y",time.gmtime())
end = time.strptime(endstr, "%d %b %y")
fin_en_seconde = time.mktime(end)

yearendstr = time.strftime("31 Dec %y",time.gmtime())
yearend = time.strptime(yearendstr, "%d %b %y")
fin_annee = time.mktime(yearend)

LSBFIRST = 1
MSBFIRST = 2
#define the pins connect to 74HC595
dataPin   = 33#18      #DS Pin of 74HC595(Pin14)
latchPin  = 35#16      #ST_CP Pin of 74HC595(Pin12)
clockPin = 37#12       #SH_CP Pin of 74HC595(Pin11)
dataPin1   = 18      #DS Pin of 74HC595(Pin14)
latchPin1  = 16      #ST_CP Pin of 74HC595(Pin12)
clockPin1 = 12       #SH_CP Pin of 74HC595(Pin11)
num = (0xc0,0xf9,0xa4,0xb0,0x99,0x92,0x82,0xf8,0x80,0x90)
digitPin = (11,13,15,19)    # Define the pin of 7-segment display common end
temps_list = [8,8,8,8,8,8,8,8,8]         # Variable counter, the number will be dislayed by 7-segment display
second_temps_list = [8,8,8,8,8,8,8,8,8]
t = 0        # define the Timer object
def setup():
    GPIO.setmode(GPIO.BOARD)    # Number GPIOs by its physical location
    GPIO.setup(dataPin, GPIO.OUT)       # Set pin mode to output
    GPIO.setup(latchPin, GPIO.OUT)
    GPIO.setup(clockPin, GPIO.OUT)
    GPIO.setup(dataPin1, GPIO.OUT)       # Set pin mode to output
    GPIO.setup(latchPin1, GPIO.OUT)
    GPIO.setup(clockPin1, GPIO.OUT)
    for pin in digitPin:
        GPIO.setup(pin,GPIO.OUT)
    
def shiftOut(dPin,cPin,order,val):      
    for i in range(0,8):
        GPIO.output(cPin,GPIO.LOW);
        if(order == LSBFIRST):
            GPIO.output(dPin,(0x01&(val>>i)==0x01) and GPIO.HIGH or GPIO.LOW)
        elif(order == MSBFIRST):
            GPIO.output(dPin,(0x80&(val<<i)==0x80) and GPIO.HIGH or GPIO.LOW)
        GPIO.output(cPin,GPIO.HIGH)
            
def outData(data):      #function used to output data for 74HC595
    GPIO.output(latchPin,GPIO.LOW)
    shiftOut(dataPin,clockPin,MSBFIRST,data)
    GPIO.output(latchPin,GPIO.HIGH)
def outData1(data):      #function used to output data for 74HC595
    GPIO.output(latchPin1,GPIO.LOW)
    shiftOut(dataPin1,clockPin1,MSBFIRST,data)
    GPIO.output(latchPin1,GPIO.HIGH)
    
def selectDigit(digit): # Open one of the 7-segment display and close the remaining three, the parameter digit is optional for 1,2,4,8
    GPIO.output(digitPin[0],GPIO.LOW if ((digit&0x08) == 0x08) else GPIO.HIGH)
    GPIO.output(digitPin[1],GPIO.LOW if ((digit&0x04) == 0x04) else GPIO.HIGH)
    GPIO.output(digitPin[2],GPIO.LOW if ((digit&0x02) == 0x02) else GPIO.HIGH)
    GPIO.output(digitPin[3],GPIO.LOW if ((digit&0x01) == 0x01) else GPIO.HIGH)

def display(liste):   #display function for 7-segment display
    outData(0xff)   #eliminate residual display
    outData1(0xff)   #eliminate residual display
    selectDigit(0x01)   #Select the first, and display the single digit
    outData(num[liste[4]]&0x7f)
    outData1(num[liste[8]])
    time.sleep(0.003)   #display duration
    outData(0xff)
    outData1(0xff)
    selectDigit(0x02)   # Select the second, and display the tens digit
    outData(num[liste[3]])
    outData1(num[liste[7]])
    time.sleep(0.003)
    outData(0xff)
    outData1(0xff)
    selectDigit(0x04)   # Select the third, and display the hundreds digit
    outData(num[liste[2]]&0x7f)
    outData1(num[liste[6]]&0x7f)
    time.sleep(0.003)
    outData(0xff)
    outData1(0xff)
    selectDigit(0x08)   # Select the fourth, and display the thousands digit
    outData(num[liste[1]])
    outData1(num[liste[5]])
    time.sleep(0.003)
def timer():        #timer function
    global temps_list
    global t
    global fin_en_seconde
    global fin_annee
    t = threading.Timer(1.0,timer)      #reset time of timer to 1s
    t.start()                           #Start timing
    temps_list = []
    temps_courant = time.time()
    if temps_courant>fin_en_seconde :
        fin_en_seconde = fin_annee
    tps_date = fin_en_seconde - temps_courant
    
    reste = time.strftime("%j%H%M%S",time.gmtime(tps_date))
    for i in reste:
        temps_list.append(int(i))
        
def loop():
    global t
    global counter
    t = threading.Timer(1.0,timer)      #set the timer
    t.start()                           # Start timing
    while True:
        display(temps_list)                # display the number counter
    
def destroy():   # When "Ctrl+C" is pressed, the function is executed. 
    global t
    GPIO.cleanup()      
    t.cancel()      #cancel the timer


if __name__ == '__main__': # Program starting from here 
    print ('Program is starting...' )
    setup() 
    try:
        loop()  
    except KeyboardInterrupt:  
        destroy()
 
