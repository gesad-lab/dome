import itertools
import json
import unittest
import util.delete_util as del_util

from dome.auxiliary.enums.intent import Intent
from dome.config import ATTRIBUTE_OK, BYE, CANCEL, DELETE_SUCCESS, GREETINGS, HELP, MISUNDERSTANDING, SAVE_SUCCESS, \
    CANCEL_WITHOUT_PENDING_INTENT
from dome.multichannelapp import MultiChannelApp
import pandas as pd


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

    def __talk(self, msg, clear_user_data=True):
        if clear_user_data:
            self.AC.clear_opr(self.user_data)
        return self.AC.app_chatbot_msg_process(msg, self.user_data)

    def __check(self, cmd_str, expected_intent, expected_class=None, expected_attributes=None, response_list=None,
                expected_where_clause=None):
        clear_user_data = expected_intent != Intent.CONFIRMATION and expected_intent != Intent.CANCELLATION
        response = self.__talk(cmd_str, clear_user_data=clear_user_data)
        response_parser = response['parser']
        processed_intent = response_parser.intent
        processed_class = response_parser.entity_class
        processed_attributes = response_parser.attributes
        processed_where_clause = response_parser.filter_attributes

        if expected_intent == Intent.READ and processed_intent == Intent.CONFIRMATION:
            # update processed_intent because the READ intent is automatically converted to CONFIRMATION
            processed_intent = response['user_data']['previous_intent']
            processed_class = response['user_data']['previous_class']
            processed_attributes = response['user_data']['previous_attributes']
        if not processed_attributes:  # if processed_attributes is None or empty
            processed_attributes = None

        self.assertEqual(expected_intent, processed_intent,
                         'intent not correct.\nprocessed_intent = ' + str(processed_intent) +
                         '\nexpected_intent = ' + str(expected_intent) +
                         '\nuser_msg: ' + cmd_str)
        self.assertEqual(expected_class, processed_class,
                         'entity class not correct.\nprocessed_class=' +
                         str(processed_class) + '\nexpected_class=' + str(expected_class) +
                         '\nuser_msg: ' + cmd_str)

        self.assertEqual(expected_attributes, processed_attributes, 'attributes not correct.' +
                         '\nprocessed_attributes=' + str(processed_attributes) +
                         '\nexpected_attributes=' + str(expected_attributes) +
                         '\nuser_msg: ' + cmd_str)
        if response_list:
            self.assertTrue(response['response_msg'] in response_list,
                            'response message not correct.\nresponse[response_msg]=' +
                            str(response['response_msg']) + '\nresponse_list=' + str(response_list))

        if expected_where_clause:
            self.assertEqual(processed_intent, Intent.UPDATE)
            self.assertEqual(processed_where_clause, expected_where_clause)

    def __check_ADD(self, entity_name, attributes=None, add_msg=None):
        if not add_msg:
            add_msg = 'add ' + entity_name
            if attributes:
                add_msg += ' with'
                for attribute_name, attribute_value in attributes.items():
                    add_msg += ' ' + attribute_name
                    add_msg += '=' + attribute_value + ","
                add_msg = add_msg[:-1]  # remove the last comma

        self.__check(add_msg, Intent.ADD, entity_name, attributes, ATTRIBUTE_OK(str(Intent.ADD), entity_name,
                                                                                attributes, None))
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
        self.__check_ADD('student', {'name': 'Anderson Martins Gomes', 'age': '20'})

    def test_add_2(self):
        self.__check_ADD('subject', {'name': 'Brazilian History', 'description': 'The history of Brazil'})

    def test_add_3(self):
        self.__check_ADD('teacher', {'name': 'Paulo Henrique', 'age': '65', 'email': 'ph@uece.br'})

    def test_add_4(self):
        # add a subject name=Math, and description is 'The best subject ever!'
        self.__check_ADD('subject', {'name': 'Math', 'description': "The best subject ever"})

    def test_add_5(self):
        self.__check_ADD('subject', {'name': 'Math', 'description': "The best subject ever!"},
                         add_msg="add subject with name=Math, description='The best subject ever!'")

    def __check_cancel(self, msg='cancel'):
        self.__check(msg, Intent.CANCELLATION, None, None, CANCEL)

    def test_cancel_1(self):
        self.__check("add student name=Anderson", Intent.ADD, "student", {'name': 'Anderson'},
                     ATTRIBUTE_OK(str(Intent.ADD), "student", {'name': 'Anderson'}, None))
        self.__check_cancel('cancel')

    def test_cancel_2(self):
        self.__check_corner_case("bla bla bla")
        self.__check(cmd_str='please, cancel', expected_intent=Intent.CANCELLATION,
                     response_list=CANCEL_WITHOUT_PENDING_INTENT)  # because the user is not in the middle of an operation

    def __check_help(self, msg='help'):
        self.__check(msg, Intent.HELP, None, None, HELP)

    def test_help_1(self):
        self.__check_help()

    def test_help_2(self):
        self.__check_help('I want to know how to use the bot')

    def test_help_3(self):
        self.__check_help('Please, help me!')

    def __check_delete(self, entity_name, delete_msg, attributes=None):
        self.__check_ADD(entity_name, attributes)
        self.__check(delete_msg, Intent.DELETE, entity_name, attributes,
                     ATTRIBUTE_OK(str(Intent.DELETE), entity_name, attributes, None))
        self.__check('ok', Intent.CONFIRMATION, None, None, DELETE_SUCCESS(1))

    def test_delete_1(self):
        self.__check_delete('student', 'delete student name is Anderson, and age is 199',
                            {'name': 'Anderson', 'age': '199'})

    def __check_read(self, msg, entity_name, attributes=None):
        self.__check(cmd_str=msg, expected_intent=Intent.READ,
                     expected_class=entity_name, expected_attributes=attributes)

    def test_read_1(self):
        self.__check_read("show all students", "student")

    def test_read_2(self):
        self.__check_read("view students", "student")

    def test_read_3(self):
        self.__check_read("fetch the students", "student")

    def test_read_4(self):
        self.__check_read("get the students", "student")

    def __check_corner_case(self, msg):
        self.__check(msg, Intent.MEANINGLESS, None, None, MISUNDERSTANDING)

    def __check_update(self, update_msg, entity_name, attributes, expected_where_clause):
        self.__check(update_msg, Intent.UPDATE, entity_name, attributes,
                     ATTRIBUTE_OK(str(Intent.UPDATE), entity_name, attributes, expected_where_clause),
                     expected_where_clause=expected_where_clause)
        self.__check('ok', Intent.CONFIRMATION, None, None, SAVE_SUCCESS)

    def test_update_01(self):
        msg = "For the students with name='Anderson', update the name to 'Anderson Martins'"
        self.__check_update(msg, 'student', {'name': 'Anderson Martins'}, {'name': 'Anderson'})

    def test_update_02(self):
        msg = 'please change student with name Paulo update age to 30'
        self.__check_update(msg, 'student', {'age': '30'}, {'name': 'Paulo'})

    def test_update_03(self):
        msg = 'for students with name Anderson, update age to 30'
        self.__check_update(msg, 'student', {'age': '30'}, {'name': 'Anderson'})

    def test_update_04(self):
        msg = 'for students, update age to 30'
        with self.assertRaises(Exception):
            self.__check_update(msg, 'student', {'age': '30'}, None)

    def test_update_05(self):
        msg = 'update students'
        self.__check(msg, Intent.UPDATE, 'student')

    def test_update_06(self):
        msg = 'Please, when students have the name equal to Anderson, update the age to 30.'
        self.__check_update(msg, 'student', {'age': '30'}, {'name': 'Anderson'})

    def test_update_07(self):
        msg = 'Update students setting the age to 42 when name is Anderson'
        self.__check_update(msg, 'student', {'age': '42'}, {'name': 'Anderson'})

    def test_update_08(self):
        msg = 'Update students set the age to 42 when name is Anderson'
        self.__check_update(msg, 'student', {'age': '42'}, {'name': 'Anderson'})

    def test_update_09(self):
        msg = 'set students with age to 42 when name is Anderson'
        self.__check_update(msg, 'student', {'age': '42'}, {'name': 'Anderson'})

    def test_update_10(self):
        msg = 'for students with name Anderson, update the age to 42'
        self.__check_update(msg, 'student', {'age': '42'}, {'name': 'Anderson'})

    def test_update_11(self):
        msg = 'Please change student with name Anderson update age to 30'
        self.__check_update(msg, 'student', {'age': '30'}, {'name': 'Anderson'})

    def test_update_12(self):
        msg = 'Please, change the student with name=\'Anderson\', updating the age to 30'
        self.__check_update(msg, 'student', {'age': '30'}, {'name': 'Anderson'})

    def test_update_13(self):
        msg = "update the age to 42, for students with name='Anderson'"
        self.__check_update(msg, 'student', {'age': '42'}, {'name': 'Anderson'})

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
        self.__check_ADD(entity_name='outcome',
                         attributes={'value': '900', 'date': 'today', 'description': 'adjusting the numbers'},
                         add_msg=msg)

    def test_corner_case_6(self):
        self.__check(cmd_str='show teachers',
                     expected_intent=Intent.READ,
                     expected_class='teacher')

    def test_corner_case_7(self):
        self.__check(cmd_str='get invoices',
                     expected_intent=Intent.READ,
                     expected_class='invoices')

    def test_corner_case_8(self):
        # 'limit = 10' is a corner case
        self.__check(cmd_str='Add a test with scope=Module X, date=01/01/2022, timeout = 100, limit=10',
                     expected_intent=Intent.ADD,
                     expected_class='test',
                     expected_attributes={'scope': 'Module X', 'date': '01/01/2022', 'timeout': '100', 'limit': '10'})

    def test_corner_case_9(self):
        # attributes names with spaces
        self.__check(cmd_str='Add a test with scope=Module Y and number = 8',
                     expected_intent=Intent.ADD,
                     expected_class='test',
                     # project specific rule. The attribute must have only one word.
                     expected_attributes={'scope': 'Module Y', 'number': '8'})

    # get students with name anderson
    def test_corner_case_10(self):
        # attributes names with spaces
        self.__check(cmd_str='get students with name anderson',
                     expected_intent=Intent.READ,
                     expected_class='student',
                     expected_attributes={'name': 'anderson'})

    def test_corner_case_11(self):
        # attributes names with spaces
        self.__check(cmd_str='show me the teachers',
                     expected_intent=Intent.READ,
                     expected_class='teacher', )

    def test_corner_case_12(self):
        # attributes names with spaces
        self.__check(cmd_str='show teachers',
                     expected_intent=Intent.READ,
                     expected_class='teacher', )

    def test_corner_case_13(self):
        # attributes names with spaces
        self.__check(cmd_str='show teacher',
                     expected_intent=Intent.READ,
                     expected_class='teacher', )

    def test_evaluation_domain(self):
        self.__check_ADD(entity_name='article', attributes={'title': 'The title', 'author': 'The author'}, )
        self.__check_update('update article with title "The title" and author "The author" '
                            'set the title to "The new title"', 'article', {'title': 'The new title'},
                            expected_where_clause={'title': 'The title', 'author': 'The author'})
        self.__check_delete(delete_msg='delete article when author="Anderson"',
                            entity_name='article',
                            attributes={'author': 'Anderson'})
        self.__check_read(msg='show me the articles',
                          entity_name='article')
        # creating other fields
        self.__check_ADD(entity_name='article', attributes={'title': 'The title', 'author': 'The author',
                                                            'abstract': 'The abstract', 'keywords': 'The keywords'})
        self.__check_update('update article with title "The title", setting the co-author as "Anderson Gomes"',
                            entity_name='article',
                            attributes={'co_author': 'Anderson Gomes'},
                            expected_where_clause={'title': 'The title'})
        self.__check_update('update article with id=1, setting the first author as "Paulo Maia"',
                            entity_name='article',
                            attributes={'first_author': 'Paulo Maia'},
                            expected_where_clause={'id': '1'})

    def test_corner_case_14(self):
        # attributes values with special chars
        self.__check_ADD(entity_name='article',
                         attributes={'title': 'The Shor\'s Quantum Algorithm'},
                         add_msg='Add an article with title="The Shor\'s Quantum Algorithm"')
        self.__check_update(update_msg='update article with title "The Shors Quantum Algorithm" '
                                       'set the title to "The new title\'s name"'
                            , entity_name='article', attributes={'title': 'The new title\'s name'},
                            expected_where_clause={'title': 'The Shors Quantum Algorithm'})

    '''
    def test_all_parser_cache(self):
        print('*** testing all parser cache')
        for row in self.AIE.get_all_considered_parser_cache():
            print('id: ', row['id'], '| intent: ', row['considered_intent'],
                  '| class: ', row['considered_class'], '| ', row['considered_attributes'], '| ', row['user_msg'])
            # set self.attributes as a dict from the string loaded from cached_parser['considered_attributes'] json
            expected_attributes = None
            if row['considered_attributes']:
                expected_attributes = json.loads(row['considered_attributes'])

            if expected_attributes:
                for key, value in expected_attributes.items():
                    expected_attributes[key] = value.lower()

            self.__check(cmd_str=row['user_msg'],
                         expected_intent=Intent(row['considered_intent']),
                         expected_class=row['considered_class'],
                         expected_attributes=expected_attributes)
    '''


if __name__ == '__main__':
    del_util.deleteOldManagedFiles()
    unittest.main()
