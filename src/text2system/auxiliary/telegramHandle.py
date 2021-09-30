import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

class TelegramHandle:
    def __init__(self, msgHandle) -> None:
        self.__TOKEN = os.getenv('TEXT2SYSTEM_TELEGRAM_TOKEN')
        #Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
        self.__logger = logging.getLogger(__name__)
        self.__PORT = int(os.environ.get('PORT', '8443'))
        self.__MSG_HANDLE = msgHandle

        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        updater = Updater(
            self.__TOKEN, use_context=True)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("help", self.help))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, self.echo))

        # log all errors
        dp.add_error_handler(self.error)

        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        
        updater.idle()


    def start(self, update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text(self.__MSG_HANDLE('Hi!', context))


    def help(self, update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text(self.__MSG_HANDLE('Help!', context))


    def echo(self, update, context):
        """Echo the user message."""
        #update.message.reply_text(update.message.text)
        update.message.reply_text(self.__MSG_HANDLE(update.message.text, context))


    def error(self, update, context):
        """Log Errors caused by Updates."""
        self.__logger.warning('Update "%s" caused error "%s"', update, context.error)


#4test
#def respondeTest(msg, context):
#    return msg + " [PROCESS]" + str(context)

#TelegramHandle(respondeTest)
