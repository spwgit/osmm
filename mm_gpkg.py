from osdatahub import DataPackageDownload
from dotenv import load_dotenv
from urllib.request import urlopen
import gdaltools
import psycopg2 as pg
import json
import pprint
import requests
import os, platform, zipfile
from datetime import datetime

def getLastestURL(latestDate):
    for item in data:
        if type(item) is dict:
            if item["id"] == dp:
                for i in item["versions"]:
                    thisDate = datetime.strptime(i["createdOn"], '%Y-%m-%d')
                    if thisDate > latestDate:
                        latestDate = thisDate
                        dpVersion = {"createdOn" : thisDate.strftime("%Y-%m-%d"),
                                     "productVersion" :  i["productVersion"],
                                     "id" : i["id"],
                                     "url" : i["url"]}
    return dpVersion

def downloadGPkgs(dpversion):

    filesURL = urlopen(dpversion["url"])
    dl = filesURL.read()
    encoding = filesURL.info().get_content_charset('utf-8')
    files = json.loads(dl.decode(encoding))
    for f in files["downloads"]:
        if f["fileName"][-4:] == ".zip":
            print(f["fileName"], ": download - actual data file")
            r = requests.get(f["url"], allow_redirects=True)
            file = open(dlCachePath + f["fileName"], 'wb').write(r.content)
            print("...", f["url"][48:])
        else:
            print(f["fileName"], ": other ignore non-zip files")

def unzipGPkgs():
    for item in os.listdir(dlCachePath):
        if item != 'unzipped':
            with zipfile.ZipFile(os.path.join(dlCachePath, item), 'r') as zObject:
                zObject.extractall(path= dlCachePath + unzipped)

def updatePGwithGPkgs():
    # ... create ogr2ogr instance to load each gpkg into tables in mastermap_new schema in base_mapping database, overwriting by default, table names following NGD naming scheme.  
    ogr = gdaltools.ogr2ogr()
    ogr.set_encoding("UTF-8")
    conn = gdaltools.PgConnectionString(host=pghost, port=pgport, dbname=pgdbname, schema=pgschema, user=pguser, password=pgpassword)
    srs = 'EPSG:27700'

    # ... prepare temporary schema
    dropConn = pg.connect(host=pghost, dbname=pgdbname, user=pguser, password=pgpassword, port=pgport)
    cur = dropConn.cursor()
    cur.execute("DROP SCHEMA mastermap CASCADE; COMMIT; CREATE SCHEMA mastermap AUTHORIZATION postgres; COMMIT;")
    dropConn.commit()
    cur.close()
    dropConn.close()

    # ... get gpkgs from local download location and extract pg table names from filenames
    for gpkg in os.listdir(os.path.join(gpkgPath, unzipped, dataFldr)):
        print("gpkg > ",gpkg)
        gpkgname = os.path.join(gpkgPath, unzipped, dataFldr, gpkg)
        print("gpkgname > ", gpkgname)
        tablename = gpkg.split("_")[2]+gpkg.split("_")[3].replace(".gpkg", "")
        print(tablename) 
        ogr.set_input(gpkgname, srs=srs)
        print(conn,  tablename,  srs)    
        ogr.set_output(conn, table_name=tablename, srs=srs)
        # ... run ogr to create tables from respective gpkg
        ogr.execute()

print(platform.system()) 

# Path and database parameters #
if platform.system() == 'Linux':
    dlCachePath = '/home/simon/data/ngd/features/'
    gpkgPath = '/home/simon/data/ngd/features/'
    unzipped = 'unzipped/'
    dataFldr = 'Data/'
    #pghost = "192.168.4.26"
    pghost = "localhost"
    pgport = 5432
# Windows
else:                   
    dlCachePath = 'C:\\osmm\\gpkg\\'
    gpkgPath =  "C:\\osmm\\gpkg\\"
    unzipped = 'unzipped'
    dataFldr = 'Data'
    pghost = "localhost"    #"sw2-gis.wychavon.gov.uk"
    pgport = 5433
    gdaltools.Wrapper.BASEPATH = "C:\Program Files\GDAL"

pgdbname="base_mapping"
pgschema="mastermap"
pguser="postgres"
pgpassword="postgres.."

#load_dotenv()
# OS Datapackage parameters
#key = os.getenv('AlcbyOhqAOIcVP1XCD37WGG33qsSntiy') 
key = 'AlcbyOhqAOIcVP1XCD37WGG33qsSntiy'
dp = "0040174475"       #look up from OS datapackages page
data = DataPackageDownload.all_products(key)

# Get downloads URL for Datapackage
latestDate = '01/01/23'
latestDate = datetime.strptime(latestDate, '%m/%d/%y')
dpv = getLastestURL(latestDate)
pprint.pp(dpv)

downloadGPkgs(dpv)      # download latest gpkg zips

unzipGPkgs()            # unzip gpkgs ito sub-folder

updatePGwithGPkgs()     # create ogr2ogr instance to load each gpkg into tables in mastermap_new schema in base_mapping  
                        # database, overwriting by default, table names following NGD naming scheme.  