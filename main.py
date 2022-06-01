import telebot
import json
import yt_dlp
import os
import logging
from config import API_KEY
from telebot import types, apihelper
from shutil import rmtree
from logger import Logger

input_URL = ''
link_enabled = False
isAudio = False

bot = telebot.TeleBot(API_KEY)
apihelper.SESSION_TIME_TO_LIVE = 2 * 60
logging.basicConfig(filename="error.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# Выбирает какую часть использовать в зависимости от нажатой кнопки
def byChoice(audioPart, videoPart):
    return audioPart if isAudio else videoPart


# Обработка команды 'начать'
@bot.message_handler(commands=['s'])
def command_start(message):
    global link_enabled
    bot.send_message(message.chat.id, 'Я в ожидании вашей ссылки из ютуба')
    link_enabled = True


# Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def text_url(message):
    global input_URL, link_enabled
    if link_enabled:
        input_URL = message.text
        # Проверка правильности ссылки
        try:
            with yt_dlp.YoutubeDL({'simulate': True}) as ydl:
                ydl.download(input_URL)
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
    global input_URL, link_enabled, isAudio
    link_enabled = False
    isAudio = True if call.data == 'audio' else False

    # Строка ниже сообщает телеграму, что кнопка была обработана (иначе будет вечное ожидание)
    bot.answer_callback_query(callback_query_id=call.id)

    # Сообщает о начале загрузке и инициализирует класс для логов
    msg = bot.edit_message_text('Скачиваю...', call.message.chat.id, call.message.message_id)
    download_logger = Logger(bot, msg)

    # Создает временную папку, в которую помещает скачиваемые файлы
    os.mkdir('./temp')
    temp_path = './temp/%(uploader)s - %(fulltitle)s.%(ext)s'

    # Настройки скачивания аудио/видео
    ydl_opts = {
        'writeinfojson'      : True,
        'writethumbnail'     : True,
        'format'             : byChoice('ba[ext=mp3][filesize<50M]/ba[filesize<50M]', 'b[ext=mp4][filesize<50M]/b[filesize<50M]'),
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
        }, byChoice({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }, {
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'         # "preferred" ?
        })]
    }

    try:
        # Скачать "аудио/видео"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(input_URL)
    # Обработка ошибки
    except Exception as e:
        logging.info(e)
        err_message = f'Доступные {byChoice("аудио", "видео")} для скачивания превышают лимит в 50 Мб, попробуйте другое видео'
        rmtree('./temp')

        return bot.edit_message_text(err_message, call.message.chat.id, call.message.message_id)

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
    temp_file = open(f'./temp/{filename}{byChoice(".mp3", ".mp4")}', 'rb')
    thumbnail = open(f'./temp/{filename}.jpg', 'rb')

    bot.edit_message_text('Выгружаю...', call.message.chat.id, call.message.message_id)
    try:
        if call.data == 'audio':
            # Отправляет аудиотрек
            bot.send_audio(call.message.chat.id, temp_file,
                        thumb=thumbnail,
                        title=title,
                        caption=f"<a href='https://song.link/y/{video_id}'><i>song.link</i></a>",
                        parse_mode='html')
        else:
            # Отправляет видео
            bot.send_video(call.message.chat.id, temp_file,
                        thumb=thumbnail,
                        width=video_width,
                        height=video_height,
                        caption=title)
    # Обработка ошибки
    except Exception as e:
        logging.info(e)
        final_message = 'Произошла неизвестая ошибка при загрузке файла.'
    else:
        final_message = 'Готово'

    # Сообщает об успешной выгрузке файла
    bot.edit_message_text(final_message, call.message.chat.id, call.message.message_id)

    # Закрывает ранее открытые файлы и удаляет времменую папку
    temp_file.close()
    thumbnail.close()
    rmtree('./temp')


bot.polling(timeout=60)
