import unittest

from dome.auxiliary.enums.intent import Intent
from dome.config import ATTRIBUTE_OK, BYE, CANCEL, DELETE_SUCCESS, GREETINGS, HELP, MISUNDERSTANDING, SAVE_SUCCESS
from dome.multichannelapp import MultiChannelApp


class TestT2S(unittest.TestCase):
    # initializing some variables
    @classmethod
    def setUpClass(cls):
        cls.MUP = MultiChannelApp(run_telegram=False)
        cls.SE = cls.MUP.get_SE()
        cls.AC = cls.SE.get_AC()
        cls.AIE = cls.AC.get_AIE()
        # simulating a user connection
        cls.user_data = {'chat_id': '12345', 'debug_mode': False}

    def __assertInDefaultResponseList(self, msg, response_list):
        self.assertTrue(self.__talk(msg)['response_msg'] in response_list)

    def __talk(self, msg):
        return self.AC.app_chatbot_msg_process(msg, self.user_data)

    def __check(self, cmd_str, expected_intent, expected_class=None, expected_attributes=None, response_list=None,
                test_only_intent_and_entity=False):
        response = self.__talk(cmd_str)
        response_parser = response['parser']
        processed_intent = response_parser.intent
        processed_class = response_parser.entity_class
        if expected_intent == Intent.READ and processed_intent == Intent.CONFIRMATION:
            # update processed_intent because the READ intent is automatically converted to CONFIRMATION
            processed_intent = response['user_data']['previous_intent']
            processed_class = response['user_data']['previous_class']

        self.assertEqual(expected_intent, processed_intent,
                         'intent not correct.\nprocessed_intent = ' + str(processed_intent) +
                         '\nexpected_intent = ' + str(expected_intent) +
                         '\nuser_msg: ' + cmd_str)
        self.assertEqual(expected_class, processed_class,
                         'entity class not correct.\nprocessed_class=' +
                         str(processed_class) + '\nexpected_class=' + str(expected_class) +
                         '\nuser_msg: ' + cmd_str)

        if test_only_intent_and_entity:
            return
        # else: test attributes
        processed_attributes = response_parser.attributes
        if not processed_attributes:  # if processed_attributes is None or empty
            processed_attributes = None

        self.assertEqual(expected_attributes, processed_attributes, 'attributes not correct.' +
                         '\nprocessed_attributes=' + str(processed_attributes) +
                         '\nexpected_attributes=' + str(expected_attributes) +
                         '\nuser_msg: ' + cmd_str)
        if response_list:
            self.assertTrue(response['response_msg'] in response_list,
                            'response message not correct.\nresponse[response_msg]=' +
                            str(response['response_msg']) + '\nresponse_list=' + str(response_list))

    def __check_SAVE(self, entity_name, att_list=None, cmd_str=None):
        if not cmd_str:
            cmd_str = 'add ' + entity_name
            if att_list:
                cmd_str += ' with'
                for i in range(0, len(att_list), 2):
                    cmd_str += ' ' + att_list[i]
                    cmd_str += '=' + att_list[i + 1] + ","

        # TODO: lower case bug
        if att_list:
            att_list = [x.lower() for x in att_list]
        cmd_str = cmd_str.lower()

        self.__check(cmd_str, Intent.SAVE, entity_name, att_list, ATTRIBUTE_OK(str(Intent.SAVE), entity_name),
                     test_only_intent_and_entity=att_list is None)
        self.__check('ok', Intent.CONFIRMATION, None, None, SAVE_SUCCESS)

    # testing the creation of the arquitecture elements
    def test_architecture_elements(self):
        self.assertIsNotNone(self.MUP)
        self.assertIsNotNone(self.SE)
        self.assertIsNotNone(self.AC)
        self.assertIsNotNone(self.AIE)

    # testing the 'hi' msg
    def __check_greetings(self, msg):
        self.__assertInDefaultResponseList(msg, GREETINGS)

    def test_greetings_1(self):
        self.__check_greetings('hi')

    def test_greetings_2(self):
        self.__check_greetings('hello! Nice to meet you!')

    def test_greetings_3(self):
        self.__check_greetings('good morning!')

    # testing the 'bye' msg
    def ___check_bye(self, msg):
        self.__assertInDefaultResponseList(msg, BYE)

    def test_bye_1(self):
        self.___check_bye('bye')

    def test_bye_2(self):
        self.___check_bye('I wanna say bye!')

    def test_bye_3(self):
        self.___check_bye('ok. bye bye!')

    # testing the 'add' intent
    def test_add_1(self):
        self.__check_SAVE('student', ['name', 'Anderson Martins Gomes', 'age', '20'])

    def test_add_2(self):
        self.__check_SAVE('subject', ['name', 'Brazilian History', 'description', 'The history of Brazil'])

    def test_add_3(self):
        self.__check_SAVE('teacher', ['name', 'Paulo Henrique', 'age', '65', 'email', 'ph@uece.br'])

    def test_add_4(self):
        # save a subject name=Math, and description is 'The best subject ever!'
        self.__check_SAVE('subject', ['name', 'Math', 'description', "The best subject ever"])

    def test_add_5(self):
        self.__check_SAVE('subject', ['name', 'Math', 'description', "The best subject ever!"],
                          cmd_str="add subject with name=Math, description='The best subject ever!'")

    def __check_cancel(self, msg='cancel'):
        self.__check(msg, Intent.CANCELLATION, None, None, CANCEL)

    def test_cancel_1(self):
        self.__check("add student name=Anderson", Intent.SAVE, "student", ['name', 'Anderson'],
                     ATTRIBUTE_OK(str(Intent.SAVE), "student"))
        self.__check_cancel('cancel')

    def test_cancel_2(self):
        self.__check_corner_case("bla bla bla")
        self.__check(cmd_str='please, cancel', expected_intent=Intent.CANCELLATION,
                     response_list=MISUNDERSTANDING)  # because the user is not in the middle of an operation

    def __check_help(self, msg='help'):
        self.__check(msg, Intent.HELP, None, None, HELP)

    def test_help_1(self):
        self.__check_help()

    def test_help_2(self):
        self.__check_help('I want to know how to use the bot')

    def test_help_3(self):
        self.__check_help('Please, help me!')

    def __check_delete(self, entity_name, delete_msg, att_list=None):
        self.__check_SAVE(entity_name, att_list)
        self.__check(delete_msg, Intent.DELETE, entity_name, att_list,
                     ATTRIBUTE_OK(str(Intent.DELETE), entity_name))
        self.__check('ok', Intent.CONFIRMATION, None, None, DELETE_SUCCESS(1))

    def test_delete_1(self):
        self.__check_delete('student', 'delete student name is Anderson, and age is 199',
                            ['name', 'Anderson', 'age', '199'])

    def __check_read(self, msg):
        self.__check(msg, Intent.CONFIRMATION)

    def test_read_1(self):
        self.__check_read("show all students")

    def test_read_2(self):
        self.__check_read("view students")

    def test_read_3(self):
        self.__check_read("fetch the students")

    def test_read_4(self):
        self.__check_read("get the students")

    def __check_corner_case(self, msg):
        self.__check(msg, Intent.MEANINGLESS, None, None, MISUNDERSTANDING)

    def test_corner_case_1(self):
        self.__check_corner_case("bla bla bla")

    def test_corner_case_2(self):
        self.__check_corner_case("123456789133 $%^&*()")

    def test_corner_case_3(self):
        self.__check_corner_case("Please, the god is god!")

    def test_corner_case_4(self):
        self.__check_corner_case("crazy message 12334")

    def test_corner_case_5(self):
        msg = 'Include outcome value 900, date is today, and description is "adjusting the numbers"'
        self.__check_SAVE(entity_name='outcome',
                          att_list=['value', '900', 'date', 'today', 'description', 'adjusting the numbers'],
                          cmd_str=msg)

    def test_corner_case_6(self):
        self.__check(cmd_str='show teachers',
                     expected_intent=Intent.READ,
                     expected_class='teacher')

    def test_corner_case_7(self):
        self.__check(cmd_str='get invoices',
                     expected_intent=Intent.READ,
                     expected_class='invoice')

    def test_all_parser_cache(self):
        print('*** testing all parser cache')
        for row in self.AIE.get_all_considered_parser_cache():
            print('id: ', row['id'], '| intent: ', row['considered_intent'],
                  '| class: ', row['considered_class'], '| ', row['user_msg'], )
            self.__check(cmd_str=row['user_msg'],
                         expected_intent=Intent(row['considered_intent']),
                         expected_class=row['considered_class'],
                         test_only_intent_and_entity=True)
            self.AC.clear_opr(self.user_data)


if __name__ == '__main__':
    unittest.main()
