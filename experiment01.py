from baseclasses import *
import time
import os

userTest = None
currentEntity = None

def boot():
    #4tests
    global userTest 
    global currentEntity
    userTest = User(os.environ['DJANGO_SUPERUSER_USERNAME'], os.environ['DJANGO_SUPERUSER_PASSWORD'])
    currentEntity = userTest.MUP.currentEntity #only one entity in this version

boot()
i = 1
while True:
    print(userTest.MUP.addAttribute(currentEntity, 'att_'+str(i), 'str'))
    time.sleep(15) # Sleep for some seconds
    if i==10: #10 is the max number of attributes for this test
        #init all and restart
        boot()
        i = 1
    else:
        i += 1 #increment the number of attributes

            
