import deleteutil as delutil
import src.text2system.user as user

#deleting the old gen files
#delutil.deleteOldManagedFiles()

user.User.getRandomNewUser().MUP.runApp_telegram()
