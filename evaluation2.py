import datetime
import json
import os
import unittest

import pandas as pd
import unicodedata

import util.delete_util as del_util
from dome.autonomouscontroller import AutonomousController
from dome.auxiliary.enums.intent import Intent
from dome.infrastructurecontroller import InterfaceController
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

    def __check_old(self, cmd_str, expected_intent, expected_class=None, expected_attributes=None, response_list=None,
                expected_where_clause=None):
        clear_user_data = expected_intent != Intent.CONFIRMATION and expected_intent != Intent.CANCELLATION
        response = self.__talk(cmd_str, clear_user_data=clear_user_data)
        response_parser = response['parser']

        processed_intent = Intent.MEANINGLESS
        processed_class = None
        processed_attributes = None
        processed_where_clause = None

        if response_parser:
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

        def normalize_str(s):
            s = str(s)
            if s:
                s = s.lower()
                s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8')
            return s
        expected_class = normalize_str(expected_class)
        processed_class = normalize_str(processed_class)
        self.assertEqual(expected_class, processed_class,
                         'entity class not correct.\nprocessed_class=' +
                         processed_class + '\nexpected_class=' + expected_class +
                         '\nuser_msg: ' + cmd_str)

        expected_attributes = normalize_str(expected_attributes)
        processed_attributes = normalize_str(processed_attributes)
        self.assertEqual(expected_attributes, processed_attributes, 'attributes not correct.' +
                         '\nprocessed_attributes=' + processed_attributes +
                         '\nexpected_attributes=' + expected_attributes +
                         '\nuser_msg: ' + cmd_str)
        if response_list:
            self.assertTrue(response['response_msg'] in response_list,
                            'response message not correct.\nresponse[response_msg]=' +
                            str(response['response_msg']) + '\nresponse_list=' + str(response_list))

        if expected_where_clause:
            self.assertEqual(processed_intent, Intent.UPDATE)
            processed_where_clause = normalize_str(processed_where_clause)
            expected_where_clause = normalize_str(expected_where_clause)
            self.assertEqual(processed_where_clause, expected_where_clause, 'where clause not correct.' +
                                                                           '\nprocessed_where_clause=' + processed_where_clause +
                                                                           '\nexpected_where_clause=' + expected_where_clause +
                                                                           '\nuser_msg: ' + cmd_str)

    def __check(self, cmd_str, expected_intent, expected_class=None, expected_attributes=None, response_list=None,
                expected_where_clause=None):
        self.__check_old(cmd_str, expected_intent, expected_class, expected_attributes, response_list,
                    expected_where_clause)

    def test_evaluation_2(self):
        url = 'https://drive.google.com/file/d/1IMckKMW5jZDFPXDdv1kJFw0ye2MEiIG7/view?usp=sharing'
        url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
        df = pd.read_csv(url)
        df['evaluation1_error_type'] = None  # None | 'assertion' | 'general'
        df['evaluation2_error_type'] = None  # None | 'assertion' | 'general'
        df['evaluation2_error_description'] = None

        number_of_errors = 0
        number_of_errors_eval1 = 0
        number_of_assertion_errors = 0
        for index, row in df.iterrows():
            if index + 1 < 0:
                continue
            user_msg = row['user_msg']
            print('id:', index + 1, '| user_msg:', user_msg)
            expected_intent = Intent(row['expected_intent'])
            expected_class = None
            if isinstance(row['expected_class'], str):
                expected_class = row['expected_class']

            # transform the string loaded from cached_parser['expected_attributes'] json into a list of tuples
            expected_attributes = None
            if row['expected_attributes'] and isinstance(row['expected_attributes'], str):
                expected_attributes = json.loads(str(row['expected_attributes']).lower())

            # transform the string loaded from cached_parser['expected_filter_attributes'] json into a list of tuples
            expected_filter_attributes = None
            if row['expected_filter_attributes'] and isinstance(row['expected_filter_attributes'], str):
                expected_filter_attributes = json.loads(str(row['expected_filter_attributes']).lower())

            # check the first evaluation
            if (str(row['processed_intent']) != str(row['expected_intent'])
                    or str(row['processed_class']) != str(row['expected_class'])
                    or str(row['processed_attributes']) != str(row['expected_attributes'])
                    or str(row['processed_filter_attributes']) != str(row['expected_filter_attributes'])):
                df.loc[index, ['evaluation1_error_type']] = 'assertion'
                number_of_errors_eval1 += 1

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
                number_of_assertion_errors += 1
                df.loc[index, ['evaluation2_error_type']] = 'assertion'
                df.loc[index, ['evaluation2_error_description']] = str(e)
            except Exception as e:
                print('*** ERROR:', e)
                number_of_errors += 1
                df.loc[index, ['evaluation2_error_type']] = 'general'
                df.loc[index, ['evaluation2_error_description']] = str(e)

        print('\n***evaluation 1')
        print('number of errors:', number_of_errors_eval1)
        print('hit hate:', (len(df) - number_of_errors_eval1) / len(df))

        print('\n***evaluation 2')
        print('number of assertion errors:', number_of_assertion_errors)
        print('number of errors:', number_of_errors)
        print('number of tests:', len(df))
        print('hit hate:', (len(df) - number_of_errors) / len(df))

        # saving the dataframe in a csv file
        # generating a unique file name using the current date and time
        logs_dir = os.path.dirname(os.path.abspath(__file__)) + '\\logs'
        dt_string = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        file_name = logs_dir + '\\evaluation2_' + dt_string + '.csv'
        print('Logs saved in:', file_name)
        df.to_csv(file_name, index=False)


if __name__ == '__main__':
    # del_util.deleteOldManagedFiles()
    # ic = InterfaceController()
    # ic.migrateModel()
    unittest.main()
