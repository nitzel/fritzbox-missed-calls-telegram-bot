# Fritzbox Missed Calls Bot
**What?** This bot will inform you about (fixed-line) calls you missed via the [telegram-messenger](https://telegram.org/).
It only works if your calls are managed by an AVM FritzBox. If available, it also displays the name associated with the phone number so that you know, who tried to call you - without even beeing at home.

![9ce2f028-ad36-11e6-84f4-8e4ae5699d16](https://cloud.githubusercontent.com/assets/8362046/20426026/8f24585e-ad7d-11e6-88d2-f491e7b36f4a.jpg)

# Usage
## Prerequisites
### Software
First, please install [Python 3.x](https://www.python.org/downloads/) and then install the necessary packages as superuser/admin:

- [requests]()
- [lxml](https://github.com/lxml/lxml) to parse XML
  - [precombiled windows binary](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml) and then `pip install lxml-....whl`
- [fritzconnection](https://github.com/kbr/fritzconnection) to access the FritzBox API
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) to manage your Telegram Bot

`pip install requests lxml fritzconnection python-telegram-bot --upgrade` or `pip install somepackage.whl`

### Telegram Bot Token
On Telegram, talk to **BotFather** to create a bot and get its access-token.

```bash
/newbot
#Botfather: name?
internbotname
#Botfather: username?
VisibleNameEndingWithBot
#Botfather: Congrats, your token is TOKEN
```

You'll need that token later!

### FritzBox
- Find out your FritzBox' IP
  - Good starting point is [fritz.box](fritz.box) when your in the FritzBox' LAN.
  - If the bot is running the FritzBox' LAN, the local IP is what we need. Usually it's yours but ending on `.1`.
- Create a user with access to the call-list and remember its name and password.
  - For security reason, disable access from internet if the bot runs from the LAN.

### Config
Open [bot_phonebook.cfg](./bot_phonebook.cfg) in your favorite UTF-8 compatible text editor.
What you see is the configuration in JSON-Format. Search for `fritzboxip`, `fritzboxpassword`, `fritzboxusername` and `telegrambot-token` and replace with the appropriate.

## Run
Now it's time to start our bot. Enter the directory and simply enter:

`python example.py` or `python3 example.py`

To stop the bot, you must kill the python process.


## From Telegram
In Telegram you can now search for your bots name and start a new chat with him.
You can control it via a few commands:
- `/start` The bot will inform you about new calls via this chat.
- `/stop` The bot will stop informing about new calls via this chat.
- `/info` The chat ids the bot is currently informing.

So go ahead and type `/start` and tell a friend to call you. If his phone-number
is available via a reverse lookup in the config file, via [tellows(Germany)](tellows.de) or
[dastelefonbuch(Germany)](dastelefonbuch.de) his name will show up.
Otherwise, it'll just be his number next to a question mark.

## Config
[bot_phonebook.cfg](./bot_phonebook.cfg)

- `knownCallId` The call-id of the most recent call that the bot has processed
- `phonebook` A dict with phonenumbers matched to names for reverse lookups.
- `clientChatIds` IDs of the Telegram-Chats the bot informs about new calls. If the URL of a chat is `https://web.telegram.org/#/im?p=g123` then its id is `g123`.

# Hacking the source
- **Add reverse lookups for phone numbers from your country:** Take a look at teh class `Phonebook` in [fritzbox.py](/fritzbotcallinfo/fritzbox.py). The function that performs the reverse lookup (matching a name to the phone number) is called `Phonebook.nameFromNumberLookup` and calls one of three functions beginning with `nameFrom`. Add yours or edit one of them to fit a service providing reverse lookups for your countries phone numbers. 
