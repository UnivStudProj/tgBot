import telebot
import logging
import json
import yt_dlp
import os
from config import API_KEY
from telebot import custom_filters, types
from shutil import rmtree
from loggerDL import Logger

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
        except Exception:
            return bot.send_message(message.chat.id, 'Wrong link...')

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
    link_enabled = False

    # Строка ниже сообщает телеграму, что кнопка была обработана (иначе будет вечное ожидание)
    bot.answer_callback_query(callback_query_id=call.id)
    msg = bot.send_message(call.message.chat.id, 'Скачиваю...')
    download_logger = Logger(bot, msg)
    os.mkdir('./temp')

    # creating temp folder and download audiostream there
    temp_path = './temp/%(uploader)s - %(fulltitle)s.%(ext)s'

    # yt-dlp options
    ydl_opts = {
        'writeinfojson'      : True,
        'writethumbnail'     : True,
        'format'             : 'mp3/ba' if call.data == 'audio' else 'mp4/bv',
        'logger'             : download_logger,
        'progress_hooks'     : [download_logger.downloadHook],
        'outtmpl': { 
            'infojson' : './temp/url.%(ext)s',
            'thumbnail': temp_path,
            'default'  : temp_path
        },
        'postprocessors': [{
            'key': 'FFmpegThumbnailsConvertor',
            'format': 'jpg'
        }, {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        } if call.data == 'audio' else {
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'         # "preferred" ?
        }]
    }

    # download file
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(userLink)

    # open metadata file
    with open('temp/url.info.json', encoding='utf-8') as f:
        data = json.load(f)
        if call.data == 'video':
            video_width  = data['width']
            video_height = data['height']
        video_id     = data['id']
        title        = data['title']

    # get path for an audio file and a thumbnail
    filename = next(os.walk('temp/'), (None, None, []))[2]
    filename.remove('url.info.json')
    filename = os.path.splitext(filename[0])[0]
    temp_file = f'./temp/{filename}{".mp3" if call.data == "audio" else ".mp4"}'
    thumbnail = f'./temp/{filename}.jpg'
    caption = f"""
        <a href='https://song.link/y/{video_id}'>
            <i>song.link</i>
        </a>"""

    # Отправляет трек
    bot.send_message(call.message.chat.id, 'Выгружаю...')

    if call.data == 'audio':
        bot.send_audio(call.message.chat.id, open(temp_file, 'rb'), 
                       thumb=open(thumbnail, 'rb'),
                       title=title, 
                       caption=caption, 
                       parse_mode='html')
    else:
        bot.send_video(call.message.chat.id, open(temp_file, 'rb'),
                       thumb=open(thumbnail, 'rb'),
                       width=video_width,
                       height=video_height, 
                       caption=title)

    rmtree('./temp')
        
    
bot.polling(none_stop=True, timeout=123)
