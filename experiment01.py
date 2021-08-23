from baseclasses import *
import time

#4tests
sysTest = MultChannelApp()
i = 1
while True:
    print(sysTest.addAttribute(sysTest.currentEntity, 'att_'+str(i), 'str'))
    time.sleep(15) # Sleep for some seconds
    i += 1