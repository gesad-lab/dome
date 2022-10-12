from dome.user import User
import time
import gc
import util.delete_util as delutil

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

while True:
    print('creating the attribute ' + str(i) + '/7')
    userTest.MUP.addAttribute(currentEntity, ATT_NAMES[i-1], 'str')
    
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
        
    time.sleep(60) # Sleep for some seconds


            
#pyreverse py --output=jpg --filter-mode=ALL --all-associated