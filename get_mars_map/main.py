import os
import math
import requests
from PIL import Image
from xml.etree import ElementTree as ET

# === Configuration ===
WMTS_URL = 'https://trek.nasa.gov/tiles/Mars/EQ/wmts.cgi'
LAYER = 'MOLA_Color_Shaded_Relief'  # Layer name, can be changed as needed
STYLE = 'default'
TILEMATRIXSET = 'EPSG:4326'  # Projection method
ZOOM_LEVEL = 5  # Zoom level
CENTER_LAT = 0.0  # Center latitude
CENTER_LON = 0.0  # Center longitude
GRID_SIZE = 3  # Tile grid size (GRID_SIZE x GRID_SIZE)
OUTPUT_FILE = 'mars_map.png'
TILE_SIZE = 256  # Pixel size of each tile

# === Get WMTS Capabilities Document ===
def get_wmts_capabilities():
    response = requests.get(f'{WMTS_URL}?SERVICE=WMTS&REQUEST=GetCapabilities')
    response.raise_for_status()
    return ET.fromstring(response.content)

# === Parse Capabilities Document to Get TileMatrixSet Information ===
def get_tile_matrix_set_info():
    capabilities = get_wmts_capabilities()
    namespaces = {'ows': 'http://www.opengis.net/ows/1.1',
                  'wmts': 'http://www.opengis.net/wmts/1.0'}
    tile_matrix_sets = capabilities.findall('.//wmts:TileMatrixSet', namespaces)
    for tms in tile_matrix_sets:
        identifier = tms.find('./ows:Identifier', namespaces).text
        if identifier == TILEMATRIXSET:
            matrices = tms.findall('.//wmts:TileMatrix', namespaces)
            matrix_info = {}
            for matrix in matrices:
                zoom = int(matrix.find('./ows:Identifier', namespaces).text)
                scale_denominator = float(matrix.find('./wmts:ScaleDenominator', namespaces).text)
                top_left_corner = matrix.find('./wmts:TopLeftCorner', namespaces).text.split()
                tile_width = int(matrix.find('./wmts:TileWidth', namespaces).text)
                tile_height = int(matrix.find('./wmts:TileHeight', namespaces).text)
                matrix_width = int(matrix.find('./wmts:MatrixWidth', namespaces).text)
                matrix_height = int(matrix.find('./wmts:MatrixHeight', namespaces).text)
                matrix_info[zoom] = {
                    'scale_denominator': scale_denominator,
                    'top_left_corner': (float(top_left_corner[0]), float(top_left_corner[1])),
                    'tile_width': tile_width,
                    'tile_height': tile_height,
                    'matrix_width': matrix_width,
                    'matrix_height': matrix_height
                }
            return matrix_info
    raise ValueError(f'TileMatrixSet {TILEMATRIXSET} not found in capabilities.')

# === Convert Latitude and Longitude to Tile Coordinates ===
def latlon_to_tile_indices(lat, lon, zoom, matrix_info):
    tile_matrix = matrix_info[zoom]
    origin_x, origin_y = tile_matrix['top_left_corner']
    scale = tile_matrix['scale_denominator'] * 0.00028  # Scale factor in WMTS standard
    pixel_x = (lon - origin_x) / scale
    pixel_y = (origin_y - lat) / scale
    tile_x = int(pixel_x // TILE_SIZE)
    tile_y = int(pixel_y // TILE_SIZE)
    return tile_x, tile_y

# === Download Tile ===
def download_tile(tile_x, tile_y, zoom):
    tile_url = (f'{WMTS_URL}/{LAYER}/{STYLE}/{TILEMATRIXSET}/{zoom}/{tile_y}/{tile_x}.png')
    response = requests.get(tile_url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        return None

# === Main Program ===
def fetch_mars_map():
    matrix_info = get_tile_matrix_set_info()
    center_tile_x, center_tile_y = latlon_to_tile_indices(CENTER_LAT, CENTER_LON, ZOOM_LEVEL, matrix_info)
    full_image = Image.new('RGB', (TILE_SIZE * GRID_SIZE, TILE_SIZE * GRID_SIZE))

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            tile_x = center_tile_x + (col - GRID_SIZE // 2)
            tile_y = center_tile_y + (row - GRID_SIZE // 2)
            tile_img = download_tile(tile_x, tile_y, ZOOM_LEVEL)
            if tile_img:
                full_image.paste(tile_img, (col * TILE_SIZE, row * TILE_SIZE))
            else:
                print(f'Tile ({tile_x}, {tile_y}) is not available at zoom level {ZOOM_LEVEL}.')

    full_image.save(OUTPUT_FILE)
    print(f'Map has been saved as {OUTPUT_FILE}')

if __name__ == '__main__':
    fetch_mars_map()
