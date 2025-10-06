import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import math

# --- Load TSV with Lat_Long column ---
df = pd.read_csv("drs_servers.tsv", sep="\t")

# Split Lat_Long into Lat and Lon
lat_lon = df["Lat_Long"].str.split(",", expand=True)
df["Lat"] = pd.to_numeric(lat_lon[0].str.strip(), errors="coerce")
df["Lon"] = pd.to_numeric(lat_lon[1].str.strip(), errors="coerce")

# Drop any invalid rows
df = df.dropna(subset=["Lat", "Lon", "TotalSize_GB"])

# --- Group near-duplicate geolocations (for decluttering) ---
def round_to(x, step):
    return np.round(x / step) * step

grouping_precision = 0.2  # degrees
df["_lat_bin"] = round_to(df["Lat"], grouping_precision)
df["_lon_bin"] = round_to(df["Lon"], grouping_precision)

groups = df.groupby(["_lat_bin", "_lon_bin"])

# --- Circle size scaling ---
sizes = df["TotalSize_GB"].values
print (f"Size range: {sizes.min()} to {sizes.max()} GB")
print(df)
print(df["TotalSize_GB"].head())
if np.nanmax(sizes) == np.nanmin(sizes):
    scaled_sizes = np.full_like(sizes, 300)
else:
    norm = (sizes - sizes.min()) / (sizes.max() - sizes.min())
    scaled_sizes = 100 + 2000 * np.sqrt(norm)  # scale so area ~ size
df["_marker_size"] = scaled_sizes

# --- Setup Cartopy map ---
fig = plt.figure(figsize=(14, 7))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()

# Add styled base map
ax.add_feature(cfeature.LAND, facecolor="honeydew", zorder=1)      # soft greenish land
ax.add_feature(cfeature.OCEAN, facecolor="aliceblue", zorder=0)    # pale blue ocean
ax.add_feature(cfeature.LAKES, facecolor="aliceblue", zorder=2)    # lakes
ax.add_feature(cfeature.RIVERS, edgecolor="skyblue", zorder=3)     # rivers
ax.coastlines(linewidth=0.5, color="gray", zorder=4)
ax.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor="black", zorder=5)

# Optional gridlines
ax.gridlines(draw_labels=False, linestyle=":", linewidth=0.3, color="gray", zorder=6)

#ax.coastlines(linewidth=0.5)
#ax.add_feature(cfeature.BORDERS, linewidth=0.3)
#ax.gridlines(draw_labels=False, linestyle=":", linewidth=0.3)

# --- Plot groups with decluttering ---
base_offset_deg = 2.0

for (_, _), g in groups:
    g = g.sort_values("TotalSize_GB", ascending=False).reset_index(drop=True)
    center_lat, center_lon = g.loc[0, "Lat"], g.loc[0, "Lon"]
    
    n = len(g)
    if n == 1:
        offsets = [(0, 0)]
    else:
        radius = base_offset_deg * (1 + 0.15 * (n - 2))
        offsets = [(0, 0)]
        for i in range(1, n):
            angle = 2 * math.pi * (i-1) / (n-1)
            dlat = radius * math.cos(angle)
            dlon = radius * math.sin(angle) / max(math.cos(math.radians(center_lat)), 0.2)
            offsets.append((dlat, dlon))
    
    for (dlat, dlon), (_, row) in zip(offsets, g.iterrows()):
        lat, lon = row["Lat"] + dlat, row["Lon"] + dlon
        label = f"{row['Name']} — {int(row['TotalSize_GB']):,} GB"
        
        ax.scatter(lon, lat, s=row["_marker_size"], color="blue",
                   alpha=0.35, transform=ccrs.PlateCarree(), zorder=10)
        #ax.text(lon, lat, label, fontsize=7, alpha=0.9,
        #        ha="center", va="bottom", transform=ccrs.PlateCarree(), zorder=11)

plt.title("DRS Servers — declustered circles with Cartopy")
plt.tight_layout()
plt.savefig("drs_world_map_cartopy.png", dpi=300, bbox_inches="tight")
plt.savefig("drs_world_map_cartopy.svg", bbox_inches="tight")
plt.show()