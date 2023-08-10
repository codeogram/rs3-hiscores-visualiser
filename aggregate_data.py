import json
import os
import pandas as pd
import bar_chart_race as bcr
from datetime import datetime


if os.environ.get("DEBUG") == "false": # if in production
    debug_prefix = ""
else:
    debug_prefix = "TEST_"

BAR_RACE_VIDEOS_DIR = f"{debug_prefix}bar_races"
RAW_DATA_DIR_PATH = f"{debug_prefix}raw_scraped_data4"
HELPER_FILES_DIR_PATH = "helper_files"
# ALL_PLAYER_IMAGES_DIR = f"{debug_prefix}player_images" # have scrapped this for now
BANNED_USERS_PATH = "banned_users.txt"


def get_full_file_path(raw_data_dir_path, file_name):
    return os.path.join(os.path.dirname(__file__), raw_data_dir_path, file_name) # absolute path to the json file


def get_data_from_json_file(full_file_path) -> dict|None:
    if ".json" not in os.path.basename(full_file_path):
        return
    with open(full_file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
        file_content_dict = json.loads(file_content)
    return file_content_dict


def organise_dict_data(file_content_dict):
    if file_content_dict["data"]: # if not an empty list
        hiscores_data = {}
        for hiscores_item in file_content_dict["data"]:
            skill_name = hiscores_item["skill"]["skill"]
            skill_data = json.loads(hiscores_item["skill_data"]) # convert json str into list 
            hiscores_data[skill_name] = skill_data
    else:
        hiscores_data = {}
    # append all the data corresponding to this timestamp, to all_organised_data
    file_data = {
        "timestamp": file_content_dict["timestamp"],
        "hiscores": hiscores_data
    }
    return file_data


def sort_all_data_by_date(all_file_data):
    return sorted(all_file_data, key=lambda file_data: file_data["timestamp"])


def get_unique_users_per_skill(data: list[dict]) -> dict:
    unique_skills = list(data[0]["hiscores"].keys())
    unique_users_per_skill = {skill: set() for skill in unique_skills} # dict of key:set pairs

    for data_point in data:
        for skill in unique_skills:
            try:
                for user in data_point["hiscores"][skill]:
                    unique_users_per_skill[skill].add(user["name"])
            except KeyError:
                pass

    return unique_users_per_skill


def get_banned_users():
    with open(BANNED_USERS_PATH, "r", encoding="utf-8") as f:
        banned_users = []
        reader = f.readlines()
        for line in reader:
            if (stripped_line := line.strip()):
                banned_users.append(stripped_line)
        if not banned_users:
            banned_users = None
    return banned_users


def create_df(data: list[dict], unique_users_per_skill: dict, skill: str, use_each_n=None, bars_visible=10) -> pd.DataFrame:
    """
    Produce a dataframe to be used for the bar race video
    index: date
    column for each unique player. each row is their xp at a given time
    their xp for each row is 0 unless they are recorded in the hiscores at that time
    """
    unique_players = unique_users_per_skill[skill]
    df = pd.DataFrame(
        data=None,
        columns=list(unique_players)
    )
    banned_users = get_banned_users()
    num_banned_users = 0 if not banned_users else len(banned_users)

    def is_valid_frame(frame_num, num_frames):
        """ determine if a given frame number is valid, given the value of use_each_n given to create_df"""
        return (use_each_n is None) or (frame_num % use_each_n == 0) or (iter_count == num_frames-1)

    lowest_visible_xp = 1 # start at 1 so lowest_visible_xp-1 = 0
    for iter_count, data_point in enumerate(data):
        if not is_valid_frame(iter_count, num_frames=len(data)):
            continue
        
        new_row = {player:lowest_visible_xp-1 for player in df.columns}
        # check through the gathered data and add any matching xp values
        this_date = datetime.strptime(data_point["timestamp"], "%Y-%m-%d %H:%M:%S")
        try:
            this_hiscores_data = data_point["hiscores"][skill]
        except KeyError: # if no data, skip this data_point
            continue

        for player in this_hiscores_data:
            xp_int = int(player["score"].replace(",",""))
            new_row[player["name"]] = xp_int
            if player["rank"] == str(bars_visible+num_banned_users): # num_banned_users in case the banned users would have been ranked above
                lowest_visible_xp = xp_int

        sorted_xp_values_desc = sorted(new_row.values(), reverse=True)
        lowest_visible_xp = sorted_xp_values_desc[bars_visible]

        # add the row to the main dataframe
        new_row_df = pd.DataFrame(data=new_row, index=[this_date])
        df = pd.concat([df, new_row_df])

        print(this_date)

    # Convert all columns to numeric dtype
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # delete banned users
    if banned_users:
        for user in banned_users:
            df = df.drop([user], axis=1)

    print(df)
    return df


def get_xp_per_level(xp_per_level_file_path) -> dict:
    import csv
    with open(xp_per_level_file_path, "r", encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        xp_per_level = {}
        for row in reader:
            xp_per_level[row["Level"]] = int(row["XP"].replace(",",""))
    return xp_per_level


def create_bar_race(df, bars_visible):
    """
    Create a bar chart race from the dataframe given
    """
    # get xp values per level
    xp_per_level = get_xp_per_level(os.path.join(HELPER_FILES_DIR_PATH, "xp_per_level.csv"))

    def get_level_from_xp(xp) -> int:
        xp_per_level = get_xp_per_level(os.path.join(HELPER_FILES_DIR_PATH, "xp_per_level.csv"))
        level = 1
        for level_compare, xp_compare in enumerate(sorted(xp_per_level.values()), 1):
            if xp_compare > xp:
                level = level_compare - 1
                break
        return level

    def period_summary(values, ranks):
        highest_xp = int(values.nlargest(1).values[0])
        highest_level = get_level_from_xp(highest_xp)
        return {
            'x': .98,
            'y': .12,
            'ha': 'right',
            'va': 'center',
            'size': '30',
            'color': 'mediumblue',
            's': f"""Highest Level: {highest_level}"""
        }

    time_now = datetime.strftime(datetime.now(), "%Y-%m-%d_%H_%M_%S")
    bcr.bar_chart_race(
        df,
        filename=os.path.join(BAR_RACE_VIDEOS_DIR, f"bar_race_{time_now}.mp4"),
        figsize=(16,9),
        n_bars=bars_visible,
        dpi=120,
        interpolate_period=True,
        period_length=300,
        steps_per_period=18,
        filter_column_colors=True,
        shared_fontdict={'family': 'RuneScape Bold Font', 'weight': 'bold', 'color': 'black'},
        bar_label_size=18,
        tick_label_size=22,
        period_label={'x': .98, 'y': .25, 'ha': 'right', 'va': 'center', 'size': '50', 'color': 'indianred'},
        period_fmt='%b %-d, %Y\n%I:%M %p',
        period_summary_func=period_summary,
        title='Race to 200m Necromancy',
        title_size=50
    )


# getting player images - SCRAPPED
def scrape_player_images(unique_users_per_skill: dict, skill: str|None=None) -> str:
    import requests

    time_now = datetime.utcnow().strftime('%Y-%m-%d_%H_%M_%S')
    scraped_dir = os.path.join(ALL_PLAYER_IMAGES_DIR, f"images_{time_now}")

    # iterate through unique_users_per_skill
    urls_to_do = set() # set, to ensure uniques
    if skill:
        for player in unique_users_per_skill[skill]:
            urls_to_do.add(f"https://secure.runescape.com/m=hiscore/compare?user1={player.replace(' ', '%20')}")
    else:
        for skill, players in unique_users_per_skill.items():
            for player in players:
                urls_to_do.add(f"https://secure.runescape.com/m=hiscore/compare?user1={player.replace(' ', '%20')}")
    urls_to_do = list(urls_to_do)
    print(urls_to_do)
    print(len(urls_to_do))
    return scraped_dir


def main():
    import time
    t1 = time.time()    
    all_file_data = []
    for file_name in os.listdir(RAW_DATA_DIR_PATH):
        if ".json" not in file_name:
            continue
        full_file_path = get_full_file_path(raw_data_dir_path=RAW_DATA_DIR_PATH, file_name=file_name)
        data_dict = get_data_from_json_file(full_file_path)
        data_dict_organised = organise_dict_data(data_dict) if data_dict else data_dict
        all_file_data.append(data_dict_organised)
    all_sorted_data = sort_all_data_by_date(all_file_data)
    unique_users_per_skill = get_unique_users_per_skill(all_sorted_data)
    bars_visible = 16
    df = create_df(
        data=all_sorted_data,
        unique_users_per_skill=unique_users_per_skill,
        skill="necromancy",
        use_each_n=20,
        bars_visible=bars_visible,
    )
    bar_race_video = create_bar_race(df, bars_visible=bars_visible,)
    print(time.time() - t1)


if __name__ == "__main__":
    main()