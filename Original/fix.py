import os
import pandas as pd

def format_image_name(name):
    if name and len(name) > 1 and name[1:].isdigit() and len(name[1:]) == 4:
        return name[:1] + name[1:2] + "0" + name[2:]
    return name

def find_missing_images(csv_file, streetview_folder, satellite_folder):
    df = pd.read_csv(csv_file)

    streetview_images = set(df['Streetview_img_name'].dropna().astype(str) + ".png")
    satellite_images = set(df['Sitelite_img_name'].dropna().astype(str) + ".png")

    existing_streetview = set(os.listdir(streetview_folder))
    existing_satellite = set(os.listdir(satellite_folder))

    missing_streetview = streetview_images - existing_streetview
    missing_satellite = satellite_images - existing_satellite

    if missing_streetview:
        print("Missing streetview images:", missing_streetview)
    else:
        print("No missing streetview images.")

    if missing_satellite:
        print("Missing satellite images:", missing_satellite)
    else:
        print("No missing satellite images.")

    def modify_image_name(name):
        if isinstance(name, str) and name + ".png" in missing_streetview | missing_satellite:
            prefix = name[0]
            num_part = name[1:]
            if num_part.isdigit() and len(num_part) == 4:
                return prefix + num_part[0] + "0" + num_part[1:]
        return name

    df['Streetview_img_name'] = df['Streetview_img_name'].apply(modify_image_name)
    df['Sitelite_img_name'] = df['Sitelite_img_name'].apply(modify_image_name)

    df.to_csv(csv_file, index=False)
    print("CSV file updated with modified names.")

    return missing_streetview, missing_satellite

csv_file = "NASA_Datasets.csv"
streetview_folder = "./streetview_images"
satellite_folder = "./satellite_images"

missing_streetview, missing_satellite = find_missing_images(csv_file, streetview_folder, satellite_folder)
