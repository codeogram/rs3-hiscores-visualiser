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
HELPER_FILES_DIR_PATH = "helper_files"
SKILLS_JSON_PATH = os.path.join(HELPER_FILES_DIR_PATH, "skills.json")


# logging configuration
from for_logging import MyLogger
from pathlib import Path
# set DEBUG to false for "production"
file_stem = Path(__file__).stem
my_logger = MyLogger(
    file_name=file_stem,
    log_file_path=os.path.join(LOG_DIR, f"{file_stem}.log")
)


def parse_args() -> tuple[int, list]:
    """ Parse args to return the scrape interval (in seconds) and list of skills to be scraped"""
    len_args = len(sys.argv)
    if len_args < 2:
        sys.exit(f"Usage: python {file_stem}.py <scrape_interval_in_mins> [specified_skills]")
        
    try:
        scrape_interval = int(sys.argv[1])
    except ValueError as err:
        sys.exit(f"<scrape_interval> has to be an integer.")
    else:
        if scrape_interval < 10 or scrape_interval > 10000:
            sys.exit(f"<scrape_interval> has to be an integer between 10 and 10,000 (seconds).")

    if len_args == 2:
        skills = ["overall"]
    else:
        skills = sys.argv[2:] # scrape all the mentioned skills

    return (scrape_interval, skills)


def get_skills_for_scraping(skills) -> list:
    """ Compare the list of skills provided with the skills in the json file, to return the relevant skill data to be used for scraping """
    skills_for_scraping = []
    with open(SKILLS_JSON_PATH, "r", encoding="utf-8") as f:
        json_data = f.read()
        skill_data = json.loads(json_data)
        for skill_info in skill_data:
            if skill_info.get("skill") in skills:
                skills_for_scraping.append(skill_info)

    my_logger.logger.debug(skills_for_scraping)
    return skills_for_scraping


def scrape(skills_for_scraping) -> str:
    """ Scrape the hiscores, for the skills in skills_for_scraping, and save the raw data to disk """
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    raw_data = {
        "timestamp": timestamp,
        "data": []
    }
    table_size = 50
    for skill in skills_for_scraping:
        url = f"https://secure.runescape.com/m=hiscore/ranking.json?table={skill.get('table')}&category=0&size={table_size}"
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
            raw_data["data"].append({
                "skill": skill,
                "skill_data": response_data
            })
            
    # save data to disk
    timestamp_for_file_name = timestamp.replace(" ", "_").replace(":", "_")
    raw_data_file_path = os.path.join(RAW_DATA_DIR, f"raw_data_{timestamp_for_file_name}.json")
    with open(raw_data_file_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, indent=4)
    return raw_data_file_path


def main():
    scrape_interval, skills = parse_args()
    skills_for_scraping = get_skills_for_scraping(skills) # retrieve the skills that need to be scraped (from the command line)

    import schedule
    import time
    def do_scrape():
        raw_data_file_path = scrape(skills_for_scraping) # scrape the skills, save to file, and return the file path
        my_logger.logger.debug(f"data saved: {raw_data_file_path}") # log the file path to which the data was saved

    # schedule the scraping
    schedule.every(scrape_interval).seconds.do(do_scrape)
    schedule.run_pending()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()