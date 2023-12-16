import telebot
from telebot import types
import g4f
import wikipediaapi
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
import requests
import json

with open('config.json') as f:
    config = json.load(f)
# # Прописываем все токены и Api

token = config['token_telegram']
client_id =config['client_id_spotify']
client_secret = config['client_secret_spotify']
api_key_yotube = config['api_key_yotube']
api_key_weather = config['api_key_weather']
wiki_key_project = config['Wiki_project']
timeout_seconds=15
video =[] # для ютюб
audio = [] # для spotify
user_query=[] # для списка запросов пользователя
button_name = ['Ask ChatGPT','Find on YouTube','Find artist on Spotify','Weather','Currency','Find on Wikipedia']

HELP = '''
Список доступных команд:
* /help - print help
* /q, /gpt- question to GPT
* /y, /youtube - question to Youtube
* /s - find in spotify
* /w, /w_ru, /вики, /w_en, /wiki - question to Wikipedia 
* /weather, /погода - question Weather
* /cur, /валюта - Currency
'''
my_commands=['/help','/q','/y','/youtube','/w','/w_en','/w_ru','/wiki','/вики',
             '/weather','/cur','/curr','/погода','/валюта','/s','/help','/валюта','/gpt']  # Для хендлера без /

bot=telebot.TeleBot(token)

#====================== Weather =================
def my_weather (prompt):
    base_url = f'https://api.openweathermap.org/data/2.5/weather?q={prompt}&appid={api_key_weather}'
    response = requests.get(base_url, timeout=timeout_seconds).json()
    my_temperature = response['main']['temp'] - 273.15
    my_temp_feels_like = response['main']['feels_like'] - 273.15
    my_weather = response['weather'][0]['main']
    my_wind = response['wind']['speed']
    my_humidity = response['main']['humidity']
    my_description = response['weather'][0]['description']
    answer = f'Temperature on {prompt} is : {my_temperature:.2f}  ❄️ \n '
    answer += f'Temperature on {prompt} feels like : {my_temp_feels_like:.2f} ❄️ \n'
    answer += f'Weather on {prompt} {my_weather} - {my_description} ☁ \n'
    answer +=f'Wind on {prompt} {my_wind} ms 💨 \n'
    answer +=f'Humidity on {prompt} {my_humidity} % 🌢 \n'
    return answer
#======================== Currency ===============================
def my_currency():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    # Загрузка файла по ссылке с установкой timeout
    response = requests.get(url, timeout=timeout_seconds)
    if response.status_code == 200:
        with open("daily_json.js", "wb") as f:
            f.write(response.content)
    # Открываем файл для чтения в бинарном режиме
    with open("daily_json.js", "rb") as f:
        # Декодируем JSON-данные
        data = json.loads(f.read().decode("utf-8"))
             #Теперь переменная data содержит распарсенные данные из файла JSON
        answer = '$ ' + f"{data['Valute']['USD']['Value']:.2f}" + ' rub' + '\n'
        answer += '€ ' + f"{data['Valute']['EUR']['Value']:.2f}" + ' rub' + '\n'
        answer += '₴ ' + f"{data['Valute']['UAH']['Value']:.2f}" + ' rub' + '\n'
        return answer
    #===================== Википедия ========
def my_wiki(my_command, prompt):
    if my_command in ('/w_en', '/w', '/wiki'):
        wiki_wiki = wiki_wiki = wikipediaapi.Wikipedia(f'{wiki_key_project}', 'en')
    else:
        wiki_wiki = wiki_wiki = wikipediaapi.Wikipedia(f'{wiki_key_project}','ru')  # RU Wiki
    page_py = wiki_wiki.page(prompt)
    if page_py.exists():
        answer = page_py.title + '\n' + page_py.text[:1000] + '\n' + page_py.fullurl
        return answer
    else:
        return f' Ничего не найдено. Попробуйте запрос еще раз'
 # =========================Spotify =================
