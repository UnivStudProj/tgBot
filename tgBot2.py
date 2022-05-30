import telebot
import logging
import json
import yt_dlp
from config import API_KEY
from telebot import custom_filters
from telebot import types
from shutil import rmtree
from os import mkdir
from Logger import MyLogger

bot = telebot.TeleBot(API_KEY)
bot.add_custom_filter(custom_filters.TextStartsFilter())
bot.add_custom_filter(custom_filters.TextMatchFilter())
logging.basicConfig(filename='./old/sample.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

userLink = ''
link_enabled = False


# Обработка команды 'начать'
@bot.message_handler(commands=['s'])
def cmd_start(message):
    global link_enabled
    bot.send_message(message.chat.id, 'Я в ожидании вашей ссылки из ютуба')
    link_enabled = True


# Обработка тестовых сообщений
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global userLink, link_enabled
    if link_enabled: 
        userLink = message.text
        # Проверка правильности ссылки
        try:
            with yt_dlp.YoutubeDL({'simulate': True}) as ydl:
                ydl.download(userLink)
        except Exception as e:
            return bot.send_message(message.chat.id, str(e).split(': ')[1])

        # Создание кнопок типа "inline"
        markup_inline = types.InlineKeyboardMarkup()
        item_audio = types.InlineKeyboardButton(text='Аудиотрек', callback_data='audio')
        item_video = types.InlineKeyboardButton(text='Видео', callback_data='video')
        markup_inline.add(item_audio, item_video)
        bot.send_message(message.chat.id, 'Что скачать?', reply_markup=markup_inline)

        
# Обработка при нажитии на кнопку
@bot.callback_query_handler(func=lambda call: True)
def call_answer(call):
    global userLink, link_enabled
    if call.data == 'audio':
        # Строка ниже сообщает телеграму, что кнопка была обработана (иначе будет вечное ожидание)
        bot.answer_callback_query(callback_query_id=call.id)
        msg = bot.send_message(call.message.chat.id, 'Скачиваю аудиотрек...')
        download_logger = MyLogger(bot, msg)

        # creating temp folder and downloading audiostream there
        mkdir('./temp')
        audio_path = './temp/%(uploader)s - %(fulltitle)s.%(ext)s'

        ydl_opts = {
            'writeinfojson'      : True,
            'writethumbnail'     : True,
            'format'             : 'mp3/ba',
            'logger'             : download_logger,
            'progress_hooks'     : [download_logger.myHook],
            'outtmpl': { 
                'infojson' : './temp/url.%(ext)s',
                'thumbnail': audio_path,
                'default'  : audio_path
            },
            'postprocessors': [{
                'key': 'FFmpegThumbnailsConvertor',
                'format': 'jpg'
            }, {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3'
            }]
        }

        # download file
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(userLink)

        # open metadata file
        with open('temp/url.info.json') as f:
            data = json.load(f)
            video_id = data['id']
            title = data['title']
            uploader = data['uploader']

        # setting path for an audio file and a thumbnail
        audio_file = audio_path % {'uploader': uploader, 'fulltitle': title, 'ext': "mp3"}
        thumbnail  = audio_path % {'uploader': uploader, 'fulltitle': title, 'ext': "jpg"}
        caption = f"""
            <a href='https://song.link/y/{video_id}'>
                <i>song.link</i>
            </a>"""

        # Отправляет трек
        bot.send_message(call.message.chat.id, 'Выгружаю трек...')
        bot.send_audio(call.message.chat.id, open(audio_file, 'rb'), 
                       thumb=open(thumbnail, 'rb'),
                       title=title, 
                       caption=caption, 
                       parse_mode='html')

        rmtree('./temp')

    link_enabled = False
        
    
bot.polling()
