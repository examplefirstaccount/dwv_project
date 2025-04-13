import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf

from data_processor import TemperatureDataProcessor

V_MIN = -5  # -23.6
V_MAX = 25  # 30.4
GRID_SIZE = 1000
IMAGE_DIR = 'data/heatmaps'
os.makedirs(IMAGE_DIR, exist_ok=True)

processor = TemperatureDataProcessor()
data = processor.get_heatmap_data()

# Bounds that JS map will use for L.imageOverlay
LON_MIN, LON_MAX = -25, 45
LAT_MIN, LAT_MAX = 34, 72


def generate_and_save_heatmaps():
    for YEAR in range(1950, 2021):
        output_path = os.path.join(IMAGE_DIR, f"heatmap_{YEAR}.png")
        if os.path.exists(output_path):
            continue

        df = pd.DataFrame(data[YEAR])
        df = df[(df['latitude'] >= LAT_MIN) & (df['latitude'] <= LAT_MAX) &
                (df['longitude'] >= LON_MIN) & (df['longitude'] <= LON_MAX)]
        df = df[df['temperature_avg'].notnull()]

        df['latitude'] = df['latitude'].round(1)
        df['longitude'] = df['longitude'].round(1)
        df = df.drop_duplicates(subset=['latitude', 'longitude'])

        lats = df['latitude'].values
        lons = df['longitude'].values
        temps = df['temperature_avg'].values

        grid_lon, grid_lat = np.meshgrid(
            np.linspace(LON_MIN, LON_MAX, GRID_SIZE),
            np.linspace(LAT_MIN, LAT_MAX, GRID_SIZE)
        )

        rbf = Rbf(lons, lats, temps, function='linear')
        grid_temp = rbf(grid_lon, grid_lat)

        # Apply land mask
        land_mask = np.load('data/europe_land_mask.npy')
        grid_temp = np.where(land_mask, grid_temp, np.nan)

        # Save the image with no axes, labels, borders, etc.
        fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
        ax.axis('off')  # remove axes
        ax.imshow(
            grid_temp,
            cmap='RdYlBu_r',
            origin='lower',
            extent=(LON_MIN, LON_MAX, LAT_MIN, LAT_MAX),
            interpolation='bilinear',
            vmin=V_MIN,
            vmax=V_MAX
        )
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        fig.savefig(output_path, dpi=100, bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close(fig)
