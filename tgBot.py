import telebot, pafy, os, subprocess, logging, requests, psycopg2
from config import tg_api_key, host, user, password, db_name
from telebot import custom_filters
from telebot import types

# FIXME: Blurry preview and encoding time

bot = telebot.TeleBot(tg_api_key)
bot.add_custom_filter(custom_filters.TextStartsFilter())
bot.add_custom_filter(custom_filters.TextMatchFilter())
logging.basicConfig(filename="./old/sample.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

usr_lnk = ''
dl_per = False  # flag for download permission
isNormalStream = False


# Database query
@bot.message_handler(text_startswith='/top')
def cmd_help(message):
    # Connecting to pgAdmin    
    try:
        connection = psycopg2.connect(
            host = host,
            user = user,
            password = password,
            database = db_name
        )     
        # Sending one song according to the position number
        if len(message.text) >= 5:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""SELECT * FROM tracks WHERE track_pos_number = {message.text[4:]};"""
                )
                row = cursor.fetchone()
                num = str(row[0]) + '. '
                artist = row[1] + ' - '
                name = row[2]
                whole_name = num + artist + name       
                bot.send_message(message.chat.id, whole_name)
        # Sending all top 100 songs
        else:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT * FROM tracks;""")
                song_l = ''
                # For each track
                for _ in range(1, 101):
                    row = cursor.fetchone()
                    pos = str(row[0]) + '. '
                    artist = row[1] + ' - '
                    name = row[2]
                    song_l += pos + artist + name + '\n'
                bot.send_message(message.chat.id, song_l)
    # Printing errors                              
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL:", _ex)
    # Closing connection
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")


# Check if command is 'help'
@bot.message_handler(commands=['help'])
def cmd_help(message):
    bot.send_message(message.chat.id,
        "Чтоб поздароваться с ботом, напишите 'Привет' или 'привет'. Чтоб запустить меня, напишите команду /s")


# Check if command is 'начать'
@bot.message_handler(commands=['s'])
def cmd_start(message):
    global dl_per
    bot.send_message(message.chat.id, "Я в ожидание вашей ссылки из ютуба")
    dl_per = True


# Receiving callback
@bot.callback_query_handler(func=lambda call: True)
def call_answer(call):
    global dl_per, usr_lnk, isNormalStream
    video = pafy.new(usr_lnk)
    if call.data == 'audio':
        audio_type = mp3_availability(video.audiostreams)
        best_audio = video.getbestaudio(preftype=audio_type)
        # Letting Telegram understand that button event is handled
        bot.answer_callback_query(callback_query_id=call.id)
        bot.send_message(call.message.chat.id, "Downloading best audio from the video...")
        # Stopping if no audiostreams
        if isNormalStream:
            bot.send_message(call.message.chat.id, "Unfortunaly, there is no audio to download...")
            isNormalStream = False
            return
        fp = f'./temp_aud/t_aud.{best_audio.extension}'
        best_audio.download(filepath=fp)
        if audio_type == 'any':
            bot.send_message(call.message.chat.id, "Converting the audio...")
            audio_name = convert_to_mp3(fp)
        else:
            audio_name = fp
        th = thumbnail_get(video.getbestthumb())
        c = f"<a href='https://song.link/y/{video.videoid}'><i>song.link</i></a>"
        # Sending audio
        bot.send_message(call.message.chat.id, "Uploading the track...")
        bot.send_audio(call.message.chat.id, open(audio_name, 'rb'), thumb=open(th, 'rb'), title=best_audio.title, caption=c, parse_mode='html')
        os.remove(audio_name)
    elif call.data == "video":
        # Letting Telegram understand that button event is handled
        bot.answer_callback_query(callback_query_id=call.id)
        best_video, best_audio = find_best_vid(video)
        th = thumbnail_get(video.bigthumb)
        bot.send_message(call.message.chat.id, f"Downloading the video ({best_video.resolution})")
        fp = f'./temp_vid/t_vid.{best_video.extension}'
        best_video.download(filepath=fp)
        video_name = os.path.abspath(fp)
        # If the video has only normal stream
        if not isNormalStream:
            bot.send_message(call.message.chat.id, "Merging...")
            video_name = merge(best_audio, fp)
        # Sending video
        bot.send_message(call.message.chat.id, "Uploading the video...")
        bot.send_video(call.message.chat.id, open(video_name, 'rb'), thumb=open(th, 'rb'), caption=best_video.title, timeout=180)
        os.remove(video_name)
    os.remove(th)
    isNormalStream = False
    dl_per = False


# Handling text messages
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global dl_per, usr_lnk
    # Handling greetings
    for h in ['Привет ', 'Привет', 'привет', 'привет ', '/start']:
        if message.text.startswith(h):
            bot.send_message(message.chat.id,
            "Привет. Я бот телеграмма для прослушивания аудиозаписи и просмотра видео")
            break
    if not dl_per: 
        return
    else:
        usr_lnk = message.text
        # Verifying link
        try:
            _ = pafy.new(usr_lnk)
        except ValueError:
            return bot.send_message(message.chat.id, "Got wrong link.")
        # Creating inline buttons
        markup_inline = types.InlineKeyboardMarkup()
        item_audio = types.InlineKeyboardButton(text='Audio', callback_data='audio')
        item_video = types.InlineKeyboardButton(text='Video', callback_data='video')
        markup_inline.add(item_audio, item_video)
        bot.send_message(message.chat.id, "What to download?", reply_markup=markup_inline)


# Checking best video
def find_best_vid(video):
    global isNormalStream
    # Iterating over videpstreams
    for v in video.videostreams:
        if eval(v.quality.replace('x', '*')) > 921600:
            break
        best_video = v
    best_audio = video.getbestaudio()
    if not video.videostreams:
        best_video = video.getbest()
        isNormalStream = True
    return best_video, best_audio


# Merging video- and audiostreams
def merge(best_audio, file_path):
    # Videostream file
    vid = file_path
    vid_abs_path = os.path.abspath(vid)
    # Audiostream file
    aud = f'./temp_aud/t_aud.{best_audio.extension}' 
    best_audio.download(filepath=aud)
    aud_abs_path = os.path.abspath(aud)
    # Converting by using ffmpeg
    subprocess.call(
        [
            'ffmpeg', '-hide_banner', \
            '-i', vid_abs_path, \
            '-i', aud_abs_path, '-c:v', 'libx264', '-crf', '27', '-preset', 'veryfast', '-c:a', 'aac', \
            vid_abs_path[:vid_abs_path.index('.')] + '_n.mp4'
        ]
    )
    # Deleting downloaded files
    os.remove(vid)
    os.remove(aud)
    return './temp_vid/t_vid_n.mp4'


# Checking if there mp3
def mp3_availability(audiostreams):
    global isNormalStream
    if not audiostreams:
        isNormalStream = True
        return
    # Iterating over audiostreams
    for a in audiostreams:
        if a.extension == 'mp3': 
            return a.extension
    return 'any'


# Converting downloaded audio to mp3
def convert_to_mp3(file_p):
    file_path = os.path.abspath(file_p)
    # Converting by using ffmpeg
    subprocess.call(
        ['ffmpeg', '-i', file_path, '-hide_banner', file_path[:file_path.index('.')] + '_n.mp3'])
    os.remove(file_p)
    return './temp_aud/t_aud_n.mp3'


# Getting a thumbnail
def thumbnail_get(url_thumb):
    r =  requests.get(url_thumb).content
    with open('thumb.jpg', 'wb') as thumb:
        thumb.write(r)
    return 'thumb.jpg'


bot.polling()
