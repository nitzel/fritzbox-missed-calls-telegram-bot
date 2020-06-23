# -*- coding: utf-8 -*-
""" Simplest example for fritzboxcallinfo usage """
from fritzbotcallinfo import CallInfoBot

# Change mock_fritzbox to `False` of you want to actually connect to one
CI_BOT = CallInfoBot(config_file='bot_phonebook.cfg', mock_fritzbox=True)

CI_BOT.startPolling()
CI_BOT.updater.idle()
