# -*- coding: utf-8 -*-
# dependencies:
# - telegram python bot

import json
from telegram.ext import CommandHandler, Filters, Job, MessageHandler, Updater
from .fritzbox import CheckCallList
from telegram.ext.callbackcontext import CallbackContext

# use logging when testing:
# import logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class CallInfoBot():
    PHONEBOOK_CONFIG_FILE = "bot_phonebook.cfg"
    CHECK_FRITZBOX_INTERVAL = 20  # in seconds

    def __init__(self, config_file=PHONEBOOK_CONFIG_FILE, mock_fritzbox=False):
        """
        Only works with a valid config file (yet)

        Parameters
        ----------
            config_file : str
                Path to a valid config file (see `README`)
            mock_fritzbox : boolean
                Set true to test the Telegram Bot without having a FritzBox to connect to.
        """
        self.configFile = config_file

        # to be laoded from config file!
        self.clientChatIds = set()
        self.telegramToken = ""
        self.checkFritzboxInterval = CallInfoBot.CHECK_FRITZBOX_INTERVAL

        # loading from config file
        with open(self.configFile, 'r') as stream:
            data = json.load(stream)
            # init fritzbox calllist checker
            self.ccl = CheckCallList.loadFromConfig(data, use_mock=mock_fritzbox)
            # copy config to this class
            self.config = data['bot']

            for key in self.config.keys():
                print("k", key, "v", self.config[key])
                setattr(self, key, self.config[key])
        # convert to set
        self.clientChatIds = set(self.clientChatIds)

        print("token", self.telegramToken,
              "intervall", self.checkFritzboxInterval)

        # initing the bot
        self.updater = Updater(token=self.telegramToken, use_context=True)

        # add handlers etc
        self.updater.job_queue.run_repeating(
            name='Check Fritzbox',
            callback=self.cb_check_fritzbox,
            context=self.ccl,
            interval=self.checkFritzboxInterval,
            first=0.0)

        start_handler = CommandHandler('start', self.cb_start)
        self.updater.dispatcher.add_handler(start_handler)

        stop_handler = CommandHandler('stop', self.cb_stop)
        self.updater.dispatcher.add_handler(stop_handler)

        info_handler = CommandHandler('info', self.cb_info)
        self.updater.dispatcher.add_handler(info_handler)

        self.updater.dispatcher.add_handler(MessageHandler(Filters.command, self.cb_unknown))
        self.updater.dispatcher.add_error_handler(self.cb_error)

    def saveToFile(self, filename):
        data = self.getConfig()

        with open(filename, 'w') as stream:
            json.dump(data, stream, indent=2)

    def getConfig(self):
        # json cant do sets, so convert to list
        self.config['clientChatIds'] = list(self.clientChatIds)
        data = self.ccl.getConfig()
        data["bot"] = self.config
        return data

    def startPolling(self):
        self.updater.start_polling()

    def stopPolling(self):
        self.updater.stop()

    def cb_error(self, arg1):
        print('An error occured', arg1)

    def cb_check_fritzbox(self, context: CallbackContext):
        """
        Checks the FritzBox for new calls and notifies all subscribers.
        """
        bot = context.bot
        ccl: CheckCallList = context.job.context  # get phonebook.CheckCallList
        newCalls = list(ccl.checkForNewCalls())
        if len(newCalls) > 0:
            # save changes
            self.saveToFile(self.configFile)
            # create message to send out
            msgtext = "#################\n"
            msgtext += "**{0} new call{1}:**\n\n".format(len(newCalls), '' if len(newCalls) == 1 else 's')  # plural s :)
            # pylint: disable=E1101
            msgtext += '\n\n'.join(map(lambda x: x.toMd(), newCalls))  # calls -> text
            msgtext += "\n#################"
            # spread to all receivers
            for chatId in self.clientChatIds:
                bot.sendMessage(chat_id=chatId, text=msgtext, parse_mode='Markdown')

    def cb_start(self, update, context):
        """
        Telegram Command to start a subscription.
        A subscriber will be notified of all new calls to the FritzBox since the subscription took place.
        """
        chat_id = update.message.chat_id

        if chat_id in self.clientChatIds:
            update.message.reply_text('You are already subscribed.')
            return

        print(f"Subscribing chat_id '{chat_id}'")
        self.clientChatIds.add(chat_id)
        update.message.reply_text("You have successfully subscribed.")
        self.saveToFile(self.configFile)

    def cb_stop(self, update, context):
        """
        Telegram Command to end a subscription. The unsubscribed will
        no longer be notified of new calls to the FritzBox.
        """

        print(f"Unsubscribing chat_id '{update.message.chat_id}'")
        try:
            self.clientChatIds.remove(update.message.chat_id)
            answer = "You sucessfully unsubscribed."
            self.saveToFile(self.configFile)
        except KeyError:
            answer = "You are not subscribed."

        update.message.reply_text(answer)

    def cb_unknown(self, update, context):
        message_text = update.message.text
        print(f"Unknown command '{message_text}'")
        update.message.reply_text(f"Unknown command '{message_text}'")

    def cb_info(self, update, context):
        chats_as_strings = map(lambda x: f"`{x}`", self.clientChatIds)
        chats = "\n".join(chats_as_strings)
        msgtext = "The following chats are subscribed: \n" + chats
        update.message.reply_text(msgtext, parse_mode='Markdown')
