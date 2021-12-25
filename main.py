import pickle
from pprint import pprint

import requests
from kivy import Config
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.recycleview import RecycleView
from time import strftime, localtime
import locale
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition
from kivy_garden.graph import LinePlot
from geopy.geocoders import Nominatim

open_weather_key = '7ce6c84dd325b5a80620aa9add3c0b91'
geolocation_key = "at_FZR2D5uMI1iSZjnVpAq19UkT2OgJh"
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Builder.load_file('WindowsWeather.kv')


# Читаем данные из файла.
def load_data_file() -> dict:
    try:
        f = open('saved_data/saved_data.pcl', 'rb')  # открываем файл
        b = pickle.load(f)  # загружаем файл в словарь
        f.close()  # закрываем файл
    except (FileNotFoundError, EOFError):
        b = {}
    return b


# сохраняет данные в файл.
def save_data_files(a: list, name_rv):
    b = {}
    f = open('saved_data/saved_data.pcl', 'wb')  # открывает файл
    b[name_rv] = a
    pickle.dump(b, f)  # записывает данные в файл
    f.close()  # закрывает файл


def wind_deg_to_str(deg: int) -> str:
    wind = ''
    if 0 <= deg <= 12 or 348 <= deg <= 359:
        wind = 'С'
    elif 13 <= deg <= 32:
        wind = 'ССВ'
    elif 33 <= deg <= 57:
        wind = 'СВ'
    elif 58 <= deg <= 87:
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
    elif 238 <= deg <= 257:
        wind = 'ЮЗЗ'
    elif 258 <= deg <= 282:
        wind = 'З'
    elif 283 <= deg <= 302:
        wind = 'СЗЗ'
    elif 303 <= deg <= 327:
        wind = 'СЗ'
    elif 328 <= deg <= 347:
        wind = 'ССЗ'
    return wind


def update_data(city_name: str, list_data: list, add_or_not: bool) -> list:
    if add_or_not:
        if {'text': city_name} in list_data:
            list_data = list_data
        else:
            list_data.insert(0, {'text': city_name})
            if len(list_data) > 30:
                list_data = list_data[:30]
    else:
        if {'text': city_name} in list_data:
            list_data.remove({"text": city_name})
    return list_data


def geolocation_from_name(name_city: str) -> list:
    geolocator = Nominatim(user_agent='main')
    location = geolocator.geocode(name_city)
    location_list = [location.latitude, location.longitude]
    return [location_list, name_city]


def city_name_from_ip() -> list:
    city_geolocation = [55.765074, 37.703719]
    city_name = 'Москва'
    return [city_geolocation, city_name]


weather_dict = {}


def load_weather_dict(city_geolocation: list):
    global weather_dict
    if city_geolocation[0][0] is not None and city_geolocation[0][1] is not None:
        base_url = 'http://api.openweathermap.org/data/2.5/onecall?lat={}&lon={' \
                   '}&appid=7ce6c84dd325b5a80620aa9add3c0b91&units=metric&lang=ru&exclude=minutely,hourly,alerts'
        weather_now = base_url.format(city_geolocation[0][0], city_geolocation[0][1])
        weather_now = requests.get(weather_now)
        locale.setlocale(locale.LC_ALL, '')
        if weather_now.status_code == 200:
            weather_dict = weather_now.json()
            weather_dict['city_name'] = city_geolocation[1]
            pprint(weather_dict)
        else:
            pass


class MyDict(dict):
    def __missing__(self, key):
        return 'not found'


class ModalHistory(ModalView):
    weather_button = ObjectProperty()
    city_name = ''

    def close_modal(self):
        self.dismiss()


