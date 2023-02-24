from osdatahub import DataPackageDownload
from dotenv import load_dotenv
from urllib.request import urlopen
import gdaltools
import psycopg2 as pg
import json
import requests
import os, platform, zipfile

print(platform.system()) 

# Path and database parameters
if platform.system() == 'Linux':
    dlCachePath = '/home/simon/data/ngd/features/'
    gpkgPath = '/home/simon/data/ngd/features/'
    unzipped = 'unzipped/'
    pghost = "localhost"
else:
    dlCachePath = 'C:\\os_ngd_features\\'
    gpkgPath =  "C:\\os_ngd_features\\"
    unzipped = 'unzipped'
    pghost = "sw2-gis.wychavon.gov.uk"
    gdaltools.Wrapper.BASEPATH = "C:\Program Files\GDAL"

pgport = 5432
pgdbname="ngd"
pgschema="features"
pguser="postgres"
pgpassword="postgres.."

load_dotenv()

# OS Datapackage parameters
#key = 'gP228DpHXZ2BWdrmffMmUNhzAFyuuE27'
key = os.getenv('key')
dp = "929"
v = "2361"
data = DataPackageDownload.all_products(key)

# Get downloads URL for Datapackage and version ... 
for item in data:
    if type(item) is dict:
        if item["id"] == dp and item["versions"][0]["id"] == v:
            dlUrl = item["versions"][0]["url"]
            print("dp:", dp, "v" ,v)

# ... and get URLs for each file (as specified in datapackage) to download ...
filesURL = urlopen(dlUrl)
dl = filesURL.read()
encoding = filesURL.info().get_content_charset('utf-8')
files = json.loads(dl.decode(encoding))

# ... write each file to local folder from URL endpoint...
for f in files['downloads']:
    r = requests.get(f["url"], allow_redirects=True)
    file = open(dlCachePath + f["fileName"], 'wb').write(r.content)
    print("...", f["url"][48:])

# ... extract each geopackage from zip file ... 
for item in os.listdir(dlCachePath):
    if item != 'unzipped':
        with zipfile.ZipFile(os.path.join(dlCachePath, item), 'r') as zObject:
            zObject.extractall(path= dlCachePath + unzipped)

# ... create ogr2ogr instance to load each gpkg into tables in features schema in ngd database, overwriting by default, table names following NGD naming scheme.  
ogr = gdaltools.ogr2ogr()
ogr.set_encoding("UTF-8")
conn = gdaltools.PgConnectionString(host=pghost, port=pgport, dbname=pgdbname, schema=pgschema, user=pguser, password=pgpassword)
srs = 'EPSG:27700'

dropConn = pg.connect(host=pghost, dbname=pgdbname, user=pguser, password=pgpassword, port=pgport)
cur = dropConn.cursor()
cur.execute("DROP SCHEMA features CASCADE; COMMIT; CREATE SCHEMA features AUTHORIZATION postgres; COMMIT;")
dropConn.commit()
cur.close()
dropConn.close()

for gpkg in os.listdir(os.path.join(gpkgPath, unzipped)):
    gpkgname = os.path.join(gpkgPath, unzipped,  gpkg)
    print("> ", gpkgname)
    tablename = gpkg[:-5]
    ogr.set_input(gpkgname, srs=srs)
    #ogr2ogr -append PG:dbname=foo abc.shp --config OGR_TRUNCATE YES
    #ogr.MODE_LAYER_OVERWRITE
    ogr.set_output(conn, table_name=tablename, srs=srs)
    print(conn,  tablename,  srs)    
    ogr.execute()