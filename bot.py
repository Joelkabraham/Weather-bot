import json
import requests
from datetime import datetime
import requests
import pandas as pd
questionsUrl = './questionsComma.csv'
df = pd.read_csv(questionsUrl, sep=",",
                 skipinitialspace=True)
# print(df['Question'].str.lower() == "hi")
# import pytz
# cet = pytz.timezone('CET')
# url = "https://api.telegram.org/bot2020338407:AAGonMkXK5auCPbkpusrA3jDaVwlHovqeu0/sendMessage"
last_read_id = -1
url = "https://api.telegram.org/bot6143320760:AAGR0uJas9B4sMS2_4clIi6CMYohswfzdt0"
try_again_text = "-1"

def auto_answer(message):
    # String = decodedResponse['result'][0]['message']['text']
    # if(String[-1] == '?'):

    answer = df.loc[df['Question'].str.lower().replace(
        to_replace='\?', value='', regex=True)
        == message.lower()]

    if not answer.empty:
        answer = answer.iloc[0]['Answer']
        return answer
    else:
        return "Sorry, I could not understand you !!! I am still learning and try to get better in answering."

def start(last_message, chat_id):
    global url
    global last_read_id
    if ("/start" in last_message['message']['text']) and (last_read_id != last_message['update_id']):

        last_read_id = last_message['update_id']
        parameters = {                                                                                       

            "chat_id": chat_id,
            "text": "Hey! How can i help you today.!"
        }
        response = requests.get(url+"/sendMessage", data=parameters)

listOfDates = []
parameters = []
forecasts = []

def forecast(last_message, chat_id):
    global url
    global parameters
    global last_read_id
    global listOfDates
    if ("/forecast" in last_message['message']['text']) and (last_read_id != last_message['update_id']):
        last_read_id = last_message['update_id']
        forecastUrl = "https://api.openweathermap.org/data/2.5/forecast?lat=9.584655516276362&lon=76.98282388465755&appid=d19877b60e33d88d860eff5661a77a05&units=metric"
        res = requests.get(
            forecastUrl)
        weatherDataList = json.loads(res.text)
        listOfForecast = weatherDataList['list']
        for i in range(len(listOfForecast)):
            forecasts.append(listOfForecast[i])
            t1 = datetime.strptime(listOfForecast[i]['dt_txt'],
                                   '%Y-%m-%d %H:%M:%S')

            listOfDates.append("%s-%s-%s" % (t1.day, t1.month, t1.year))
        listOfDates = list(set(listOfDates))

        for i in range(len(listOfDates)):
            parameters.append(
                {"text": listOfDates[i], "callback_data": listOfDates[i]})
        # send_buttons(chat_id, parameters, "Predict weather on")
        listDate = []
        listOflistDate = []
        for i in range(1, len(listOfDates)+1):
            listDate.append(
                {"text": listOfDates[i-1], "callback_data": listOfDates[i-1]})
            if i % 3 == 0 and i != 0:
                listOflistDate.append(listDate)
                listDate = []
        send_buttons(
            chat_id, listOflistDate, "Predict weather on")

def send_buttons(chat_id, callback_object, text):

    keyboard = json.dumps(
        {'inline_keyboard': callback_object})
    parameters = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": keyboard
    }

    response = requests.post(url+"/sendMessage", data=parameters)

