import os
import math
import requests
from PIL import Image

# === Configuration ===
API_KEY = 'AIzaSyBA25B9Ba8UI5ZIgXKOOAaghe460qg-_rU'  # <-- Replace with your API key
center_lat = 41.582778     
center_lng = -87.475278    
zoom = 21                  
img_size = 640             
grid_size = 11             
output_file = 'map_output.png'

# === Coordinate Conversion ===
def latlng_to_pixel_xy(lat, lng, zoom):
    sin_lat = math.sin(lat * math.pi / 180.0)
    x = ((lng + 180) / 360) * 256 * 2**zoom
    y = (0.5 - math.log((1 + sin_lat) / (1 - sin_lat)) / (4 * math.pi)) * 256 * 2**zoom
    return x, y

def pixel_xy_to_latlng(x, y, zoom):
    lng = x / (256 * 2**zoom) * 360.0 - 180
    n = math.pi - 2 * math.pi * y / (256 * 2**zoom)
    lat = 180 / math.pi * math.atan(0.5 * (math.exp(n) - math.exp(-n)))
    return lat, lng

# === Download Map Tiles ===
def download_tile(lat, lng, zoom, filename):
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom={zoom}&size={img_size}x{img_size}&maptype=satellite&key={API_KEY}&tilt=0&heading=0"
    r = requests.get(url)
    if r.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(r.content)
    else:
        print("Error:", r.status_code, r.text)

# === Main Program ===
def fetch_large_map():
    center_x, center_y = latlng_to_pixel_xy(center_lat, center_lng, zoom)
    full_image = Image.new('RGB', (img_size * grid_size, img_size * grid_size))

    for row in range(grid_size):
        for col in range(grid_size):
            dx = (col - grid_size // 2) * img_size
            dy = (row - grid_size // 2) * img_size
            x = center_x + dx
            y = center_y + dy
            lat, lng = pixel_xy_to_latlng(x, y, zoom)
            tile_file = f'tile_{row}_{col}.png'
            print(f'Downloading tile ({row},{col}) at lat: {lat:.6f}, lng: {lng:.6f}')
            download_tile(lat, lng, zoom, tile_file)

            tile_img = Image.open(tile_file)
            full_image.paste(tile_img, (col * img_size, row * img_size))
            
            # Remove the temporary tile file after pasting it
            os.remove(tile_file)

    full_image.save(output_file)
    print(f"Stitching complete, large image saved as {output_file}")

if __name__ == '__main__':
    fetch_large_map()