class WeatherNow(Screen):
    search_city = ObjectProperty()
    weather_label = ObjectProperty()
    history_rv = ObjectProperty()
    weather_now = ''

    def __init__(self, **kwargs):
        super(WeatherNow, self).__init__(**kwargs)
        load_weather_dict(city_name_from_ip())
        self.create_weather_now(weather_dict)
        print(weather_dict)
        self.weather_label.text = self.weather_now

    def create_weather_now(self, weather: dict):

        self.weather_now = 'Город   {city}    Дата:   {dt}\n{description}\nТемпература  {temp}℃ ' \
                           '   По ощущениям  {feels_like}℃\nИндекс ультрафиолета {uvi}     ' \
                           'Точка росы  {dew_point}℃\nВетер:  Скорость   {speed}м/с    ' \
                           'Направление    {deg}\nПорывы до  {gust}м/с\nДавление {pressure} K/pa    ' \
                           'Влажность {humidity}%\nВосход  {sunrise}    Закат {sunset}'
        format_now_dict = {'city': weather['city_name'],
                           'dt': strftime('%d.%m.%Y   %H:%M:%S', localtime(weather['current']['dt'])),
                           'description': weather['current']['weather'][0]['description'],
                           'temp': str(weather['current']['temp']),
                           'feels_like': str(weather['current']['feels_like']),
                           'dew_point': str(weather['current']['dew_point']),
                           'uvi': str(weather['current']['uvi']),
                           'speed': str(weather['current']['wind_speed']),
                           'deg': wind_deg_to_str(weather['current']['wind_deg']),
                           'gust': str(weather['current'].get('wind_gust', 'нет данных  ')),
                           'pressure': str(weather['current']['pressure']),
                           'humidity': str(weather['current']['humidity']),
                           'sunrise': strftime('%H:%M:%S', localtime(weather['current'].get('sunrise',
                                                                                            -10800))),
                           'sunset': strftime('%H:%M:%S', localtime(weather['current'].get('sunset',
                                                                                           -10800)))}
        self.weather_now = self.weather_now.format_map(format_now_dict)

    def update_weather_from_search(self):
        if self.search_city.text == '':
            pass
        else:
            load_weather_dict(geolocation_from_name(self.search_city.text))
            self.create_weather_now(weather_dict)
            self.weather_label.text = self.weather_now

    def update_weather_from_history(self, city_name):
        load_weather_dict(geolocation_from_name(city_name))
        print(weather_dict)
        self.create_weather_now(weather_dict)
        self.weather_label.text = self.weather_now


class CityNameButton(Button):
    modal_history = ModalHistory()

    def modal_window(self, city_name: str):
        self.modal_history.weather_button.text = 'Погода\n' + city_name
        self.modal_history.city_name = city_name
        self.modal_history.open()


class HistoryRV(RecycleView):
    weather_nw = WeatherNow()

    def __init__(self, **kwargs):
        super(HistoryRV, self).__init__(**kwargs)
        try:
            self.data = load_data_file()['history']
        except (KeyError, pickle.UnpicklingError):
            pass

    def update_rv(self, city_name, add_or_not):
        if city_name == '':
            pass
        else:
            self.data = update_data(city_name, self.data, add_or_not)
            save_data_files(list(self._get_data()), 'history')


