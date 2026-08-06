from aiogram.utils.keyboard import InlineKeyboardBuilder


# Функция, укорачивающая список предметов за конкретный семестр
def callback_for_buttons(SubjectList):
    callback = []
    for i in SubjectList:
        if len(i) > 30:
            shortened_list = i[:30]
            callback.append(shortened_list)
        else:
            callback.append(i)
    return callback


# Клавиатура Inline кнопок из предметов за тот же семестр
def homework_keyboard(type, SubjectList):
    short =callback_for_buttons(SubjectList=SubjectList)

    kbd = InlineKeyboardBuilder()
    for Subject, Callback in zip(SubjectList, short):
        kbd.button(text=Subject, callback_data=f'{type}_{Callback}')
    return kbd.adjust(1,).as_markup()


# Функция получающая полный список укороченных предметов предметов
def list_for_dict(subjects):
    callback = []
    for i in subjects:
        short = [] 
        for k in i: 
            if len(k) > 30:
                shortened_list = k[:30]
                short.append(shortened_list)
            else:
                short.append(k)
        callback.append(short)
    return callback


# Функция, создающая словарь, где ключами являются укороченные слова
    # И им в соответствие ставятся полные слова
def subject_dict(full):
    short = list_for_dict(full)
    result_dict = {}
    for i, k in zip(short, full):
            for h, f in zip(i,k):
                result_dict[f"{h}"] = f
    return result_dict
