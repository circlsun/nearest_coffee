import os
import json
import requests
import folium

from geopy import distance
from flask import Flask
from dotenv import load_dotenv


FILE_NAME = "coffee.json"


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url,
                            params={
                                "geocode": address,
                                "apikey": apikey,
                                "format": "json",
                            })
    response.raise_for_status()
    found_places = response.json(
    )['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_all_caffes():
    with open(FILE_NAME, "r", encoding="CP1251") as file:
        file_contents = file.read()
    return json.loads(file_contents)


def get_caffe_list(get_all_caffes, my_coords):
    caffes_list = []
    for caffe in get_all_caffes():
        caffes_dict = {}
        caffe_coord = [
            caffe["geoData"]["coordinates"][1],
            caffe["geoData"]["coordinates"][0]
        ]
        caffes_dict["title"] = caffe["Name"]
        caffes_dict["distance"] = distance.distance(my_coords, caffe_coord).km
        caffes_dict["latitude"] = caffe['geoData']['coordinates'][1]
        caffes_dict["longitude"] = caffe['geoData']['coordinates'][0]
        caffes_list.append(caffes_dict)
    return caffes_list


def get_distance(caffes_list):
    return caffes_list["distance"]


def get_caffes_map(get_all_caffes, my_coords):
    sorted_caffes = sorted(get_caffe_list(get_all_caffes, my_coords),
                           key=get_distance)
    caffes_location = folium.Map(location=my_coords, zoom_start=17)

    for caffe in sorted_caffes[:5]:
        folium.Marker(
            location=[caffe["latitude"], caffe["longitude"]],
            popup=caffe["title"],
            icon=folium.Icon(color="green", icon="info-sign"),
        ).add_to(caffes_location)
        folium.Marker(
            location=my_coords,
            popup="My_location",
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(caffes_location)

    caffes_location.save("map_caffes.html")


def get_map():
    with open("map_caffes.html") as file:
        return file.read()


def main():
    load_dotenv()
    api_key = os.environ['API_KEY_YANDEX']
    my_location = input("Где вы находитесь? ")
    my_coords = list(fetch_coordinates(api_key, my_location))
    my_coords[0], my_coords[1] = my_coords[1], my_coords[0]
    app = Flask(__name__)
    get_caffes_map(get_all_caffes, my_coords)
    app.add_url_rule("/", "Кофейни", get_map)
    app.run("0.0.0.0")


if __name__ == "__main__":
    main()
