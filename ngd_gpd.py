import geopandas as gpd
import matplotlib.pyplot as plt
from osdatahub import NGD, Extent
import contextily as ctx
import os
# os.environ['PROJ_NETWORK'] = 'OFF'

key = 'gP228DpHXZ2BWdrmffMmUNhzAFyuuE27'
crs = "EPSG:27700" 
extent = Extent.from_bbox((384863, 254429, 385181, 254573), crs=crs)

# (342730, 137700, 347700, 141642) demo
# (349196, 245517, 370776, 256640)
# (359196, 245517, 370776, 250640)
# (383184, 254503, 383819, 254792) 
collection = "bld-fts-buildingpart"
ngd = NGD(key, collection)
bldpart = ngd.query(extent=extent, crs=crs)

collection = "bld-fts-buildingline"
ngd = NGD(key, collection)
bldline = ngd.query(extent=extent, crs=crs)

gdf_bp = gpd.GeoDataFrame.from_features(bldpart['features'], crs=crs)
print(gdf_bp.count)
gdf_bl = gpd.GeoDataFrame.from_features(bldline['features'], crs=crs)
print(gdf_bl.count)

#ax = gdf_bp.plot(color="moccasin", figsize=(12, 8))
# # Plot the query extent
#ax.plot(*zip(*extent.polygon.exterior.coords), color="dimgray",
#        linestyle='--', label="Bounding Box")

fig, ax = plt.subplots(figsize= (12, 8))
gdf_bp.plot(ax=ax, color="moccasin")
gdf_bl.plot(ax=ax, color="darkgray")

# Define limits of the plot
bounds = extent.polygon.bounds
# margin adds a bit of space around the bounding box
margin = 10
x_limits = (bounds[0] - margin, bounds[2] + margin)
y_limits = (bounds[1] - margin, bounds[3] + margin)
ax.set_xlim(*x_limits)
ax.set_ylim(*y_limits)

# Add labelscls
ax.set_xlabel("Eastings")
ax.set_ylabel("Northings")
ax.set_title("bld-fts-buildingpart")
plt.legend()

# Add the basemap. Note: contextily only works with EPSG:3857 basemaps, but will convert it to match the data crs
#basemap_url = "https://api.os.uk/maps/raster/v1/zxy/Light_3857/{z}/{x}/{y}.png?key=" + key
ctx.add_basemap(ax, zoom="auto", source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf_bp.crs, interpolation="sinc")

plt.show()