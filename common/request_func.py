import requests
import fake_useragent
import json
import os

def request(username, password):

#Создание юзер-агента и сессии
    user = fake_useragent.UserAgent().random
    session = requests.Session()
    
#Передача логина и пароля в дату при авторизации
    headers_auth = {
        'user-agent' : user
    }

    data_auth = {
        'username': username, 
        'password': password 
    }

#получение токена
    link = "https://api.muctr.ru/accounts/authenticate/login/"
    token =  session.post(link, headers= headers_auth, data = data_auth).json().get('token')
    # print(token)
    
#передача токена в заголовки (обязательный шаг)
    headers = {
        
        'authorization': f'Token {token}',
        'user-agent': user,
    }

#Получение eios_id
    eios_link = 'https://api.muctr.ru/education/students/student/'
    eios_id = session.get(eios_link, headers= headers).json()['educations'][0]['id']
    eios_id_json = session.get(eios_link, headers= headers).json()
    group_id = eios_id_json['educations'][0]['education_group']['id']

#Получение журнала с баллами в виде .json
    journal_link = f'https://api.muctr.ru/education/students/education/{eios_id}/journal/full/'
    journal_json = session.get(journal_link, headers=headers).json()

#Запись в файлик 
    # directory = 'MUCTRBot/JSON'
    # if not os.path.exists(directory):
    #     os.makedirs(directory)

    # journal_path = os.path.join(directory, "Journal.json")
    # with open(journal_path, 'w', encoding='utf-8') as file:
    #     json.dump(journal_json, file, indent=4, ensure_ascii=False)

# возвращаем список с предметами
    courses_numbers = [course['number'] for course in journal_json['courses']]

# Получаем список всех семестров
    semesters_names = []
    for course in journal_json['courses']:
        for semester in course['semesters']:
            semesters_names.append(semester['name'])

    # Получаем список всех предметов для каждого семестра
    semester_subjects = []
    for course in journal_json['courses']:
        for semester in course['semesters']:
            subjects = [subject['subject_name'] for subject in semester['subjects']]
            semester_subjects.append(subjects)

            
    return courses_numbers,  semesters_names, semester_subjects, group_id
        


def request_json(username, password):

#Создание юзер-агента и сессии
    user = fake_useragent.UserAgent().random
    session = requests.Session()
    
#Передача логина и пароля в дату при авторизации
    headers_auth = {
        'user-agent' : user
    }

    data_auth = {
        'username': username, 
        'password': password 
    }

#получение токена
    link = "https://api.muctr.ru/accounts/authenticate/login/"
    token =  session.post(link, headers= headers_auth, data = data_auth).json().get('token')
    # print(token)
    
#передача токена в заголовки (обязательный шаг)
    headers = {
        
        'authorization': f'Token {token}',
        'user-agent': user,
    }

#Получение eios_id
    eios_link = 'https://api.muctr.ru/education/students/student/'
    eios_id = session.get(eios_link, headers= headers).json()['educations'][0]['id']
    # print(eios_id)
#Получение журнала с баллами в виде .json
    journal_link = f'https://api.muctr.ru/education/students/education/{eios_id}/journal/full/'
    journal_json = session.get(journal_link, headers=headers).json()
   
    return journal_json





