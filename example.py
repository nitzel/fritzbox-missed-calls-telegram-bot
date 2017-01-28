# -*- coding: utf-8 -*-
""" Simplest example for fritzboxcallinfo usage """
from fritzbotcallinfo import CallInfoBot


CI_BOT = CallInfoBot(configFile='bot_phonebook.cfg')

CI_BOT.startPolling()
CI_BOT.updater.idle()
