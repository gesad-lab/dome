import json

# from transformers import T5Tokenizer, T5ForConditionalGeneration

from dome.auxiliary.enums.intent import Intent
from dome.config import HUGGINGFACE_TOKEN
from dome.multichannelapp import MultiChannelApp

version = "xl"  # [small, base, large, xl, xxl]
'''
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-" + version)
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-" + version)  # .to("cuda")

def generate(input_text):
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids  # .to("cuda")
    output = model.generate(input_ids, max_length=100)
    return tokenizer.decode(output[0], skip_special_tokens=True)
'''

import requests

# https://huggingface.co/google/flan-t5-xxl
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-" + version
headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}


def generate(input_text):
    payload = {"inputs": input_text, "options": {"use_cache": True, "wait_for_model": True}}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def prompt(question, fact, options, log=False):
    input_text = '-QUESTION: %s-CONTEXT: %s-OPTIONS: %s' % (question + '\n', fact + '\n', options)
    if log:
        print('PROMPT -------------------')
        print(input_text)
        print('--------------------------')
    return generate(input_text)


def make_any_sense(user_msg):
    question = "Does the user message make any sense?"
    fact = "The user message is: " + user_msg + \
           '\nA user sent this message to a chatbot.' + \
           '\nThe chatbot is trying to understand the user\'s intention.' + \
           '\nIt is trying to understand if the user message makes any sense.'
    options = "Yes, No"
    return prompt(question, fact, options)


def make_any_sense(user_msg):
    question = "Does the user message make any sense?"
    fact = "The user message is: " + user_msg + \
           '\nA user sent this message to a chatbot.' + \
           '\nThe chatbot is trying to understand the user\'s intention.' + \
           '\nIt is trying to understand if the user message makes any sense.'
    options = "Yes, No"
    return prompt(question, fact, options)


def is_CRUD_operation(user_msg):
    question = "Is the user message intention refers to a CRUD operation?"
    fact = "The user message is: " + user_msg + \
           '\nA user sent this message to a chatbot.' + \
           '\nThe chatbot is trying to understand the user\'s intention.' + \
           '\nIt is trying to understand if the user message refers to a CRUD operation.' + \
           '\nCRUD refers to the four basic operations a software application should be able to perform: ' \
           'Create, Read, Update, and Delete.'
    options = "Yes, No"
    return prompt(question, fact, options)


def get_intent(user_msg):
    question = "What is the user's message intention?"
    fact = "The user message is: " + user_msg + \
           '\nA user sent this message to a chatbot.' + \
           '\nThe chatbot is trying to understand the user\'s intention.' + \
           '\nIt is trying to classify the message according to the intention of the user.'
    options = ", ".join([intent.name for intent in Intent])
    return prompt(question, fact, options)


user_cmds = ["Hi!",
             "Gfjsafjksaf1112",
             "Add a test with scope=Module X, date=01/01/2022, timeout = 100, limit = 10",
             'bla bla bla 123',
             'bye bye',
             'thank you!',
             ]
# user_cmds = []
for cmd in user_cmds:
    print(cmd)
    print('[Make sense? ' + str(make_any_sense(cmd)) + ']')
    print('[Intent: ' + str(get_intent(cmd)) + ']')
    print('[CRUD? ' + str(is_CRUD_operation(cmd)) + ']')
    print('*******************')

exit()

MUP = MultiChannelApp(run_telegram=False)
SE = MUP.get_SE()
AC = SE.get_AC()
AIE = AC.get_AIE()


def __check(user_msg, expected_intent, expected_class, expected_attributes):
    make_sense = make_any_sense(user_msg)
    print('[Make sense? ' + str(make_sense) + ']')

    processed_intent = get_intent(user_msg)
    print('[processed Intent: ' + str(processed_intent) + ']')

    is_CRUD = is_CRUD_operation(user_msg)
    print('[CRUD? ' + str(is_CRUD) + ']')
    print('*******************')


print('*** testing all parser cache')
testing_data = AIE.get_all_considered_parser_cache()
for row in testing_data:
    print('id: ', row['id'], '| intent: ', row['considered_intent'],
          '| class: ', row['considered_class'], '| ', row['considered_attributes'], '| ', row['user_msg'])
    # set self.attributes as a dict from the string loaded from cached_parser['considered_attributes'] json
    expected_atts = None
    if row['considered_attributes']:
        expected_atts = json.loads(row['considered_attributes'])

    __check(user_msg=row['user_msg'], expected_intent=Intent(row['considered_intent']),
            expected_class=row['considered_class'],
            expected_attributes=expected_atts)




