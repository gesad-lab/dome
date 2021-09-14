from baseclasses import *
import time
import os
import shutil
import gc

userTest = None
currentEntity = None

def boot():
    #4tests
    global userTest 
    global currentEntity
    userTest = User(os.environ['DJANGO_SUPERUSER_USERNAME'], os.environ['DJANGO_SUPERUSER_PASSWORD'])
    currentEntity = userTest.MUP.currentEntity #only one entity in this version

#deleting the old gen files
root_path = os.path.dirname(__file__)
print('Excluding the old files...')
for dir in os.listdir(root_path):
    full_dir_path = os.path.join(root_path, dir)
    if os.path.isdir(full_dir_path) and (dir != '.git'): 
        shutil.rmtree(full_dir_path)
    
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

            
