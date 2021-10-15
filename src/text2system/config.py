#bot msgs
MISUNDERSTANDING = ["""Um. I don't recognize it. Which operation do you want to do? Add, update, delete or get some information? (say 'help' for samples)"""
                    , """Sorry, but I didn't get it. Try something like 'register new sale' or 'get product information type=T-Shirt' (say 'help' for more samples)"""
                    , "Please, repeat in another way, because I didn't get it. (say 'help' for more info)"]

GREETINGS = ["Hi! You can say something like 'Add student with name=Anderson'"
             ,"Hello! Please say something like 'Get info about student with name=Anderson'"
             ,"Hello! Good see you here! Please say some data operation like 'Include student with name=Anderson, email=andersonmg@gmail.com'"
            ]

BYE = ["Ok! Thank you. See you next time!"
       ,"Thank you so much. I stand at your disposal."
       ,"Thank you! If you need save some info, please text me."
      ]

HELP = ["""I'm a bot that helps you save your information in an organized, secure, and flexible way. Say what you want to add, update, delete or only get info. \nFor example, say something like 'add a $10 value shirt purchase', 'view purchases for the current month', or 'delete my last purchase'."""
        , """I'm a bot that allows you to save your information using natural language. Like a traditional system, but more accessible and flexible. \nFor instance, to add some appointment to your calendar, say 'add meeting tomorrow with my co-workers' or 'cancel the presentation next Wednesday'."""
        ,"""I'm your bot that securely saves your information. I understand better direct sentences. \nThus let me know first what you want to do (save, read or delete some data), what type the information you want to operate (a sale, a product, a contact, an appointment, etc.), and, finally, the data itself. \nSome examples: 'add student with name=Anderson', 'delete my last purchase', 'get info about the product with name=T-Shirt'."""
        ]

CANCEL = ['No problem! The operation was canceled successfully.']

ASK_CONFIRM = ['OK to confirm current operation;\nCANCEL to cancel\n...or simply continue doing this operation ;)]'
               , "[Any time you can say 'ok' to confirm the operation, or 'cancel' to cancel the current operation]"
               ] 

ATTRIBUTE_FORMAT = ["I'll understand better if the data is in the following format:\n<<data name>> = <<data value>>\nFor example:\nage = 21"]

ATTRIBUTE_FORMAT_FIRST_ATTEMPT = lambda opr, clas: [f"Ok! We are going to {opr} a {clas}. Please, now inform the data in the following format:\n<<data name>> = <<data value>>\nFor example:\nage = 21"]

ATTRIBUTE_OK = lambda opr, clas: [f"Ok! I got it!\nWe are going to {opr} a {clas}.\nSay 'Ok' to confirm\n'Cancel' to cancel this operation\nor simply continue informing the data..."]

CREATE_OR_UPDATE_SUCCESS = ['Ok! Information saved successfully!'
                            , 'It done! Information saved. ;)'
                            , "Yes! All done. We've saved your data with security."]

MISSING_CLASS = ["Would you please inform me of the information type that you want to operate? For instance, if you are trying to save data about an appointment, say 'appointment'.\n(If you wish to cancel this operation, say 'cancel'.)"]
MULTIPLE_CLASSES = ['Please, try to inform the information type with only one word or between "...", ok?']
#config variables
MANAGED_SYSTEM_NAME = 'managedsys'
SUFIX_ENV = '_env'
SUFIX_CONFIG = '_config'
SUFIX_WEB = '_web'
WEBAPP_HOME_URL = 'http://localhost/admin'

PNL_GENERAL_THRESHOLD = 0.75

#tokens
WIT_ACCESS_KEY='PPKWS6JBWM7FMOXYIS2VW4ZFNGJ3N7ZI'