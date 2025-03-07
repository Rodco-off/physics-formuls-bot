from aiogram import Router
from aiogram.types import Message


router = Router()


@router.message()
async def process_unknow_command(message: Message) -> None:

    await message.answer('''Извините, неизвестная комманда, напишите комманду /help, чтобы узнать какие комманды поддерживает наш бот''')