class WeatherWeek(Screen):
    weather_daily = {}
    city_in_week = ObjectProperty()
    weather_now = WeatherNow()
    day0 = ObjectProperty()
    day1 = ObjectProperty()
    day2 = ObjectProperty()
    day3 = ObjectProperty()
    day4 = ObjectProperty()
    day5 = ObjectProperty()
    day6 = ObjectProperty()
    day7 = ObjectProperty()
    icon_0 = ObjectProperty()
    icon_1 = ObjectProperty()

    def __init__(self, **kwargs):
        super(WeatherWeek, self).__init__(**kwargs)

        self.create_weather_daily(weather_dict)
        self.city_in_week.text = "{}   Погода на неделю".format(self.weather_daily['city_name'])
        self.day0.text = self.weather_daily['day0']
        self.day1.text = self.weather_daily['day1']
        self.day2.text = self.weather_daily['day2']
        self.day3.text = self.weather_daily['day3']
        self.day4.text = self.weather_daily['day4']
        self.day5.text = self.weather_daily['day5']
        self.day6.text = self.weather_daily['day6']
        self.day7.text = self.weather_daily['day7']
        self.icon_0.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][0] + '.png'
        self.icon_1.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][1] + '.png'
        self.icon_2.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][2] + '.png'
        self.icon_3.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][3] + '.png'
        self.icon_4.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][4] + '.png'
        self.icon_5.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][5] + '.png'
        self.icon_6.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][6] + '.png'
        self.icon_7.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][7] + '.png'

    def update_weather(self):
        self.create_weather_daily(weather_dict)
        self.city_in_week.text = "{}   Погода на неделю".format(self.weather_daily['city_name'])
        self.day0.text = self.weather_daily['day0']
        self.day1.text = self.weather_daily['day1']
        self.day2.text = self.weather_daily['day2']
        self.day3.text = self.weather_daily['day3']
        self.day4.text = self.weather_daily['day4']
        self.day5.text = self.weather_daily['day5']
        self.day6.text = self.weather_daily['day6']
        self.day7.text = self.weather_daily['day7']
        self.icon_0.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][0] + '.png'
        self.icon_1.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][1] + '.png'
        self.icon_2.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][2] + '.png'
        self.icon_3.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][3] + '.png'
        self.icon_4.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][4] + '.png'
        self.icon_5.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][5] + '.png'
        self.icon_6.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][6] + '.png'
        self.icon_7.source = 'icons/MyIconWeather/' + self.weather_daily['icon_list'][7] + '.png'

    def create_weather_daily(self, weather: dict):
        icon_list = []
        day_str = '   {dt}\n\n   {description}\n  восход {sunrise}\n   закат {sunset}\n   утром {morn}℃\n   ' \
                  'по ощущениям {feels_morn}℃\n    днём {day}℃\n   по ощущениям {feels_day}℃\n   вечером {eve}℃\n   ' \
                  'по ощущениям {feels_eve}℃\n   ночью {night}℃\n   по ощущениям {feels_night}℃\n  ' \
                  'давление {pressure}K/pa\n   влажность {humidity}\n   ветер\n   скорость {speed}м/с\n   ' \
                  'направление {deg}\n   порывы до {gust}м/с\n   облачность {clouds}%\n   индекс у/ф {uvi}\n'
        for i in range(len(weather['daily'])):
            day_dict = {'sunrise': strftime('%H:%M:%S', localtime(weather['daily'][i].get('sunrise', -10800))),
                        'sunset': strftime('%H:%M:%S', localtime(weather['daily'][i].get('sunset', -10800))),
                        'dt': strftime('%A\n   %d.%m.%Y', localtime(weather['daily'][i]['dt'])),
                        'morn': str(weather['daily'][i]['temp']['morn']),
                        'feels_morn': str(weather['daily'][i]['feels_like']['morn']),
                        'day': str(weather['daily'][i]['temp']['day']),
                        'feels_day': str(weather['daily'][i]['feels_like']['day']),
                        'eve': str(weather['daily'][i]['temp']['eve']),
                        'feels_eve': str(weather['daily'][i]['feels_like']['eve']),
                        'night': str(weather['daily'][i]['temp']['night']),
                        'feels_night': str(weather['daily'][i]['feels_like']['night']),
                        'pressure': str(weather['daily'][i]['pressure']),
                        'humidity': str(weather['daily'][i]['humidity']),
                        'speed': str(weather['daily'][i]['wind_speed']),
                        'deg': wind_deg_to_str(weather['daily'][i]['wind_deg']),
                        'gust': str(weather['daily'][i]['wind_gust']),
                        'clouds': str(weather['daily'][i]['clouds']),
                        'uvi': str(weather['daily'][i]['uvi']),
                        'description': weather['daily'][i]['weather'][0]['description']}
            self.weather_daily['day' + str(i)] = day_str.format_map(day_dict)
            icon_list.append(weather_dict['daily'][i]['weather'][0]['icon'])
        self.weather_daily['city_name'] = weather['city_name']
        self.weather_daily['icon_list'] = icon_list


class History(Screen):
    history_rv = ObjectProperty()
    weather_week = WeatherWeek()


