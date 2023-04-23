import requests


def geocoder(text):
    geocoder_uri = "http://geocode-maps.yandex.ru/1.x/"

    response = get_response(geocoder_uri, params={
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "geocode": text
    })
    try:
        if not response["response"]["GeoObjectCollection"]["featureMember"]:
            return 'К сожалению ничего не нашлось('
    except Exception:
        return f'Ошибка: {response}'
    toponym = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    text = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['metaDataProperty'][
        'GeocoderMetaData']['text']
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    delta = "0.03"
    ll, spn = f'{toponym_longitude},{toponym_lattitude}', f'{delta},{delta}'
    # Можно воспользоваться готовой функцией,
    # которую предлагалось сделать на уроках, посвящённых HTTP-геокодеру.

    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}" \
                         f"&l=sat&pt={toponym_longitude},{toponym_lattitude},flag"
    return static_api_request


def get_response(url, params):
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as error:
        raise error
