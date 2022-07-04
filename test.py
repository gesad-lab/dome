import unittest

from text2system import user as user_lib
from text2system.auxiliary.enums.intent import Intent
from text2system.config import ATTRIBUTE_OK, BYE, CANCEL, DELETE_SUCCESS, GREETINGS, HELP, MISUNDERSTANDING, SAVE_SUCCESS

class TestT2S(unittest.TestCase):
    #initializing some variables
    @classmethod
    def setUpClass(cls):
        cls.USER = user_lib.User.getRandomNewUser()
        cls.MUP = cls.USER.MUP
        cls.SE = cls.MUP.getSE()
        cls.AC = cls.SE.getAC()
        #simulating a user connection
        cls.user_data = {}
        cls.user_data['chat_id'] = '12345'
        cls.user_data['debug_mode'] = False
        
    def __assertInDefaultResponseList(self, msg, response_list):
        self.assertTrue(self.__talk(msg)['response_msg'] in response_list)

    def __talk(self, msg):
        return self.AC.app_chatbot_msgProcess(msg, self.user_data)

    def __check(self, cmd_str, intent, entity_name=None, attList=None, response_list=None):
        response = self.__talk(cmd_str)
        response_parser = response['parser']
        self.assertEqual(response_parser.intent, intent, 'intent not correct. response[intent]=' + str(response_parser.intent))
        self.assertEqual(response_parser.entity_class, entity_name, 'entity class not correct.\nresponse[entity_class_name]=' + 
                            str(response_parser.entity_class) + '\nentity_name=' + str(entity_name))
        if response_parser.attributes and len(response_parser.attributes)==0:
            response_parser.attributes = None
        self.assertEqual(response_parser.attributes, attList, 'attributes not correct.\nresponse[attributes]=' +
                    str(response_parser.attributes) + '\natt_list=' + str(attList))
        if response_list:    
            self.assertTrue(response['response_msg'] in response_list, 'response message not correct.\nresponse[response_msg]=' +
                            str(response['response_msg']) + '\nresponse_list=' + str(response_list))
    
    def __test_SAVE(self, entity_name, attList, cmd_str=None):
        if not cmd_str:
            cmd_str = 'add ' + entity_name
            if len(attList) > 0:
                cmd_str += ' with'
            for i in range(0, len(attList), 2):
                cmd_str += ' ' + attList[i]
                cmd_str += '=' + attList[i+1] + ","
        
        #TODO: lower case bug
        attList = [x.lower() for x in attList]
        cmd_str = cmd_str.lower()
        
        self.__check(cmd_str, Intent.SAVE, entity_name , attList, ATTRIBUTE_OK(str(Intent.SAVE), entity_name))
        self.__check('ok', Intent.CONFIRMATION, None , None, SAVE_SUCCESS)
            
    #testing the creation of the arquitecture elements
    def test_arquitecture_elements(self):
        self.assertIsNotNone(self.USER)
        self.assertIsNotNone(self.MUP) 
        self.assertIsNotNone(self.SE) 
        self.assertIsNotNone(self.AC)
    
    #testing the 'hi' msg
    def test_greetings(self):
        self.__assertInDefaultResponseList('hi', GREETINGS)
        self.__assertInDefaultResponseList('hello! Nice to meet you!', GREETINGS)
        
    #testing the 'bye' msg
    def test_bye(self):
        self.__assertInDefaultResponseList('bye', BYE)
        self.__assertInDefaultResponseList('I wanna say bye!', BYE)
        
    #testing the 'add' intent
    def test_add_intent(self):
        self.__test_SAVE('student', ['name', 'Anderson Martins Gomes', 'age', '20'])
        self.__test_SAVE('subject', ['name', 'Brazilian History', 'description', 'The history of Brazil'])
        self.__test_SAVE('teacher', ['name', 'Paulo Henrique', 'age', '65', 'email', 'ph@uece.br'])
        #save a subject name=Math, and description is 'The best subject ever!'
        self.__test_SAVE('subject', ['name', 'Math', 'description', "The best subject ever"])
        #TODO: solve the "'" problem
        #self.__test_SAVE('subject', ['name', 'Math', 'description', "The best subject ever!"], 
        #                 cmd_str="add subject with name=Math, description='The best subject ever!'")
    
    def test_cancel_intent(self):
        self.__check("add student name=Anderson", Intent.SAVE, "student" , ['name', 'Anderson'], ATTRIBUTE_OK(str(Intent.SAVE), "student"))
        self.__check('cancel', Intent.CANCELATION, None , None, CANCEL)
        
    def test_help_intent(self):
        self.__check("help", Intent.HELP, None , None, HELP)
    
    def test_delete_intent(self):
        self.__test_SAVE('student', ['name', 'Anderson', 'age', '199'])
        self.__check("delete student name is Anderson, and age is 199", Intent.DELETE, "student" , ['name', 'Anderson', 'age', '199'],
                     ATTRIBUTE_OK(str(Intent.DELETE), "student"))
        self.__check('ok', Intent.CONFIRMATION, None, None, DELETE_SUCCESS(1))

    def test_read_intent(self):
        #TODO: fix the bug regards the intent type and the entity class
        self.__check("show all students", Intent.CONFIRMATION) 
        
    def test_corner_cases(self):
        def check_corner_case(msg):
            self.__check(msg, Intent.UNKNOWN, None, None, MISUNDERSTANDING) 
        check_corner_case("bla bla bla")
        check_corner_case("123456789133 $%^&*()")
        check_corner_case("Please, the god is god!")
        
if __name__ == '__main__':
    unittest.main()