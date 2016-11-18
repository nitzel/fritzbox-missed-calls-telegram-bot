# -*- coding: utf-8 -*-
from fritzbotcallinfo import CallInfoBot

cib = CallInfoBot(configFile = 'bot_phonebook.cfg')

cib.startPolling()
cib.updater.idle()
