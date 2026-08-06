from aiogram.utils.keyboard import InlineKeyboardBuilder

#Auth Button
AuthKB = InlineKeyboardBuilder()
agreement_list = ['Согласен(на)', 'Не согласен(на)']

for item in agreement_list:
   AuthKB.button(text=item, callback_data=item)
AuthKB.adjust(2)

#Map buttons
korpus_mapKB = InlineKeyboardBuilder()

korpus_mapKB.button(text='Миусский копрус', callback_data='Miusi')
korpus_mapKB.button(text='Тушинский копрус', callback_data='Tushka')

korpus_mapKB.adjust(1)

Miusi_mapKB = InlineKeyboardBuilder()

miusi_floor_list = ['1 этаж', '2 этаж','3 этаж','4 этаж','5 этаж']

for item in miusi_floor_list:
   
   Miusi_mapKB.button(text=item, callback_data=f'M_{item}')
Miusi_mapKB.adjust(2,2,1)


Tushka_mapKB = InlineKeyboardBuilder()

Tushka_floor_list = ['1 этаж', '2 этаж','3 этаж','4 этаж','5 этаж', '6 этаж','7 этаж','8 этаж','9 этаж']

for i in Tushka_floor_list:
   Tushka_mapKB.button(text=i, callback_data=f'T_{i}')
Tushka_mapKB.adjust(2,1,2,1,2,1)
