from baseclasses.user import User
import util.deleteutil as delutil

#deleting the old gen files
delutil.deleteOldManagedFiles()

userTest = User.getRandomNewUser()
userTest.MUP.interactive()
