import unittest

from text2system import user as user_lib
from text2system.config import BYE, GREETINGS

class TestT2S(unittest.TestCase):
    #initializing some variables
    def setUp(self):
        self.USER = user_lib.User.getRandomNewUser()
        self.MUP = self.USER.MUP
        self.SE = self.MUP.getSE()
        self.AC = self.SE.getAC()
        
    #testing the creation of the arquitecture elements
    def test_arquitecture_elements(self):
        self.assertIsNotNone(self.USER)
        self.assertIsNotNone(self.MUP) 
        self.assertIsNotNone(self.SE) 
        self.assertIsNotNone(self.AC)

    def test_AC_app_chatbot_msgProcess(self):
        #simulating a user connection
        user_data = {}
        user_data['chat_id'] = '12345'
        user_data['debug_mode'] = False
        
        def assertInDefaultResponseList(msg, response_list):
            self.assertTrue(self.AC.app_chatbot_msgProcess(msg, user_data)['response_msg'] in response_list)
            
        assertInDefaultResponseList('hi', GREETINGS)
        assertInDefaultResponseList('bye', BYE)
    
if __name__ == '__main__':
    unittest.main()