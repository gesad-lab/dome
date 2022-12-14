import util.delete_util as delutil
from dome import user as user

# deleting the old gen files
# delutil.deleteOldManagedFiles()

user.User.get_random_new_user().MUP.runApp_telegram()
