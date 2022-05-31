import telebot
import logging
import json
import yt_dlp
import os
from config import API_KEY
from telebot import types
from shutil import rmtree
from loggerDL import Logger

bot = telebot.TeleBot(API_KEY)
logging.basicConfig(filename='./old/sample.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

userLink = ''
link_enabled = False


# Обработка команды 'начать'
@bot.message_handler(commands=['s'])
def cmd_start(message):
    global link_enabled
    bot.send_message(message.chat.id, 'Я в ожидании вашей ссылки из ютуба')
    link_enabled = True


# Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def text_url(message):
    global userLink, link_enabled
    if link_enabled: 
        userLink = message.text
        # Проверка правильности ссылки
        try:
            with yt_dlp.YoutubeDL({'simulate': True}) as ydl:
                ydl.download(userLink)
        except Exception:
            return bot.reply_to(message, 'Получена некорректная сслыка...')

        # Создание кнопок типа "inline"
        markup_inline = types.InlineKeyboardMarkup()
        item_audio = types.InlineKeyboardButton(text='Аудиотрек', callback_data='audio')
        item_video = types.InlineKeyboardButton(text='Видео', callback_data='video')
        markup_inline.add(item_audio, item_video)
        bot.reply_to(message, 'Что скачать?', reply_markup=markup_inline)

        
# Обработка при нажитии на кнопку
@bot.callback_query_handler(func=lambda call: True)
def call_answer(call):
    global userLink, link_enabled
    link_enabled = False

    # Строка ниже сообщает телеграму, что кнопка была обработана (иначе будет вечное ожидание)
    bot.answer_callback_query(callback_query_id=call.id)
    msg = bot.edit_message_text('Скачиваю...', call.message.chat.id, call.message.message_id)
    download_logger = Logger(bot, msg)
    os.mkdir('./temp')

    # Создает временную папку, в которую помещаем скачиваемые файлы
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

    # Скачать "аудио/видео"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(userLink)

    # Открывает файл с метадатой
    with open('temp/url.info.json', encoding='utf-8') as f:
        data = json.load(f)
        if call.data == 'video':
            video_width  = data['width']
            video_height = data['height']
        video_id         = data['id']
        title            = data['title']

    # Получить имя "аудио/видео" файла
    filename = next(os.walk('temp/'), (None, None, []))[2]
    filename.remove('url.info.json')
    filename = os.path.splitext(filename[0])[0]

    # Отрывает "аудио/видео" и картинку для превью
    temp_file = open(f'./temp/{filename}{".mp3" if call.data == "audio" else ".mp4"}', 'rb')
    thumbnail = open(f'./temp/{filename}.jpg', 'rb')

    # Отправляет трек
    bot.edit_message_text('Выгружаю...', call.message.chat.id, call.message.message_id)

    try:
        if call.data == 'audio':
            caption = f"""<a href='https://song.link/y/{video_id}'><i>song.link</i></a>"""
            bot.send_audio(call.message.chat.id, temp_file, 
                        thumb=thumbnail,
                        title=title, 
                        caption=caption, 
                        parse_mode='html')
        else:
            bot.send_video(call.message.chat.id, temp_file,
                        thumb=thumbnail,
                        width=video_width,
                        height=video_height, 
                        caption=title)

    except Exception:
        final_message = 'Произошла ошибка при загрузке файла. Возможно, размер файла слишком велик'

    temp_file.close()
    thumbnail.close()
    bot.edit_message_text('Готово' if 'final_message' not in locals() else final_message, call.message.chat.id, call.message.message_id)
    rmtree('./temp')
        
    
bot.polling(timeout=60)
