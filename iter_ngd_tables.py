import psycopg2 as pg
from dotenv import load_dotenv
import os, platform

load_dotenv()
if platform.system() == 'Linux':
    pghost = "localhost"
else:
    pghost = "sw2-gis.wychavon.gov.uk"

pgport = 5432
pgdbname="ngd"
pgschema="features"
pguser="postgres"
pgpassword=os.getenv('pgpassword')

conn = pg.connect(host=pghost, dbname=pgdbname, user=pguser, password=pgpassword, port=pgport)
cur = conn.cursor()
t_cur = conn.cursor()
cur.execute("select * from information_schema.tables where table_schema = 'features';")
for row in cur:
    tableName = row[2]
    t_cur.execute("select distinct theme, description from features."+ tableName +" order by description")
    for t_row in t_cur:
        print(tableName,',', t_row[0],',', t_row[1])
    t_cur.close
cur.close()
conn.close()