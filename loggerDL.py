class Logger:

    def __init__(self, bot, botMessage):
        self.__msg_info = f'[download]   0.0% of 0.0MiB at 0.0KiB/s ETA 00:00'
        self.__bot = bot
        self.__botMessage = botMessage

    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        self.__msg_info = msg

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

    def downloadHook(self, d):
        if d['status'] == 'downloading':
            self.__bot.edit_message_text(
                self.__msg_info.split('[download]')[1],
                self.__botMessage.chat.id,
                self.__botMessage.message_id
            )

        elif d['status'] == 'finished':
            self.__bot.edit_message_text(
                "Конвертирую...",
                self.__botMessage.chat.id,
                self.__botMessage.message_id
            )

