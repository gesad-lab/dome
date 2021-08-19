from baseclasses import *
import time

#4tests
sysTest = MultChannelApp()
i = 1
while True:
    print(sysTest.addAttribute(sysTest.currentEntity, 'att_'+str(i), 'string'))
    time.sleep(3) # Sleep for 3 seconds
    i += 1