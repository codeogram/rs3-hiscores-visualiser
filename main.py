import datetime
import json
import requests
import sys


RAW_DATA_DIR = "raw_data"
LOG_DIR = "logs"


# logging configuration
from for_logging import MyLogger
import os
from pathlib import Path
file_stem = Path(__file__).stem
my_logger = MyLogger(
    file_name=file_stem,
    log_file_path=os.path.join(LOG_DIR, f"TEST_{file_stem}.log") if os.environ.get("DEBUG") else os.path.join(LOG_DIR, f"{file_stem}.log")
)


# determining which skill to scrape
if len(sys.argv) < 2:
    skills = ["overall"]
else:
    skills = sys.argv[1:] # scrape all the mentioned skills


# determine each skill's table number
skills_for_scraping = []
with open("config.json", "r", encoding="utf-8") as f:
    json_data = f.read()
    skill_data = json.loads(json_data)
    
    for skill_info in skill_data:
        if skill_info.get("skill") in skills:
            skills_for_scraping.append(skill_info)
# print(skills_for_scraping)
my_logger.logger.debug(skills_for_scraping)


# scrape the hiscores, for each skill, and store the data with a timestamp
raw_data = []
table_size = 50

for skill in skills_for_scraping:
    url = f"https://secure.runescape.com/m=hiscore/ranking.json?table={skill.get('table')}&category=28&size={table_size}"


    # try:
    #     response = requests.get(url)
    # except requests.exceptions.ConnectionError:
        

    