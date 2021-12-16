import telebot
bot = telebot.TeleBot("2044262249:AAEmNIoXNS1FlXxyWR4t02YWDCVJ11Lao8Q")
@bot.message_handler(content_types=['text'])
def get_text_messages(message) :
    if message.text == 'Привет' or message.text == 'привет' or message.text == '/start':
        bot.send_message(message.from_user.id,
                         "Привет. Я бот телеграмма для прослушивания аудиозаписи и просмотра видео")
    elif message.text == "/help":
        bot.send_message(message.from_user.id,
                         "Чтоб поздароваться с ботом напишите <Привет> <привет>.     Чтоб запустить меня напишите команду </начать>")
    elif message.text == "/начать":
        bot.send_message(message.from_user.id, "Я в ожидание вашей ссылки из ютуба")
        message.text = message.get()

        def ccilka(message):
            while message.text != 'https://':
                bot.send_message(message.from_user.id, 'Введи ссылку')
                break
            if message.text.startswith("https://www.youtube.com"):
                bot.send_message(message.from_user.id, "ютуб")
            elif message.text.startswith("https://vk.com/" or message.text.startswith("https://yandex.ru/")):
                bot.send_message(message.from_user.id, "Это ссылка не с ютуба введи ссылку с ютуба")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю, напишите /help.")

bot.polling(none_stop=True, interval=0)
