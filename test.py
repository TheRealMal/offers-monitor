import requests

headers = {
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://www.cian.ru',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.cian.ru/',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

json_data = {
    'jsonQuery': {
        '_type': 'flatrent',
        'engine_version': {
            'type': 'term',
            'value': 2,
        },
        'region': {
            'type': 'terms',
            'value': [
                1,
            ],
        },
        'price': {
            'type': 'range',
            'value': {
                'lte': 65000,
            },
        },
        'currency': {
            'type': 'term',
            'value': 2,
        },
        'for_day': {
            'type': 'term',
            'value': '!1',
        },
        'room': {
            'type': 'terms',
            'value': [
                1,
                2,
            ],
        },
    },
}
import time
for i in range(1000):
    response = requests.post(
        'https://api.cian.ru/search-offers/v2/search-offers-desktop/',
        headers=headers,
        json=json_data,
        verify=False
    )
    print(response.text, response.status_code)
    time.sleep(5)