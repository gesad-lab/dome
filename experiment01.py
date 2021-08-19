from baseclasses import *
import time

#4tests
sysTest = MultChannelApp()
while True:
    print(sysTest.addAttribute('att1', 'string', 'entity1'))
    time.sleep(3) # Sleep for 3 seconds