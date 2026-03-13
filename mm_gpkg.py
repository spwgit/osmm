from osdatahub import DataPackageDownload
from dotenv import load_dotenv, find_dotenv, set_key
from urllib.request import urlopen
from pathlib import Path
import gdaltools
import psycopg2 as pg
import json
import pprint
import requests
import os, platform, zipfile
from datetime import datetime

from mmUsrPerms import mmPermSQL 

def getLatestURL(latestDate):
    for item in data:
        if type(item) is dict:
            if item["id"] == dp:
                for i in item["versions"]:
                    thisDate = datetime.strptime(i["createdOn"], '%Y-%m-%d')
                    if thisDate > latestDate:
                        print("Previous: ",latestDate, "Latest: ", thisDate)
                        latestDate = thisDate
                        dpVersion = {"createdOn" : thisDate.strftime("%Y-%m-%d"),
                                     "productVersion" :  i["productVersion"],
                                     "id" : i["id"],
                                     "url" : i["url"]}
    return dpVersion

def downloadGPkgs(dpversion):

    filesURL = urlopen(dpversion["url"])
    print(dpversion["url"])
    dl = filesURL.read()
    encoding = filesURL.info().get_content_charset('utf-8')
    files = json.loads(dl.decode(encoding))
    emptyExistingFiles(dlCachePath)
    for f in files["downloads"]:
        if f["fileName"][-4:] == ".zip":
            print(f["fileName"], ": download - actual data file")
            r = requests.get(f["url"], allow_redirects=True, verify=False)
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
    Conn = pg.connect(host=pghost, dbname=pgdbname, user=pguser, password=pgpassword, port=pgport)
    cur = Conn.cursor()
    cur.execute("DROP SCHEMA IF EXISTS mastermap_new CASCADE; COMMIT; DROP SCHEMA IF EXISTS mastermap_old CASCADE; COMMIT; CREATE SCHEMA mastermap_new AUTHORIZATION postgres;")
    cur.close()
    Conn.commit()

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
    cur.close()
    Conn.close()
    
def renameSchema():
    Conn = pg.connect(host=pghost, dbname=pgdbname, user=pguser, password=pgpassword, port=pgport)
    cur = Conn.cursor()
    # tidy up text_string column name
    cur.execute("ALTER TABLE mastermap_new.cartographictext RENAME text_string TO textstring;")
    Conn.commit()
    # it it exists move current live mastermap out of the way as mastermap_old
    try:
        cur.execute("ALTER SCHEMA mastermap RENAME TO mastermap_old;")
        Conn.commit()
    except:
        print("Mastermap schema does not exist")
    # remane new tables to mastermap
    cur.execute("ALTER SCHEMA mastermap_new RENAME TO mastermap;")
    Conn.commit()
    # apply schema permissions to authority adimns and users
    cur.execute(mmPermSQL)

    Conn.commit()
    cur.close()
    Conn.close()

def emptyExistingFiles(directory_path):
    """
    Walks through the provided directory path and deletes all files,
    but keeps the directory structure (folders) intact.
    """
    
    # Check if the directory actually exists
    if not os.path.exists(directory_path):
        print(f"Error: The directory '{directory_path}' does not exist.")
        return

    print(f"Starting cleanup in: {directory_path}")
    
    deleted_count = 0
    errors = 0

    # os.walk yields a 3-tuple (dirpath, dirnames, filenames)
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
                deleted_count += 1
            except OSError as e:
                print(f"Error deleting {file_path}: {e}")
                errors += 1

    print("-" * 30)
    print("Cleanup complete.")
    print(f"Total files deleted: {deleted_count}")
    print(f"Errors encountered: {errors}")

def writeUpdatesToEnv():
    print(dpv["createdOn"])
    set_key(dotenv_file,"latestDate", dpv["createdOn"])

def downloadAndImportNewGpkgs(dpv, gpkgPath):

    emptyExistingFiles(gpkgPath)
    downloadGPkgs(dpv)      # download latest gpkg zips
    unzipGPkgs()            # unzip gpkgs ito sub-folder
    updatePGwithGPkgs()     # create ogr2ogr instance to load each gpkg into tables in mastermap_new schema in base_mapping  
                            # database, overwriting by default

print(platform.system()) 

dotenv_file = find_dotenv()
load_dotenv(dotenv_file)

# OS/Platform dependant settings
if platform.system() == 'Linux':
    sysPrefix = 'linux'

else:   # Windows
    sysPrefix = 'win'
    gdaltools.Wrapper.BASEPATH = os.environ.get("win_dataFldrgdaltool_Wrapper_BASEPATH")
    os.environ['PROJ_LIB'] = os.environ.get("win_os_environ_PROJ_LIB") 

# Path and database parameters #
dlCachePath = os.environ.get(sysPrefix + "_dlCachePath")  
gpkgPath = os.environ.get(sysPrefix + "_gpkgPath") 
permsPath = os.environ.get(sysPrefix + "_permsPath") 
unzipped = os.environ.get(sysPrefix + "_unzipped")
dataFldr = os.environ.get(sysPrefix + "_dataFldr")
pghost = os.environ.get(sysPrefix + "_pghost") 
pgport = os.environ.get(sysPrefix + "_pgport") 

# PG Database parameters
pgdbname = os.environ.get("pgDBName")
pgschema = os.environ.get("pgSchema") 
pguser = os.environ.get("pgUser") 
pgpassword = os.environ.get("pgpassword")

# OS Datapackage parameters
key = os.environ.get("key")
dp = os.environ.get("mastermapDataPackageID") # NTS: look up from OS datapackages page?
print(key, pguser) 
data = DataPackageDownload.all_products(key)

# Get downloads URL for Datapackage
latestDate = datetime.strptime(os.environ.get("latestDate"), '%Y-%m-%d')
try:
    dpv = getLatestURL(latestDate)
    pprint.pprint(dpv)
    
    try:
        downloadAndImportNewGpkgs(dpv, gpkgPath)
    except:
        print("A problem occured while attemping to download updated packages")
        pass
    try:
        renameSchema()          # rename newly created schema to original name
    except:
        print("A problem occured while attemping to PG database schema")
    
    writeUpdatesToEnv()
except:
    print("The latest South Worcestershire Mastermap Geopackages are installed in the Postgres base_mapping mastermap schema")


