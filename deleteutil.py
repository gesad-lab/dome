import os
import shutil
from src.text2system.config import SUFIX_ENV

def deleteOldManagedFiles():
    root_path = os.path.dirname(os.path.dirname(__file__)) #parent directory
    print('Excluding the old files...')
    for dir in os.listdir(root_path):
        full_dir_path = os.path.join(root_path, dir)
        if ((os.path.isdir(full_dir_path)) 
            and ((dir.find(SUFIX_ENV, len(dir) - len(SUFIX_ENV)) > 0) 
                 or (dir == '__pycache__'))):  
            shutil.rmtree(full_dir_path)
