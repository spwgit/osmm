from osdatahub import DataPackageDownload
from urllib.request import urlopen
import gdaltools
import json
import requests
import os, zipfile

key = 'gP228DpHXZ2BWdrmffMmUNhzAFyuuE27'
dp = "929"
v = "2361"
data = DataPackageDownload.all_products(key)

for item in data:
    if type(item) is dict:
        if item["id"] == dp and item["versions"][0]["id"] == v:
            dlUrl = item["versions"][0]["url"]
            print("dp:", dp, "/v" ,v)

filesURL = urlopen(dlUrl)
dl = filesURL.read()
encoding = filesURL.info().get_content_charset('utf-8')
files = json.loads(dl.decode(encoding))
dlCachePath = 'c:/os_ngd_features/'

for f in files['downloads']:
    r = requests.get(f["url"], allow_redirects=True)
    file = open(dlCachePath + f["fileName"], 'wb').write(r.content)
    print("...", f["url"][48:])

for item in os.listdir(dlCachePath):
   with zipfile.ZipFile(dlCachePath + item, 'r') as zObject:
        zObject.extractall(path= dlCachePath + "/unzipped/")

#gdaltools.Wrapper.BASEPATH = "C:\Program Files\GDAL"

ogr = gdaltools.ogr2ogr()
ogr.set_encoding("UTF-8")
conn = gdaltools.PgConnectionString(host="sw2-gis.wychavon.gov.uk", port=5432, dbname="ngd", schema="features", user="postgres", password="postgres..")
srs = 'EPSG:27700'
gpkgPath = "c:\\os_ngd_features\\"

for gpkg in os.listdir(gpkgPath + "unzipped\\"):
    gpkgname = gpkgPath + "unzipped\\" + gpkg
    tablename =  table_name=gpkg[:-5]
    ogr.set_input(gpkgname, srs=srs)
    print(gpkgname, srs)
    ogr.set_output(conn, table_name=tablename, srs=srs)
    print(conn, tablename, srs)    
    ogr.execute()
    
