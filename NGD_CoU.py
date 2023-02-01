from osdatahub import DataPackageDownload

key = 'gP228DpHXZ2BWdrmffMmUNhzAFyuuE27'
dpdl = DataPackageDownload.all_products(key)
#print(type(dpdl))
for i in dpdl:
    if i["id"] == "929":
        print(i["url"])