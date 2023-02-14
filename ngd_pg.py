from osdatahub import DataPackageDownload
from urllib.request import urlopen
import gdaltools
import json
import requests
import os, platform, zipfile

dlCachePath = 'C:\\os_ngd_features\\'
gpkgPath = "C:\\os_ngd_features\\"
unzipped = 'unzipped'

pghost="sw2-gis.wychavon.gov.uk"
pgport=5432
pgdbname="ngd"
pgschema="features"
pguser="postgres"
pgpassword="postgres.."

gdaltools.Wrapper.BASEPATH = "C:\Program Files\GDAL"

ogr = gdaltools.ogr2ogr()
ogr.set_encoding("UTF-8")
conn = gdaltools.PgConnectionString(host=pghost, port=pgport, dbname=pgdbname, schema=pgschema, user=pguser, password=pgpassword)
print(conn)
srs = 'EPSG:27700'

for gpkg in os.listdir(os.path.join(gpkgPath, unzipped)):
    gpkgname = os.path.join(gpkgPath, unzipped,  gpkg)
    tablename = gpkg[:-5]
    print(os.path.isfile(gpkgname), gpkgname)
    ogr.set_input(gpkgname, srs=srs)
    ogr.set_output(conn, table_name=tablename, srs=srs)
    ogr.set_output_mode(data_source_mode=ogr.MODE_DS_CREATE_OR_UPDATE)
    ogr.execute()