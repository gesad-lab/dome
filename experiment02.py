from wit import Wit
from config import WIT_ACCESS_KEY

client = Wit(access_token=WIT_ACCESS_KEY)
client.interactive()
