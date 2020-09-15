import telebot
import os
from datetime import datetime
from core import picture_processor
from telebot import types

USER_PICTURES_PATH = os.path.abspath("./user_pictures/")
RESOURCES_PATH = os.path.abspath('./resources/')


# import logging
# import ssl
# from aiohttp import web

TOKEN = '1367451894:AAEbiQxuvYXGhlCi7b5fwc-di5DAfk5nPOQ'

# ----- WEBHOOK CONFIG

# WEBHOOK_HOST = 'ip adress of host'
# WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
# WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
#
# WEBHOOK_SSL_CERT = '/path/to/cert.cert'  # Path to the ssl certificate
# WEBHOOK_SSL_PRIV = '/path/to/private.key'  # Path to the ssl private key
#
# WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
# WEBHOOK_URL_PATH = "/{}/".format(TOKEN)
#
# logger = telebot.logger
# telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(TOKEN)

# ------- ALSO WEBHOOK CONFIG
# app = web.Application()


# async def handle(request):
#     if request.match_info.get('token') == bot.token:
#         request_body_dict = await request.json()
#         update = telebot.types.Update.de_json(request_body_dict)
#         bot.process_new_updates([update])
#         return web.Response()
#     else:
#         return web.Response(status=403)
#
#
# app.router.add_post('/{token}/', handle)



def createPicName(now, user_id):
    date = "_".join(str(now).split('.')[0].split(" "))
    return date + "_" + str(user_id) + ".jpg"


@bot.message_handler(commands=['start'])
def start(message):
    ans = bot.send_message(message.chat.id, "Привет, отправь мне картинку!")
    return bot.register_next_step_handler(ans, getPic)


@bot.message_handler(content_types=['photo', 'text'])
def getPic(message):
    if not message.photo:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте картинку!")
        return bot.register_next_step_handler(message, getPic)
    markup = None
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    picName = '/'+createPicName(datetime.now(), message.from_user.id)
    with open(USER_PICTURES_PATH + picName, 'wb') as pic:
        pic.write(downloaded_file)
    picture_processor.addText(USER_PICTURES_PATH + picName, picture_processor.getRandomPhrase(), "/temp.jpg")
    isMakeupAvailable = picture_processor.doMakeUp(USER_PICTURES_PATH + picName)
    newPic = open(RESOURCES_PATH + "/temp.jpg", "rb")
    return sendPic(message, newPic, isMakeupAvailable)


def sendPic(message, newPic, isMakeupAvailable):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    acceptBtn = types.KeyboardButton('Давай посмотрим')
    denyBtn = types.KeyboardButton('Нет, спасибо)')
    markup.row(acceptBtn, denyBtn)
    bot.send_photo(message.chat.id, newPic)
    if not isMakeupAvailable:
        return bot.register_next_step_handler(message, getPic)
    else:
        ans = bot.send_message(message.chat.id, "Я обнаружил на фото чей-то фейс. Могу его поправить, хочешь?",
                               reply_markup=markup)
        return bot.register_next_step_handler(ans, processMakeup)


def processMakeup(message):
    if message.text == 'Давай посмотрим':
        newPic = open(RESOURCES_PATH + "/makeup.jpg", "rb")
        bot.send_photo(message.chat.id, newPic)
        bot.send_message(message.chat.id, "Ну как? Шли еще фотки!")
        return bot.register_next_step_handler(message, getPic)
    elif message.text == 'Нет, спасибо)':
        bot.send_message(message.chat.id, 'Ок, я и дальше к твоим услугам!')
        return bot.register_next_step_handler(message, getPic)
    else:
        message = bot.send_message(message.chat.id, 'Не понял, выбери один из двух вариантов!')
        return bot.register_next_step_handler(message, processMakeup)


bot.polling(none_stop=False)
