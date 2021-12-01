import pickle
import requests
import geocoder
from kivy import Config
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.recycleview import RecycleView
from time import strftime, localtime
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import ScreenManager, Screen


# Читаем данные из файла.
def load_data_file() -> dict:
    try:
        f = open('saved_data/saved_data.pcl', 'rb')  # открываем файл
        b = pickle.load(f)  # загружаем файл в словарь
        f.close()  # закрываем файл
    except (FileNotFoundError, EOFError):
        b = {}
    print(b)
    return b


# сохраняет данные в файл.
def save_data_files(a: list, name_rv):
    b = {}
    f = open('saved_data/saved_data.pcl', 'wb')  # открывает файл
    b[name_rv] = a
    print('b', b)
    pickle.dump(b, f)  # записывает данные в файл
    f.close()  # закрывает файл


my_key = '7ce6c84dd325b5a80620aa9add3c0b91'


def wind_deg_to_str(deg: int) -> str:
    wind = ''
    if 0 <= deg <= 12 or 348 <= deg <= 359:
        wind = 'С'
    elif 13 <= deg <= 32:
        wind = 'ССВ'
    elif 33 <= deg <= 57:
        wind = 'СВ'
    elif 56 <= deg <= 77:
        wind = 'СВВ'
    elif 88 <= deg <= 102:
        wind = 'В'
    elif 103 <= deg <= 122:
        wind = 'ЮВВ'
    elif 123 <= deg <= 147:
        wind = 'ЮВ'
    elif 146 <= deg <= 167:
        wind = 'ЮЮВ'
    elif 168 <= deg <= 192:
        wind = 'Ю'
    elif 193 <= deg <= 212:
        wind = 'ЮЮЗ'
    elif 213 <= deg <= 237:
        wind = 'ЮЗ'
    elif 237 <= deg <= 257:
        wind = 'ЮЗЗ'
    elif 258 <= deg <= 282:
        wind = 'З'
    elif 283 <= deg <= 302:
        wind = 'СЗЗ'
    elif 303 <= deg <= 327:
        wind = 'СЗ'
    elif 328 <= deg <= 347:
        wind = 'ССЗ'
    print(wind)
    return wind


def city_name_here() -> str:
    g = geocoder.ip('me')
    return g.city


def update_data(city_name: str, list_data: list) -> list:
    if {'text': city_name} in list_data:
        list_data = list_data
    else:
        list_data.insert(0, {'text': city_name})
        if len(list_data) > 20:
            list_data = list_data[:20]
    return list_data


def weather_from_search(city_name) -> str:
    base_url = 'http://api.openweathermap.org/data/2.5/weather?q={' \
               '}&appid=7ce6c84dd325b5a80620aa9add3c0b91&lang=ru&units=metric'
    weather_now = base_url.format(city_name)
    req_now = requests.get(weather_now)
    if req_now.status_code == 200:
        print(req_now.json())
        print(type(req_now.json()))
        # base_icon_url = ' http://openweathermap.org/img/wn/{}@2x.png'
        # icon_now_url = base_icon_url.format(req_now.json()['weather'][0]['icon'])
        # # icon_weather = AsyncImage(source=icon_now_url)

        weather_str = 'Город:   {city}({country})    Время:   {dt}\n{description}\nТемпература:  {temp}℃ ' \
                      '   По ощущениям:  {feels_like}℃\nТемпература макс: {temp_max}℃     ' \
                      'Температура мин:  {temp_min}℃\nВетер  Скорость:   {speed}м/с    ' \
                      'Направление:    {deg}\nПорывы до:  {gust}м/с\nДавление: {pressure} K/pa    ' \
                      'Влажность: {humidity}%\nВосход:    {sunrise}    Закат: {sunset}'

        format_dict = MyDict({'city': req_now.json()['name'], 'country': req_now.json()['sys']['country'],
                              'dt': strftime('%d.%m.%Y   %H:%M:%S', localtime(req_now.json()['dt'])),
                              'description': req_now.json()['weather'][0]['description'],
                              'temp': str(req_now.json()['main']['temp']),
                              'feels_like': str(req_now.json()['main']['feels_like']),
                              'temp_max': str(req_now.json()['main']['temp_max']),
                              'temp_min': str(req_now.json()['main']['temp_min']),
                              'speed': str(req_now.json()['wind']['speed']),
                              'deg': wind_deg_to_str(req_now.json()['wind']['deg']),
                              'gust': str(req_now.json().get('wind').get('gust', '    ')),
                              'pressure': str(req_now.json()['main']['pressure']),
                              'humidity': str(req_now.json()['main']['humidity']),
                              'sunrise': strftime('%H:%M:%S', localtime(req_now.json()['sys']['sunrise'])),
                              'sunset': strftime('%H:%M:%S', localtime(req_now.json()['sys']['sunset']))})
        return weather_str.format_map(format_dict)


Config.set('input', 'mouse', 'mouse,disable_multitouch')
Builder.load_file('WindowsWeather.kv')


class MyDict(dict):
    def __missing__(self, key):
        return 'not found'


class ModalHistory(ModalView):
    weather_button = ObjectProperty()

    def close_modal(self):
        self.dismiss()


class WeatherNow(Screen):
    search_city = ObjectProperty()
    weather_label = ObjectProperty()
    history_rv = ObjectProperty()

    def __init__(self, **kwargs):
        super(WeatherNow, self).__init__(**kwargs)
        self.weather_label.text = weather_from_search(city_name_here())

    def update_weather(self):
        self.weather_label.text = weather_from_search(self.search_city.text)

    def update_weather_from_history(self, city_name: str):
        self.weather_label.text = weather_from_search(city_name)


class CityNameButton(Button):
    modal_history = ModalHistory()

    def modal_window(self, city_name: str):
        self.modal_history.weather_button.text = 'Погода\n' + city_name
        self.modal_history.open()


class HistoryRV(RecycleView):
    weather_nw = WeatherNow()

    def __init__(self, **kwargs):
        super(HistoryRV, self).__init__(**kwargs)
        try:
            self.data = load_data_file()['history']
        except (KeyError, pickle.UnpicklingError):
            pass

    def update_rv(self, city_name):
        self.data = update_data(city_name, self.data)
        save_data_files(list(self._get_data()), 'history')


class WeatherWeek(Screen):
    pass


class History(Screen):
    history_rv = ObjectProperty()


class WindowsWeatherApp(App):
    icon = 'icons/cloud_weather_32.png'

    def build(self):
        screen_mn = ScreenManager()
        screen_mn.add_widget(WeatherNow(name='now'))
        screen_mn.add_widget(History(name='source'))
        screen_mn.add_widget(WeatherWeek(name='week'))
        return screen_mn


if __name__ == '__main__':
    WindowsWeatherApp().run()
