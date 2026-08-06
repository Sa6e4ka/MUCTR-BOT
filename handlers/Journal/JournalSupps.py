from aiogram.utils.keyboard import InlineKeyboardBuilder

def subject_dict(short, full):
    result_dict = {}
    for i, k in zip(short, full):
            for h, f in zip(i,k):
                result_dict[f"{h}"] = f
    return result_dict

def callback(subjects):
    callback = []
    for i in subjects:
        short = [] 
        for k in i: 
            if len(k) > 20:
                shortened_list = k[:20]
                short.append(shortened_list)
            else:
                short.append(k)
        callback.append(short)
    return callback

def semkbd(semnum, subjects):
    semnum = InlineKeyboardBuilder()
    for i, k in zip(subjects, callback(subjects)):
        semnum.button(text=i, callback_data=f'subject_{k}')
    return semnum.adjust(1,).as_markup()


def get_subject__full_info(course_number, semester_name, subject_name, journal):
        for course in journal["courses"]:
            if course["number"] == course_number: 
                for semester in course["semesters"]:
                    if semester["name"] == semester_name:
                        for subject in semester["subjects"]:
                            if subject["subject_name"] == subject_name:
                                return subject
        return None

def get_subject_info(semester_name, subject_name, journal):
        for course in journal["courses"]:
                for semester in course["semesters"]:
                    if semester["name"] == semester_name:
                        for subject in semester["subjects"]:
                            if subject["subject_name"] == subject_name:
                                return subject
        return None

