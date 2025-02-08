import os

import requests
import logging
from geopy.distance import geodesic
from location.models import Location


logger = logging.getLogger(__name__)
apikey = os.getenv('APIKEY_YANDEXMAP')

def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    try:
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
        data = response.json()
        found_places = data['response']['GeoObjectCollection']['featureMember']
        if not found_places:
            logger.error(f"Адрес '{address}' не найден.")
            return None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        return float(lat), float(lon)
    except (requests.exceptions.RequestException, KeyError, IndexError, ValueError) as e:
        logger.error(f"Ошибка при запросе к API для адреса '{address}': {e}")
        return None


def get_or_create_location(address):
    location, created = Location.objects.get_or_create(address=address)
    if not location.latitude or not location.longitude:
        coordinates = fetch_coordinates(apikey, address)
        if coordinates:
            lat, lon = coordinates
            location.latitude = lat
            location.longitude = lon
            location.save()
    return (location.latitude, location.longitude) if location.latitude is not None and location.longitude is not None else None


def calculate_distances_to_restaurants(delivery_coords, restaurants):
    restaurant_addresses = [restaurant.address for restaurant in restaurants]
    locations = {
        loc.address: (loc.latitude, loc.longitude)
        for loc in Location.objects.filter(address__in=restaurant_addresses)
    }
    for restaurant in restaurants:
        restaurant_coords = locations.get(restaurant.address)
        if restaurant_coords:
            restaurant.distance = calculate_distance(delivery_coords, restaurant_coords)
        else:
            restaurant.distance = None


def sort_restaurants_by_distance(restaurants):
    return sorted(
        restaurants,
        key=lambda x: x.distance if x.distance is not None else float("inf")
    )


def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).km

