# -*- coding: utf-8 -*-
# dependencies:
# - telegram python bot

import json
from telegram.ext import Updater, CommandHandler, Filters, Job
from .fritzbox import CheckCallList


# use logging when testing:
# import logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

class CallInfoBot():
    PHONEBOOK_CONFIG_FILE = "bot_phonebook.cfg"
    CHECK_FRITZBOX_INTERVAL = 20 # in seconds


    def __init__(self, configFile=PHONEBOOK_CONFIG_FILE):
        """ only works with a valid config file (yet) """
        self.configFile = configFile

        # to be laoded from config file!
        self.clientChatIds = set()
        self.telegramToken = ""
        self.checkFritzboxInterval = CallInfoBot.CHECK_FRITZBOX_INTERVAL

        # loading from config file
        with open(self.configFile, 'r') as stream:
            data = json.load(stream)
            # init fritzbox calllist checker
            self.ccl = CheckCallList.loadFromConfig(data)
            # copy config to this class
            self.config = data['bot']
            # If config is to be manually defined:
            # self.config = {'checkFritzboxInterval' = checkFritzboxInterval,
            #                'telegramToken' = telegramToken,
            #                'clientChatIds' = list(self.clientChatIds)}
            for key in self.config.keys():
                print("k", key, "v", self.config[key])
                setattr(self, key, self.config[key])
        # convert to set
        self.clientChatIds = set(self.clientChatIds)

        print("token", self.telegramToken,
              "intervall", self.checkFritzboxInterval)

        # initing the bot
        self.updater = Updater(token=self.telegramToken)

        # add handlers etc
        job_minute = Job(self.cb_minute, self.checkFritzboxInterval, repeat=True, context=self.ccl)
        self.updater.job_queue.put(job_minute, next_t=0.0)

        start_handler = CommandHandler('start', self.cb_start)
        self.updater.dispatcher.add_handler(start_handler)

        stop_handler = CommandHandler('stop', self.cb_stop)
        self.updater.dispatcher.add_handler(stop_handler)

        info_handler = CommandHandler('info', self.cb_info)
        self.updater.dispatcher.add_handler(info_handler)

        unknown_handler = CommandHandler(Filters.command, self.cb_unknown)
        self.updater.dispatcher.add_handler(unknown_handler)



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
    def cb_minute(self, bot, job):
        ccl = job.context # get phonebook.CheckCallList
        newCalls = ccl.checkForNewCalls()
        if len(newCalls) > 0:
            # save changes
            self.saveToFile(self.configFile)
            # create message to send out
            msgtext = "#################\n"
            msgtext += "**{0} new call{1}:**\n\n".format(len(newCalls), '' if len(newCalls) == 1 else 's') # plural s :)
            msgtext += '\n\n'.join(map(lambda x: x.toMd(), newCalls)) # calls -> text
            msgtext += "\n#################"
            # spread to all receivers
            for chatId in self.clientChatIds:
                bot.sendMessage(chat_id=chatId, text=msgtext, parse_mode='Markdown')


    def cb_start(self, bot, update):
        print("Add chat_id '{0}'".format(update.message.chat_id))
        self.clientChatIds.add(update.message.chat_id)
        bot.sendMessage(chat_id=update.message.chat_id, text="Added to messaging list")
        self.saveToFile(self.configFile)

    def cb_stop(self, bot, update):
        print("Remove chat_id '{0}'".format(update.message.chat_id))
        try:
            self.clientChatIds.remove(update.message.chat_id)
            answer = "Removed from messaging list."
            self.saveToFile(self.configFile)
        except KeyError:
            answer = "You aren't even in that list. Anyways..."
        bot.sendMessage(chat_id=update.message.chat_id, text=answer)


    def cb_unknown(self, bot, update):
        print("unknown command!")
        bot.sendMessage(chat_id=update.message.chat_id, text="Unknown command")


    def cb_info(self, bot, update):
        print("printing info")
        chats_as_strings = map(lambda x: "`"+str(x)+"`", self.clientChatIds)
        chats = "\n".join(chats_as_strings)
        msgtext = "I am reporting to those chats: \n" + chats
        bot.sendMessage(chat_id=update.message.chat_id, text=msgtext, parse_mode='Markdown')
