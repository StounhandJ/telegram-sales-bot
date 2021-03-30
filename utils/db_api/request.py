import requests

server = "http://localhost:3000"


def request(method, uri, params=None):
    if params is None:
        params = {}

    response = None
    if method == "POST":
        response = requests.post(server+uri, params=params).json()
    elif method == "GET":
        response = requests.get(server+uri, params=params).json()
    return response
