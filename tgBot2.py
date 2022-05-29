import telebot
import os
import subprocess
import logging
import pathlib
import json
from config import tg_api_key
from telebot import custom_filters
from telebot import types

bot = telebot.TeleBot(tg_api_key)
bot.add_custom_filter(custom_filters.TextStartsFilter())
bot.add_custom_filter(custom_filters.TextMatchFilter())
logging.basicConfig(filename="./old/sample.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

userLink = ''
link_enabled = False


# Обработка команды 'начать'
@bot.message_handler(commands=['s'])
def cmd_start(message):
    global link_enabled
    bot.send_message(message.chat.id, "Я в ожидании вашей ссылки из ютуба")
    link_enabled = True


# Обработка тестовых сообщений
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global userLink, link_enabled
    if link_enabled: 
        userLink = message.text
        # Проверка правильности ссылки
        try:
            _ = pafy.new(userLink)
        except ValueError:
            return bot.send_message(message.chat.id, "Получена неверная ссылка, попробуйте ввести снова")

        # Создание кнопок типа "inline"
        markup_inline = types.InlineKeyboardMarkup()
        item_audio = types.InlineKeyboardButton(text='Аудиотрек', callback_data='audio')
        item_video = types.InlineKeyboardButton(text='Видео', callback_data='video')
        markup_inline.add(item_audio, item_video)
        bot.send_message(message.chat.id, "Что скачать?", reply_markup=markup_inline)

        
# Обработка при нажитии на кнопку
@bot.callback_query_handler(func=lambda call: True)
def call_answer(call):
    global userLink, link_enabled
    if call.data == "audio":
        # Строка ниже сообщает телеграму, что кнопка была обработана (иначе будет вечное ожидание)
        bot.answer_callback_query(callback_query_id=call.id)
        bot.send_message(call.message.chat.id, "Скачиваю аудиотрек...")
        audio_path = "/temp_aud/%(creator)s - %(title)s.%(ext)s"
        subprocess.call(
            ["yt-dlp", "--compat-options", "no-clean-infojson", "-x", userLink, "-f", "ba", "-o", audio_path]
        )

        with open("temp_aud/data.info.json") as f:
            data = json.load(f)
            title = data["title"]
            uploader = data["uploader"]
            thumbnail = f"temp_aud/{title}.opus"

        caption = f"""
            <a href='https://song.link/y/{video.videoid}'>
                <i>song.link</i>
            </a>"""

        # Отправляет трек
        bot.send_message(call.message.chat.id, "Выгружаю трек...")
        bot.send_audio(call.message.chat.id, open(audio_path % (title, uploader), 'rb'), 
                       thumb=open(thumbnail, 'rb'),
                       title=best_audio.title, 
                       caption=c, parse_mode='html')
        os.remove(audio_name)
        
    
bot.polling()
