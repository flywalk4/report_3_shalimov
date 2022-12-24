import requests
import json
import csv
import datetime
from time import sleep
def request_vacancies(date_from : datetime, date_to : datetime):
    hour_from = str(date_from.hour).zfill(2)
    hour_to = str(date_to.hour).zfill(2)
    day_from = str(date_from.day).zfill(2)
    day_to = str(date_to.day).zfill(2)
    request = requests.get('https://api.hh.ru/vacancies', 
    params={'specialization':1, 
            "per_page":100,
            'date_from':f"2022-12-{day_from}T{hour_from}:00:00+0000",
            'date_to':f"2022-12-{day_to}T{hour_to}:00:00+0000"})
    return request

def form_vacancy(item):
    try:
        salary_from = item["salary"]["from"]
    except:
        salary_from = ""

    try:
        salary_to = item["salary"]["to"]
    except:
        salary_to = ""
        
    try:
        salary_currency = item["salary"]["currency"]
    except:
        salary_currency = ""  
    
    try:
        area_name = item["address"]["city"]
    except:
        area_name = "" 

    return [item["name"], salary_from, salary_to, salary_currency, area_name,item["published_at"]]

def input_datetime():
    print("Press <enter> for default")
    year = input("Введите год (default=2022): ")
    year = 2022 if year == "" else int(year)
    month = input("Введите месяц (default=12): ")
    month = 12 if month == "" else int(month)
    day = input("Введите день (default=22): ")
    day = 22 if day == "" else int(day)
    return datetime.datetime(year, month, day)

def get_day_range(date : datetime):
    day_range = []
    for hour in range(1,24):
        if hour == 24:
            day_range.append([datetime.datetime(date.year, date.month, date.day, 23, 0, 0),
                            datetime.datetime(date.year, date.month, date.day, 23, 59, 59)])
            continue
        day_range.append([datetime.datetime(date.year, date.month, date.day, hour - 1, 0, 0),
                        datetime.datetime(date.year, date.month, date.day, hour, 0, 0)])
    return day_range
    
def make_requests(day_range):
    items = []
    for request_params in day_range:
        request = request_vacancies(*request_params)
        if request.status_code == 200:
            items += json.loads(request.text)["items"]
        else:
            print("Request rejected, sleeping 2 seconds and retrying")
            sleep(2)
            request = request_vacancies(*request_params)
            if request.status_code == 200:
                items += json.loads(request.text)["items"]
            else:
                print(f"Request rejected with params: {request_params}")
    return items

def write_vacancies(items):
    if len(items) == 0:
        print("Нет данных")
        return
    myFile = open('vacancies.csv', 'w', encoding="UTF-8")
    writer = csv.writer(myFile, lineterminator='\n')
    writer.writerow(['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at'])
    for item in items:
        writer.writerow(form_vacancy(item))
    myFile.close()
 
date = input_datetime()
day_range = get_day_range(date)
items = make_requests(day_range)
write_vacancies(items)