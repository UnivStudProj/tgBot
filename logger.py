class Logger:

    def __init__(self, bot, botMessage):
        self.__bot = bot
        self.__botMessage = botMessage
        self.__last_msg = ''
        self.__msg_info = f'0.0% of 0.0MiB at 0.0KiB/s ETA 00:00'

    def debug(self, msg):
        # Для совместимости с 'youtube-dl', 'debug' и 'info' передаются в 'debug'
        # Их можно различить с помощью префикса '[debug] '
        if not msg.startswith('[debug] '):
            self.__msg_info = msg

    def downloadHook(self, d):
        # Не обновляем сообщение, если оно точно такое же, как и предыдущее
        if self.__last_msg == self.__msg_info: return

        # Показывает статус загрузки
        if d['status'] == 'downloading':
            self.__bot.edit_message_text(
                self.__msg_info.split('[download]')[1],
                self.__botMessage.chat.id,
                self.__botMessage.message_id
            )
            self.__last_msg = self.__msg_info

        # После завершения загрузки
        elif d['status'] == 'finished':
            self.__bot.edit_message_text(
                "Конвертирую...",
                self.__botMessage.chat.id,
                self.__botMessage.message_id
            )
