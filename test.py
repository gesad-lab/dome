import unittest

from text2system import user as user_lib
from text2system.aiengine import Intent
from text2system.config import ATTRIBUTE_OK, BYE, GREETINGS, SAVE_SUCCESS

class TestT2S(unittest.TestCase):
    #initializing some variables
    @classmethod
    def setUpClass(cls):
        cls.USER = user_lib.User.getRandomNewUser()
        cls.MUP = cls.USER.MUP
        cls.SE = cls.MUP.getSE()
        cls.AC = cls.SE.getAC()
        
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
            self.assertTrue(talk(msg)['response_msg'] in response_list)

        def talk(msg):
            return self.AC.app_chatbot_msgProcess(msg, user_data)
        
        def test_SAVE(entity_name, attList):
            #TODO: lower case bug
            attList = [x.lower() for x in attList]
            cmd_str = 'add ' + entity_name
            if len(attList) > 0:
                cmd_str += ' with'
            for i in range(0, len(attList), 2):
                cmd_str += ' ' + attList[i]
                cmd_str += '=' + attList[i+1] + ","
            
            def check(cmd_str, intent, response_list):
                response = talk(cmd_str)
                self.assertEqual(response['intent'], intent, 'intent not correct. response[intent]=' + str(response['intent']))
                self.assertEqual(response['entity_class_name'], entity_name, 'entity class not correct.\nresponse[entity_class_name]=' + 
                                 response['entity_class_name'] + '\nentity_name=' + entity_name)
                att_dict = {}
                for i in range(0, len(attList), 2):
                    att_dict[attList[i]] = attList[i+1]
                    
                if intent != Intent.CONFIRMATION:
                    self.assertEqual(response['attributes'], att_dict, 'attributes not correct.\nresponse[attributes]=' +
                                str(response['attributes']) + '\natt_list=' + str(attList))
                self.assertTrue(response['response_msg'] in response_list, 'response message not correct.\nresponse[response_msg]=' +
                                response['response_msg'] + '\nresponse_list=' + str(response_list))
                
            check(cmd_str, Intent.SAVE, ATTRIBUTE_OK(str(Intent.SAVE), entity_name))
            check('ok', Intent.CONFIRMATION, SAVE_SUCCESS)
            
        assertInDefaultResponseList('hi', GREETINGS)
        assertInDefaultResponseList('bye', BYE)
        test_SAVE('subject', ['name', 'Brazilian History', 'description', 'The history of Brazil'])
        test_SAVE('teacher', ['name', 'Paulo Henrique', 'age', '65', 'email', 'ph@uece.br'])
        test_SAVE('student', ['name', 'Anderson Martins Gomes', 'age', '20'])
        
    
if __name__ == '__main__':
    unittest.main()