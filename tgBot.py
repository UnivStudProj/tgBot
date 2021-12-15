import telebot, pafy, os, subprocess, logging, requests, psycopg2
from config import tg_api_key, host, user, password, db_name
from telebot import custom_filters
from telebot import types

bot = telebot.TeleBot(tg_api_key)
bot.add_custom_filter(custom_filters.TextStartsFilter())
bot.add_custom_filter(custom_filters.TextMatchFilter())
dl_per = 0  # flag for download permission
logging.basicConfig(filename="sample.log", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
usr_lnk = ''


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
        print("[INFO] Error while working with PosgreSQL:", _ex)
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
    dl_per = 1


# Receiving callback
@bot.callback_query_handler(func=lambda call: True)
def call_answer(call):
    global dl_per, usr_lnk
    video = pafy.new(usr_lnk)
    if call.data == 'audio':
        audio_type = mp3_availability(video.audiostreams)
        best_audio = video.getbestaudio(preftype=audio_type)
        # Letting Telegram understand that button event is handled
        bot.answer_callback_query(callback_query_id=call.id)
        bot.send_message(call.message.chat.id, "Downloading best audio from the video...")
        best_audio.download()
        if audio_type == 'any':
            bot.send_message(call.message.chat.id, "Converting the audio...")
            audio_name = convert_to_mp3(video.title, '.' + best_audio.extension)
        else:
            audio_name = video.title + '.' + best_audio.extension
        th = thumbnail_get(video.bigthumb)
        c = f"<a href='https://song.link/y/{video.videoid}'><i>song.link</i></a>"
        # Sending audio
        bot.send_audio(call.message.chat.id, open(audio_name, 'rb'), thumb=open(th, 'rb'), caption=c, parse_mode='html')
        os.remove(audio_name)
        os.remove(th)
    elif call.data == "video":
        # Letting Telegram understand that button event is handled
        bot.answer_callback_query(callback_query_id=call.id)
        best_video, best_audio = find_best_vid(video)
        bot.send_message(call.message.chat.id, f"Downloading the video ({best_video.resolution})")
        best_video.download()
        bot.send_message(call.message.chat.id, "Merging...")
        video_name = merge(best_video, best_audio)
        # Sending video
        bot.send_message(call.message.chat.id, "Uploading the video...")
        th = thumbnail_get(video.thumb)
        bot.send_video(call.message.chat.id, open(video_name, 'rb'), thumb=open(th, 'rb'))
        os.remove(video_name)
        os.remove(th)
    dl_per = 0


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
    if dl_per == 0: 
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
    for v in video.videostreams:
        if int(str(v)[str(v).index('x') + 1:]) > 720: 
            break
        best_video = v
    best_audio = video.getbestaudio()
    return best_video, best_audio


# Merging video- and audiostreams
def merge(best_video, best_audio):
    # Videostream file
    v_ttl = best_video.title + '_v'
    v_ext = '.' + best_video.extension
    os.rename(best_video.title + v_ext, v_ttl + v_ext)
    vid = v_ttl + v_ext
    vid_path = os.path.abspath(vid)
    # Audiostream file
    best_audio.download()
    os.rename(best_audio.title + '.' + best_audio.extension, best_audio.title + '_a' + v_ext)
    aud = best_audio.title + '_a' + v_ext
    aud_path = os.path.abspath(aud)
    # Converting by using ffmpeg
    logging.info(v_ttl)
    subprocess.call(
        ['ffmpeg', '-i', vid_path, '-hide_banner', '-i', aud_path, '-c:v', 'copy', '-c:a', 'aac', vid_path[:vid_path.index('_v') + 2] + '_n' + '.mp4'])
    # Deleting downloaced files
    os.remove(vid)
    os.remove(aud)
    os.rename(v_ttl + '_n' + '.mp4', best_video.title + '.mp4')
    return best_video.title + '.mp4'


# Checking if there mp3
def mp3_availability(audiostreams):
    for a in audiostreams:
        if a.extension == 'mp3': 
            return a.extension
    return 'any'


# Converting downloaded audio to mp3
def convert_to_mp3(file_name, file_extension):
    whole_file = file_name + file_extension
    file_path = os.path.abspath(whole_file)
    # Converting by using ffmpeg
    subprocess.call(
        ['ffmpeg', '-i', file_path, '-hide_banner', file_path[:file_path.index('.')] + '.mp3'])
    os.remove(whole_file)
    return file_name + '.mp3'


# Getting a thumbnail
def thumbnail_get(url_thumb):
    r =  requests.get(url_thumb).content
    with open('thumb.jpg', 'wb') as thumb:
        thumb.write(r)
    return 'thumb.jpg'


bot.polling()
