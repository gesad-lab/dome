from baseclasses.user import User
import time
import os
import gc
import deleteutil

userTest = None
currentEntity = None

def boot():
    #4tests
    global userTest 
    global currentEntity
    userTest = User(os.environ['DJANGO_SUPERUSER_USERNAME'], os.environ['DJANGO_SUPERUSER_PASSWORD'])
    currentEntity = userTest.MUP.addEntity('entity01') #only one entity in this version

#deleting the old gen files
deleteutil.deleteOldManagedFiles()
    
boot()
i = 1

while True:
    print('creating the attribute ' + str(i) + '/10')
    userTest.MUP.addAttribute(currentEntity, 'att_'+str(i), 'str')
    time.sleep(30) # Sleep for some seconds
    if i==10: #10 is the max number of attributes for this test
        #memory managment
        del userTest
        del currentEntity
        gc.collect()
        #init all and restart
        boot()
        i = 1
    else:
        i += 1 #increment the number of attributes

            
#pyreverse baseclasses.py --output=jpg --filter-mode=ALL --all-associated