def weather(last_message, chat_id):
    global url
    global last_read_id
    global try_again_text
    res = requests.get(
        'https://api.openweathermap.org/data/2.5/weather?q=idukki&appid=d19877b60e33d88d860eff5661a77a05&units=metric')
    weatherData = json.loads(res.text)

    if ("/weather" in last_message['message']['text']) and (last_read_id != last_message['update_id']):

        last_read_id = last_message['update_id']
        parameters = {
            "chat_id": chat_id,
            "text": "Enter the city you want to know the weather of"
        }
        response = requests.get(url+"/sendMessage", data=parameters)
        # waiting for reply
        last_read_id = last_message['update_id']
        while True:
            q = requests.get(url+"/getUpdates?offset=-1")
            qJson = q.json()
            if('/weather' not in qJson['result'][0]['message']['text']):
                weatherQuery = qJson['result'][0]['message']['text']
                res = requests.get(
                    'https://api.openweathermap.org/data/2.5/weather?q='+str(weatherQuery) + '&appid=d19877b60e33d88d860eff5661a77a05&units=metric')
                weatherData = json.loads(res.text)
                last_read_id = last_message['update_id']
                if (weatherData['cod'] == 200):

                    parameters = {
                        "chat_id": chat_id,
                        "photo": "https://openweathermap.org/img/wn/"+weatherData['weather'][0]['icon']+"@2x.png"
                    }
                    response = requests.get(
                        url+"/sendPhoto", data=parameters)

                    sr = int(weatherData['sys']['sunrise'])
                    ss = int(weatherData['sys']['sunset'])
                    sunrise = datetime.fromtimestamp(
                        sr).strftime('%H:%M:%S')
                    sunset = datetime.fromtimestamp(
                        ss).strftime('%H:%M:%S')
                    parameters = {
                        "chat_id": chat_id,
                        "text": "🏙 City name: "+weatherQuery+"\n🔥 Temperature: "+str(weatherData['main']['temp'])+"°C\n💡 Feels like: "+str(weatherData['main']['feels_like'])+"\n🤯 Pressure: "+str(weatherData['main']['pressure'])+"\n💧 Humidity: "+str(weatherData['main']['humidity'])+"\n🌫 Visibility: "+str(weatherData['visibility'])+"m\n🌬 Wind Speed: "+str(weatherData['wind']['speed'])+"\n💨 Wind degree: "+str(weatherData['wind']['deg'])+"\n☁️ Clouds: "+str(weatherData['clouds']['all'])+"\n⛅️ Sunrise: "+sunrise+"\n🌘 Sunset: "+sunset
                    }
                    response = requests.get(
                        url+"/sendMessage", data=parameters)

                    try_again_text = "-1"
                    break
                elif(weatherData['cod'] == 401):
                    if try_again_text != str(weatherQuery):
                        parameters = {
                            "chat_id": chat_id,
                           "text": "No city found try another city"
                        }
                        response = requests.get(.
                            url+"/sendMessage", data=parameters)
                        try_again_text = str(weatherQuery)
                else:
                    print("Some problem in bot")

question = '-1-1-2-4214'
while True:

    # url = "https://api.telegram.org/bot6143320760:AAGR0uJas9B4sMS2_4clIi6CMYohswfzdt0/getUpdates?offset=-1"
    # url = "https://api.telegram.org/bot6143320760:AAGR0uJas9B4sMS2_4clIi6CMYohswfzdt0/getUpdates?offset=-1"

    response = requests.get(url+"/getUpdates?offset=-1")
    decodedResponse = response.json()
    timeRanges = []
    if ('callback_query' in decodedResponse['result'][0]):
        last_message = decodedResponse['result'][0]
        data_from_callback = last_message['callback_query']['data']
        chat_id = last_message['callback_query']['message']['chat']['id']
        print(data_from_callback)
        for forecast in forecasts:
            t1 = datetime.strptime(forecast['dt_txt'],
                                   '%Y-%m-%d %H:%M:%S')
            if "%s-%s-%s" % (t1.day, t1.month, t1.year) == data_from_callback:
                timeRanges.append("%s-%s-%s" % (t1.hour, t1.minute, t1.second))
        print(timeRanges)
        break
    else:
        if(len(decodedResponse['result']) != 0):
            last_message = decodedResponse['result'][0]
            chat_id = last_message['message']['chat']['id']
            String = decodedResponse['result'][0]['message']['text']
            s1 = slice(1)
            if(String[s1] == '/'):
                if('/start' in decodedResponse['result'][0]['message']['text']):
                    start(last_message, chat_id=chat_id)
                if('/forecast' in decodedResponse['result'][0]['message']['text']):
                    forecast(last_message, chat_id=chat_id)
                if('/weather' in decodedResponse['result'][0]['message']['text']):
                    # takeQuery()
                    weather(last_message, chat_id=chat_id)
            else:
                if question != decodedResponse['result'][0]['message']['text']:

                    msg = auto_answer(
                        decodedResponse['result'][0]['message']['text'])

                    parameters = {
                        "chat_id": chat_id,
                        "text": msg
                    }
                    response = requests.get(
                        url+"/sendMessage", data=parameters)
                    question = decodedResponse['result'][0]['message']['text']

# url = 'https://raw.githubusercontent.com/vikasjha001/telegram/main/qna_chitchat_professional.tsv'
# HACAq0EwiDrOfYaBkZNqeshIM46bCexa
# {'ok': True, 'result': [{'update_id': 227072419, 'callback_query': {'id': '8106460477530363864', 'from':
# {'id': 1887432410, 'is_bot':# False, 'first_name': 'Gokul', 'language_code': 'en'},
# 'message': {'message_id': 516, 'from': {'id': 6143320760, 'is_bot': True, 'first_name':# 'weatherwizard', 'username': 'wind_whisperer_bot'},
# 'chat': {'id': 1887432410, 'first_name': 'Gokul', 'type': 'private'}, 'date': 1677519218,
# 'text': 'Predict weather on', 'reply_markup': {'inline_keyboard':[[{'text': '28', 'callback_data': 'vide3o'}, {'text': '29', 'callback_data':# 'playlist'}]]}}, 'chat_instance': '6416464067071861225', 'data': 'vide3o'}}]}
