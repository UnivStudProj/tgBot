class MyLogger:
    __msg_info = f'[download]   0.0% of 0.0MiB at 0.0KiB/s ETA 00:00'
    __bot = None
    __botMessage = None

    def __init__(self, bot, botMessage) -> None:
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

    def myHook(self, d):
        if d['status'] != 'error':
            self.__bot.edit_message_text(
                self.__msg_info,
                self.__botMessage.chat.id,
                self.__botMessage.message_id
            )

        if d['status'] == 'finished':
            self.__bot.send_message(self.__botMessage.chat.id, "Converting...")

