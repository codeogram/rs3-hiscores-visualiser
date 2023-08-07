import datetime
import json
import os
import requests
import sys


if os.environ.get("DEBUG") == "false": # if in production
    debug_prefix = ""
else:
    debug_prefix = "TEST_"

RAW_DATA_DIR = f"{debug_prefix}raw_data"
LOG_DIR = f"{debug_prefix}logs"

SKILLS_JSON_PATH = "skills.json"


# logging configuration
from for_logging import MyLogger
from pathlib import Path
# set DEBUG to false for "production"
file_stem = Path(__file__).stem
my_logger = MyLogger(
    file_name=file_stem,
    log_file_path=os.path.join(LOG_DIR, f"{file_stem}.log")
)


# determining which skill to scrape
if len(sys.argv) < 2:
    skills = ["overall"]
else:
    skills = sys.argv[1:] # scrape all the mentioned skills


# determine each skill's table number
skills_for_scraping = []
with open(SKILLS_JSON_PATH, "r", encoding="utf-8") as f:
    json_data = f.read()
    skill_data = json.loads(json_data)
    
    for skill_info in skill_data:
        if skill_info.get("skill") in skills:
            skills_for_scraping.append(skill_info)
# print(skills_for_scraping)
my_logger.logger.debug(skills_for_scraping)


# scrape the hiscores, along with the timestamp
timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
print(timestamp)
raw_data = {
    "timestamp": timestamp,
    "data": []
}
table_size = 50
for skill in skills_for_scraping:
    url = f"https://secure.runescape.com/m=hiscore/ranking.json?table={skill.get('table')}&category=28&size={table_size}"
    print(url)
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError as err:
        my_logger.logger.error(err)
    else:
        if response.ok:
            my_logger.logger.debug(f"{response.status_code}: {url}")
            response_data = json.dumps(response.json())
        else:
            my_logger.logger.error(f"{response.status_code}: {url}")
            response_data = None
        raw_data["data"].append(response_data)
        

# save data to disk
timestamp_for_file_name = timestamp.replace(" ", "_").replace(":", "_")
raw_data_file_path = os.path.join(RAW_DATA_DIR, f"raw_data_{timestamp_for_file_name}.json")
with open(raw_data_file_path, "w", encoding="utf-8") as f:
    json.dump(raw_data, f, indent=4)