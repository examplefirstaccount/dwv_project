import geopandas as gpd
import numpy as np
from shapely.geometry import Point, Polygon

# Europe bounds
LON_MIN, LON_MAX = -25, 45
LAT_MIN, LAT_MAX = 34, 72
GRID_SIZE = 1000


def is_land(lon, lat, land_polygons):
    point = Point(lon, lat)
    return any(land.contains(point) for land in land_polygons.geometry)


def generate_eu_land_mask():
    land = gpd.read_file('https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip')
    europe_bbox = Polygon([
        (LON_MIN, LAT_MIN),
        (LON_MAX, LAT_MIN),
        (LON_MAX, LAT_MAX),
        (LON_MIN, LAT_MAX)
    ])
    land_polygons = land.clip(europe_bbox)

    land_mask = np.zeros((GRID_SIZE, GRID_SIZE))
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            land_mask[i,j] = is_land(
                LON_MIN + (LON_MAX-LON_MIN)*j/GRID_SIZE,
                LAT_MIN + (LAT_MAX-LAT_MIN)*i/GRID_SIZE,
                land_polygons
            )
    np.save('europe_land_mask.npy', land_mask)
