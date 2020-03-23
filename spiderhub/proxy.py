import requests
import json

host = '127.0.0.1'
port = '5010'
get_ip_endpoint = '/get'
del_ip_endpoint = '/delete?proxy=%s'


def get_proxy():
    response = requests.get("http://%s:%s%s" % (host, port, get_ip_endpoint))
    content = json.loads(response.content.decode())
    return content['proxy']


def delete_proxy(proxy):
    requests.get("http://%s:%s%s" % (host, port, del_ip_endpoint % proxy))

