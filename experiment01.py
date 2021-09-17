from baseclasses.user import User
import time
import gc
import util.deleteutil as delutil

userTest = None
currentEntity = None
ATT_NAMES = ['name', 'middle_name', 'surname', 'email', 'home_address', "mother_name", "father_name"]

def boot():
    #4tests
    global userTest 
    global currentEntity
    userTest = User.getRandomNewUser()
    currentEntity = userTest.MUP.addEntity('student') #only one entity in this version

#deleting the old gen files
delutil.deleteOldManagedFiles()

boot()
i = 1

userTest.MUP.runApp_web()
exit()

while True:
    print('creating the attribute ' + str(i) + '/10')
    userTest.MUP.addAttribute(currentEntity, ATT_NAMES[i-1], 'str')
    time.sleep(30) # Sleep for some seconds
    if i==len(ATT_NAMES): #len(ATT_NAMES) is the max number of attributes for this test
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