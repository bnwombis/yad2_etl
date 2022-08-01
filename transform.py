import logging
import glob
from math import floor
from bs4 import BeautifulSoup
import json
import os
import pandas as pd

logging.basicConfig(level=logging.INFO)

stage_pages_path = "stage/re_pages"
stage_csv_fn = "stage/re_ads.csv"
stage_json_fn = "stage/re_ads.json"
stage_json_unique_fn = "stage/re_ads_unique.json"
stage_json_city_mapped_fn = "stage/re_ads_city_mapped.json"
stage_json_cleaned_fn = "stage/re_ads_city_cleaned.json"


def process_pages():
    fp_out_csv = open(stage_csv_fn, "w")
    ads = []
    for file_name in sorted(glob.glob("{stage_pages_path}/*.html".format(stage_pages_path=stage_pages_path))):
        logging.info("process file: {file_name}".format(file_name=file_name))
        with open(file_name, "r") as file:
            page_source = file.read()
            bs = BeautifulSoup(page_source, features="lxml")
        
            elements = bs.find_all(class_="feeditem")
            for element in elements:
                ad = {
                    'item_id': "",
                    'city_name': "",
                    'price': "",
                    'date': "",
                    "rooms": "",
                    "square": "",
                    "floor": "",
                    "source": "private"
                }
                element_contents = element.contents[0]
                ad["item_id"] = element.find(class_="feed_item")['item-id']
                if element.find("div", {"class": "agency"}) is not None:
                    ad["source"] = "agency"
                title = element.find(class_="subtitle").contents[0]
                title_elements = title.split(",")
                ad["city_name"] = title_elements[-1].strip()
                ad["price"] = element.find(class_="price").text.strip().replace(' ₪', '').replace(',', '')
                ad["date"] = element.find(class_="showDateInLobby").text.strip()
                ad["rooms"] = element.find(class_="data rooms-item").find(class_="val").text.strip()
                ad["square"] = element.find(class_="data SquareMeter-item").find(class_="val").text.strip()
                ad["floor"] = element.find(class_="data floor-item").find(class_="val").text.strip()
                csv_string = ";".join(ad.values())
                fp_out_csv.write(csv_string + '\n')
                ads.append(ad)

    fp_out_csv.close()
    json_string = json.dumps(ads)
    with open(stage_json_fn, "w") as fp_json:
        fp_json.write(json_string)
    return ads

def unique_ads():
    df_ads = pd.read_json(stage_json_fn)
    df_ads = df_ads.drop_duplicates(subset=['item_id'], keep='last')
    df_ads.to_json(stage_json_unique_fn)

def map_cities_en():
    df_cities = pd.read_csv("input_data/cities_map.csv", delimiter=";")
    df_ads = pd.read_json(stage_json_fn)

    df_cities = df_cities.set_index("city_name_he")
    df_ads = df_ads.set_index("city_name")

    df_ads = df_ads.join(df_cities)
    df_ads = df_ads.drop_duplicates(subset=['item_id'], keep='last')

    df_ads = df_ads.dropna()
    df_ads = df_ads.set_index("item_id")

    df_ads.to_json(stage_json_city_mapped_fn)

def clean_dat():
    df_ads = pd.read_json(stage_json_city_mapped_fn)
    df_ads = df_ads.drop(df_ads[df_ads["price"]=="לא צוין מחיר"].index)
    df_ads.loc[df_ads["floor"] == "קרקע", "floor"] = "0"
    df_ads.loc[df_ads['rooms'] == "-", 'rooms'] = "0"
    df_ads = df_ads.drop(df_ads[df_ads["square"]=="לא צוין"].index)
    df_ads.to_json(stage_json_cleaned_fn)
    
if not os.path.exists(stage_json_fn):
    process_pages()

unique_ads()
map_cities_en()
