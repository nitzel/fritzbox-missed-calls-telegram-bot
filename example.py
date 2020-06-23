# -*- coding: utf-8 -*-
""" Simplest example for fritzboxcallinfo usage """
from fritzbotcallinfo import CallInfoBot

# Change mock_fritzbox to `True` if you don't want to connect to a real 
# FritzBox at the moment and instead just need to test the Telegram bot.
CI_BOT = CallInfoBot(config_file='bot_phonebook.cfg', mock_fritzbox=True)

CI_BOT.startPolling()
CI_BOT.updater.idle()
