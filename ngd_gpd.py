import geopandas as gpd
import matplotlib.pyplot as plt
from osdatahub import NGD, Extent
import contextily as ctx

key = 'gP228DpHXZ2BWdrmffMmUNhzAFyuuE27'
crs = "EPSG:27700" 
extent = Extent.from_bbox((385022, 251510, 385521, 251799), crs=crs)

# (342730, 137700, 347700, 141642) demo
# (349196, 245517, 370776, 256640)
# (359196, 245517, 370776, 250640)
# (383184, 254503, 383819, 254792)
# (384863, 254429, 385181, 254573) cathedral
# (385022, 251510, 385521, 251799) carrington
collection = "bld-fts"
ngd = NGD(key, collection)
bldpart = ngd.query(extent=extent, crs=crs)

collection = "bld-fts-buildingline"
ngd = NGD(key, collection)
bldline = ngd.query(extent=extent, crs=crs)

gdf_bp = gpd.GeoDataFrame.from_features(bldpart['features'], crs=crs)
gdf_bl = gpd.GeoDataFrame.from_features(bldline['features'], crs=crs)

#ax = gdf_bp.plot(color="moccasin", figsize=(12, 8))
# # Plot the query extent
#ax.plot(*zip(*extent.polygon.exterior.coords), color="dimgray",
#        linestyle='--', label="Bounding Box")

fig, ax = plt.subplots(figsize= (12, 8))

ax.plot(*zip(*extent.polygon.exterior.coords), color="dimgray", linestyle='--', label='Query Bounding Box')
gdf_bp.plot(ax=ax, color="moccasin", label='bld-fts-buildingpart')
gdf_bl.plot(ax=ax, color="darkgray", label='bld-fts-buildingline')

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
fig.legend()

# Add the basemap.
ctx.add_basemap(ax, zoom="auto", source=ctx.providers.CartoDB.Positron, crs=gdf_bp.crs, interpolation="sinc")

plt.show()