class WeatherGraphs(Screen):
    temp_graph = ObjectProperty(None)
    press_graph = ObjectProperty(None)
    graph_box = ObjectProperty()
    press_plot = LinePlot(line_width=2, color=[1, 0, 1, 1])
    temp_day_plot = LinePlot(line_width=2, color=[1, 0, 0, 1])
    temp_night_plot = LinePlot(line_width=3, color=[0, 0, 1, 1])
    dict_graph = {}

    def __init__(self, **kwargs):
        super(WeatherGraphs, self).__init__(**kwargs)
        self.update_weather()

    def data_for_graph(self, weather: dict):
        list_tuple_day = []
        list_max_min_day = []
        list_max_min_night = []
        list_tuple_night = []
        list_tuple_press = []
        for i in range(len(weather['daily'])):
            list_tuple_day.append((i + 1, weather['daily'][i]['temp']['day']))
            list_max_min_day.append(int(weather['daily'][i]['temp']['day']))
            list_max_min_night.append(int(weather['daily'][i]['temp']['night']))
            list_tuple_night.append((i + 1, weather['daily'][i]['temp']['night']))
            list_tuple_press.append((i + 1, weather['daily'][i]['pressure']))
        list_max_min = list_max_min_day + list_max_min_night
        print(list_max_min)
        self.dict_graph['tuple_day'] = list_tuple_day
        self.dict_graph['max_min'] = list_max_min
        self.dict_graph['tuple_night'] = list_tuple_night
        self.dict_graph['tuple_press'] = list_tuple_press
        pprint(self.dict_graph['tuple_press'])
        self.create_max_min_temp()

    def create_max_min_temp(self) -> list:
        temp_max = int(max(self.dict_graph['max_min']))
        temp_min = int(min(self.dict_graph['max_min']))
        list_max_min = []
        for i in range(1, 6):
            temp_max += 1
            if temp_max % 5 == 0:
                list_max_min.insert(0, temp_max)
            temp_min -= 1
            if temp_min % 5 == 0:
                list_max_min.insert(1, temp_min)
        print(list_max_min)
        return list_max_min

    def update_weather(self):
        self.data_for_graph(weather_dict)

        self.temp_graph.remove_plot(self.temp_day_plot)
        self.temp_graph.remove_plot(self.temp_night_plot)
        # self.temp_graph.xlabel = 'Дни'
        self.temp_graph.ylabel = 'Температура'
        self.temp_graph.x_ticks_minor = 1
        self.temp_graph.x_ticks_major = 1
        self.temp_graph.y_ticks_major = 10
        self.temp_graph.y_ticks_minor = 5
        self.temp_graph.y_grid_label = True
        self.temp_graph.x_grid_label = True
        self.temp_graph.padding = 7
        self.temp_graph.x_grid = True
        self.temp_graph.y_grid = True
        self.temp_graph.xmin = 1
        self.temp_graph.xmax = 8
        self.temp_graph.ymin = self.create_max_min_temp()[1]
        self.temp_graph.ymax = self.create_max_min_temp()[0]
        self.temp_day_plot.points = self.dict_graph['tuple_day']
        self.temp_night_plot.points = self.dict_graph['tuple_night']
        self.temp_graph.add_plot(self.temp_day_plot)
        self.temp_graph.add_plot(self.temp_night_plot)

        self.press_graph.remove_plot(self.press_plot)
        # self.press_graph.xlabel = 'Дни'
        self.press_graph.ylabel = 'Давление'
        self.press_graph.x_ticks_minor = 1
        self.press_graph.x_ticks_major = 1
        self.press_graph.y_ticks_major = 50
        self.press_graph.y_ticks_minor = 10
        self.press_graph.y_grid_label = True
        self.press_graph.x_grid_label = True
        self.press_graph.x_grid = True
        self.press_graph.y_grid = True
        self.press_graph.xmin = 1
        self.press_graph.xmax = 8
        self.press_graph.ymin = 950
        self.press_graph.ymax = 1050
        self.press_graph.label_options({})
        self.press_plot.on_clear_plot()
        self.press_plot.points = self.dict_graph['tuple_press']
        self.press_graph.add_plot(self.press_plot)


class WindowsWeatherApp(App):
    icon = 'icons/cloud_weather_32.png'

    def build(self):
        screen_mn = ScreenManager(transition=RiseInTransition())
        screen_mn.add_widget(WeatherNow(name='now'))
        screen_mn.add_widget(WeatherWeek(name='week'))
        screen_mn.add_widget(WeatherGraphs(name='graphs'))
        screen_mn.add_widget(History(name='history'))
        return screen_mn


if __name__ == '__main__':
    WindowsWeatherApp().run()
