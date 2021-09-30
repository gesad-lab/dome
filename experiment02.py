from text2system.src.user import User
import util.deleteutil as delutil

#deleting the old gen files
delutil.deleteOldManagedFiles()

User.getRandomNewUser().MUP.runApp_cmd()
