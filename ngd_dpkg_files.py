from osdatahub import DataPackageDownload
from urllib.request import urlopen
import json

key = 'gP228DpHXZ2BWdrmffMmUNhzAFyuuE27'
dp = "929"
v = "2361"
data = DataPackageDownload.all_products(key)

for item in data:
    if type(item) is dict:
        if item["id"] == dp and item["versions"][0]["id"] == v:
            dlUrl = item["versions"][0]["url"]
            print("dp:", dp, "/v" ,v)

webURL = urlopen(dlUrl)
dl = webURL.read()
encoding = webURL.info().get_content_charset('utf-8')
files = json.loads(dl.decode(encoding))

for f in files['downloads']:
    print("...", f["url"][48:])
