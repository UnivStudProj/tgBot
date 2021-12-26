import asyncio

from aiogram import Bot, executor, Dispatcher, types
from aiogram.types import InputFile

bot = Bot('2109248970:AAGTBjA4tTYIZDqX4cpirBi0tQ-bh8iXVqk')
dp = Dispatcher(bot)



@dp.message_handler(commands=["n"])
async def tst(message: types.Message):

    thumb = InputFile('./thumb.jpg')
    with open('./temp_vid/t_vid_n.mp4', 'rb') as video:
        await message.answer_video(video)

    await bot.close()

if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)