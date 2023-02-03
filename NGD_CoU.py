from urllib.request import urlopen
import pprint
import requests
from osdatahub import DataPackageDownload
import json

key = 'gP228DpHXZ2BWdrmffMmUNhzAFyuuE27'
data = DataPackageDownload.all_products(key)
#print(type(data))
#pprint.pprint(data)

for item in data:
    if type(item) is dict:
        if item["id"] == "929" and item["versions"][0]["id"] == "2361":
            dlUrl = item["versions"][0]["url"]
            #print(item)
            print("-------------------------------------------------------------------------")
            print(dlUrl)

webURL = urlopen(dlUrl)
dl = webURL.read()
encoding = webURL.info().get_content_charset('utf-8')
JSON_object = json.loads(dl.decode(encoding))

for u in JSON_object:
    if u == "downloads":
        for i in u:
            pprint.pprint(i)
    print("-----------------------")