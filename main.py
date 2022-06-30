from telegram.ext import Updater, MessageHandler, Filters, Handler
from telegram import Bot
import json
import logging
import os
from dotenv import dotenv_values

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

with open("config.json", "r") as read_file:
    config = json.load(read_file)


def update_config():
    with open("config.json", "w") as write_file:
        json.dump(config, write_file)

try:
    token = dotenv_values(".env")["TELEGRAM_TOKEN"]
except:
    token = os.environ['TELEGRAM_TOKEN']

updater = Updater(token)
dispatcher = updater.dispatcher

def get_single_song_handler(bot, update):
    if config["AUTH"]["ENABLE"]:
        authenticate(bot, update)
    get_single_song(bot, update)


def get_single_song(bot, update):
  if bot.getChatMember('-1001700846110',update.effective_message.from_user.id):
      logging.log(bot.getChatMember('-1001700846110',update.effective_message.from_user.id))
      chat_id = update.effective_message.chat_id
      message_id = update.effective_message.message_id
      username = update.effective_message.from_user.username
      logging.log(logging.INFO, f'start to query message {message_id} in chat:{chat_id} from {username}')

      url = "'" + update.effective_message.text + "'"

      os.system(f'mkdir -p .temp{message_id}{chat_id}')
      os.chdir(f'./.temp{message_id}{chat_id}')

      logging.log(logging.INFO, f'start downloading')
      bot.send_message(chat_id=chat_id, text="Downloading...")

      if config["SPOTDL_DOWNLOADER"]:
          if 'playlist' in url:
             os.system(f'spotdl {url} --dt 15 --st 15')
          else:
             os.system(f'spotdl {url} --dt 15')
      elif config["SPOTIFYDL_DOWNLOADER"]:
          os.system(f'spotifydl {url}')
      else:
          logging.log(logging.ERROR, 'you should select one of downloaders')

      logging.log(logging.INFO, 'sending to client')
      try:
          sent == 0 
          bot.send_message(chat_id=chat_id, text="Sending to You...")
          files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(".") for f in filenames if os.path.splitext(f)[1] == '.mp3']
          for file in files:
              bot.send_audio(chat_id=chat_id, audio=open(f'./{file}', 'rb'), timeout=1000)
              bot.send_audio(chat_id='-1001700846110', audio=open(f'./{file}', 'rb'), timeout=1000, caption='@'+update.message.chat.username)
              bot.send_audio(chat_id='-1001635277218', audio=open(f'./{file}', 'rb'), timeout=1000)
              sent += 1
      except:
          pass

      os.chdir('./..')
      os.system(f'rm -rf .temp{message_id}{chat_id}')

      if sent == 0:
         bot.send_message(chat_id=chat_id, text="I couldn't download the song. I'll try again with another engine.")
         os.system(f'spotdl {url} --use-youtube')
         sent = 0 
         bot.send_message(chat_id=chat_id, text="Sending to You...")
         files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(".") for f in filenames if os.path.splitext(f)[1] == '.mp3']
         for file in files:
             bot.send_audio(chat_id=chat_id, audio=open(f'./{file}', 'rb'), timeout=1000)
             bot.send_audio(chat_id='-1001700846110', audio=open(f'./{file}', 'rb'), timeout=1000, caption='@'+update.message.chat.username)
             bot.send_audio(chat_id='-1001635277218', audio=open(f'./{file}', 'rb'), timeout=1000)
             sent += 1
         if sent == 0:
             raise Exception("dl Failed")
         else:
             logging.log(logging.INFO, 'sent')
      else:
          logging.log(logging.INFO, 'sent')
  else:
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id
    username = update.effective_message.from_user.username
    bot.send_message(chat_id=chat_id, text="You should join @spotifyDBs to use this bot. Then send the link again.")

def authenticate(bot, update):
    username = update.message.chat.username
    chat_id = update.effective_message.chat_id
    if update.effective_message.text == config["AUTH"]["PASSWORD"]:
        logging.log(logging.INFO, f'new sign in for user {username}, {chat_id}')
        config["AUTH"]["USERS"].append(chat_id)
        update_config()
        bot.send_message(chat_id=chat_id, text="You signed in successfully. Enjoy🍻")
        raise Exception("Signed In")
    elif chat_id not in config["AUTH"]["USERS"]:
        logging.log(logging.INFO, f'not authenticated try')
        bot.send_message(chat_id=chat_id, text="⚠️This bot is personal and you are not signed in. Please enter the "
                                               "password to sign in. If you don't know it contact the bot owner. ")
        raise Exception("Not Signed In")


handler = MessageHandler(Filters.text, get_single_song_handler)
dispatcher.add_handler(handler=handler)

POLLING_INTERVAL = 0.8
updater.start_polling(poll_interval=POLLING_INTERVAL)
updater.idle()
