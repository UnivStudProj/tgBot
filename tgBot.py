import telebot, pafy, os, subprocess, logging
from config import tg_api_key
from telebot import custom_filters
from telebot import types

bot = telebot.TeleBot(tg_api_key)
bot.add_custom_filter(custom_filters.TextStartsFilter())
bot.add_custom_filter(custom_filters.TextMatchFilter())
dl_per = 0 # flag for download permisson
logging.basicConfig(filename="sample.log",format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
usr_lnk = ''  


# Check if text is 'Привет' or 'привет'     
@bot.message_handler(text=['Привет', 'привет'])
def text_hello(message):
    bot.send_message(message.chat.id,
    "Привет. Я бот телеграмма для прослушивания аудиозаписи и просмотра видео")


# Check if command is 'help'
@bot.message_handler(commands=['help'])
def cmd_help(message):
    bot.send_message(message.chat.id,
    "Чтоб поздароваться с ботом напишите <Привет> <привет>. Чтоб запустить меня напишите команду </начать>")


# Check if command is 'начать'
@bot.message_handler(commands=['s'])
def cmd_start(message):
    global dl_per
    bot.send_message(message.chat.id, "Я в ожидание вашей ссылки из ютуба")
    dl_per = 1


# Check if message starts with "https://www.youtube.com/"      
@bot.message_handler(text_startswith="https://www.youtube.com/")
def download_music(message):   
    global dl_per, usr_lnk
    if dl_per == 0: return
    usr_lnk = message.text
    markup_inline = types.InlineKeyboardMarkup()
    item_audio = types.InlineKeyboardButton(text='Audio', callback_data='audio')
    item_video = types.InlineKeyboardButton(text='Video', callback_data='video')
    markup_inline.add(item_audio, item_video)
    bot.send_message(message.chat.id, "What to download?", reply_markup=markup_inline)


# Receiving callback
@bot.callback_query_handler(func=lambda call: True)
def call_answer(call):
    global dl_per, usr_lnk
    try:
        if call.data == 'audio':
            video = pafy.new(usr_lnk)
            audio_type = mp3_availability(video.audiostreams)
            best_audio = video.getbestaudio(preftype=audio_type)
            bot.answer_callback_query(callback_query_id=call.id) # Letting Telegram understand that button event is handled 
            bot.send_message(call.message.chat.id, "Downloading best audio from the video...")         
            best_audio.download()
            if audio_type == 'any':
                bot.send_message(call.message.chat.id, "Converting the audio...")
                audio_name = convert_to_mp3(video.title, '.' + best_audio.extension)
            else:
                audio_name = video.title + '.' + best_audio.extension
            bot.send_audio(call.message.chat.id, open(audio_name, 'rb'))
            os.remove(audio_name)
        elif call.data == "video":
            video = pafy.new(usr_lnk)
            video_type = mp4_availability(video.streams)
            best_video = video.getbest(preftype=video_type)
            bot.answer_callback_query(callback_query_id=call.id) # Letting Telegram understand that button event is handled 
            bot.send_message(call.message.chat.id, "Downloading the video ({})".format(best_video.resolution))
            best_video.download()
            if video_type == 'any':
                bot.send_message(call.message.chat.id, "Converting the video...")
                video_name = convert_to_mp4(video.title, '.' + best_video.extension)
            else:
                video_name = video.title + '.' + best_video.extension
            video_name = video.title + '.' + best_video.extension
            bot.send_video(call.message.chat.id, open(video_name, 'rb'))
            os.remove(video_name)
        dl_per = 0   
    except ValueError:
        bot.send_message(call.message.chat.id, "dNeed 11 character video id or the URL of the video.")
    

# Handling text messages
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global dl_per
    # Verifying a link
    if dl_per == 1 and not message.text.startswith("https://www.youtube.com/watch?v="):
        return bot.send_message(message.chat.id, "Got incorrect link, please write a valid link")
  

# Checking if there mp4
def mp4_availability(streams):
    for s in streams:
        if s.extension == 'mp4': return s.extension
    return 'any'

  
# Checking if there mp3
def mp3_availability(audiostreams):
    for a in audiostreams:
        if a.extension == 'mp3': return a.extension
    return 'any'
        
        
# Converting downloaded video to mp4
def convert_to_mp4(file_name, file_extension):
    whole_file = file_name + file_extension
    file_path = os.path.abspath(whole_file) # Setting a path of file
    subprocess.call(['ffmpeg', '-i', file_path, '-hide_banner', file_path[:file_path.index('.')] + '.mp4']) # Converting by using ffmpeg
    os.remove(whole_file)
    return file_name + '.mp4'


# Converting downloaded audio to mp3
def convert_to_mp3(file_name, file_extension):
    whole_file = file_name + file_extension
    file_path = os.path.abspath(whole_file) # Setting a path of file
    subprocess.call(['ffmpeg', '-i', file_path, '-hide_banner', file_path[:file_path.index('.')] + '.mp3']) # Converting by using ffmpeg
    os.remove(whole_file)
    return file_name + '.mp3'


bot.polling()
