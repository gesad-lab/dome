import json
import unittest

import pandas as pd

import util.delete_util as del_util
from dome.auxiliary.enums.intent import Intent
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

    def test_evaluation_2(self):
        url = 'https://drive.google.com/file/d/1TcJwceDj_Y4vLc66OX7qqi7FSf7Tt8pu/view?usp=sharing'
        url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
        df = pd.read_csv(url)
        number_of_errors = 0
        for index, row in df.iterrows():
            user_msg = row['user_msg']
            print('id:', index, '| user_msg:', user_msg)
            expected_intent = Intent(row['expected_intent'])
            expected_class = None
            if isinstance(row['expected_class'], str):
                expected_class = row['expected_class']

            # transform the string loaded from cached_parser['expected_attributes'] json into a list of tuples
            expected_attributes = None
            if row['expected_attributes'] and isinstance(row['expected_attributes'], str):
                expected_attributes = json.loads(str(row['expected_attributes']).lower(), )

            # transform the string loaded from cached_parser['expected_filter_attributes'] json into a list of tuples
            expected_filter_attributes = None
            if row['expected_filter_attributes'] and isinstance(row['expected_filter_attributes'], str):
                expected_filter_attributes = json.loads(str(row['expected_filter_attributes']).lower())

            # catch the exception and account the error
            try:
                self.__check(cmd_str=str(row['user_msg']).lower(),
                             expected_intent=expected_intent,
                             expected_class=expected_class,
                             expected_attributes=expected_attributes,
                             expected_where_clause=expected_filter_attributes)
                print('**** OK. Test passed.')
            except AssertionError as e:
                print('*** ERROR:', e)
                number_of_errors += 1

        print('number of errors:', number_of_errors)
        print('number of tests:', len(df))
        print('hit hate:', (len(df) - number_of_errors) / len(df))


if __name__ == '__main__':
    del_util.deleteOldManagedFiles()
    unittest.main()
