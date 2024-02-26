from aiogram import Bot, Router, types
from aiogram.filters import Command 
from filters.chat_types import Admin_filt

#Admin Router
ar = Router()

ar.message.filter(Admin_filt(['6592529444']))

# Когда-нибудь тут будут обработчики команд....