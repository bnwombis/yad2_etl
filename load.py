import shutil
stage_final_fn = "stage/re_ads_city_cleaned.json"
load_fn = "load/yad2_ads.json"
shutil.copy(stage_final_fn, load_fn)