def my_spotify(prompt):
    # print(prompt)
    audio.clear()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                                   client_secret=client_secret))
    # Ищем исполнителя
    results = sp.search(q=prompt, type='artist', limit=1)
    if results:
        answer = results['artists']['items'][0]['external_urls']['spotify']  # URL of spotify
        results = sp.search(q=prompt, limit=3)  #Top 3

        if results:
            for track in results['tracks']['items']:
                # answer = answer + '\n' + track['name'] + '\n' + track['external_urls']['spotify']
                audio.append(track['name'] + '\n' + track['external_urls']['spotify'])
        return answer
    else:
        return f'Исполнитель {prompt} не найден'
#=================== Youtube==============
def my_youtube(prompt):
    # Создаем объект Youtube Api
    youtube = build('youtube', 'v3', developerKey=api_key_yotube)
    search_query = prompt
    request = youtube.search().list(
        q=search_query,
        type='video',
        part='id,snippet',
        maxResults=5
    )
    response = request.execute()
    video.clear() # очищаем список
    for item in response['items']:
        video_id = item['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        video.append(video_url)
    return video
# ================ GPT =====
def my_gpt(prompt):
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],  # такой шаблон передачи
            stream=True,
        )
        answer = ''
        for element in response:
            # print(element, flush=True, end='')
            answer = answer + element
        return answer
    except requests.Timeout:
        return f"Время ожидания запроса истекло (timeout: {timeout_seconds} секунд)."
    except requests.RequestException as e:
        return f"Ошибка при выполнении запроса: {e}"
def my_help():
    return HELP

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(button_name[0])
    btn2 = types.KeyboardButton(button_name[1])
    btn3 = types.KeyboardButton(button_name[2])
    btn4 = types.KeyboardButton(button_name[3])
    btn5 = types.KeyboardButton(button_name[4])
    btn6 = types.KeyboardButton(button_name[5])

    markup.row(btn1, btn2, btn3)
    markup.row(btn4, btn5, btn6)
    bot.register_next_step_handler(message, on_click)
    bot.send_message(message.chat.id, f'Hi, {message.from_user.first_name} 👋', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def on_click(message):
    try:
        command=''    # Команда пользователя
        prompt = ''  # Запрос на поиск пользователя
        # Если выбрана команда - выполняем её ==============
        if message.text[0]== '/':
            command = message.text.split()[0].lower()  # Какая команда выбрана
            if command in my_commands:
                if len(message.text.split()) > 1:  # Если элементов более 1 выделяем что искать, т.к для валюты нет поиска
                    prompt = message.text.split(maxsplit=1)[1]  # Текст для поиска
                    user_query.append(prompt) # добавляем запрос в список
            else:
                bot.send_message(message.chat.id, 'Неверная команда. Используйте /help')
        else:
            if message.text not in button_name:
                user_query.append(message.text)  # Запрос на поиск пользователя
        if message.text == '/help':
            bot.send_message(message.chat.id, my_help())
        if message.text == 'Ask ChatGPT' or command in ('/q', '/gpt'):
            bot.send_message(message.chat.id, my_gpt(user_query[-1]))
        elif message.text == 'Find on YouTube' or command in ('/y','/youtube'):
            my_youtube(user_query[-1])  # Для вывода Топ 5 делаем цикл
            for item in video:
                bot.send_message(message.chat.id, item)
        elif message.text =='Weather' or command in ['/weather','/погода']:
            bot.send_message(message.chat.id, my_weather(user_query[-1]))
        elif message.text == 'Currency' or command in ['/cur','/валюта']:
            bot.send_message(message.chat.id, my_currency())
        elif message.text == 'Find on Wikipedia' or command in command in ['/w_ru','/w_en','/w','/wiki']:
            bot.send_message(message.chat.id, my_wiki(command, user_query[-1]))
        elif message.text == 'Find artist on Spotify' or command in ['/s']:
            bot.send_message(message.chat.id, my_spotify(user_query[-1]))
            bot.send_message(message.chat.id, 'Топ-3')
            for track in audio:
                bot.send_message(message.chat.id, track)
    except requests.Timeout:
        bot.send_message(message.chat.id, f"Время ожидания запроса истекло (timeout: {timeout_seconds} секунд).")
    except requests.RequestException as e:
        bot.send_message(message.chat.id, f"Ошибка при выполнении запроса: {e}")

def main():
    try:
        bot.polling(none_stop=True)
    except requests.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")

if __name__ == '__main__':
    main()