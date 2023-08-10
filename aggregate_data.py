import json
import os
import sys
import pandas as pd
import bar_chart_race as bcr
from datetime import datetime


if os.environ.get("DEBUG") == "false": # if in production
    debug_prefix = ""
else:
    debug_prefix = "TEST_"

BAR_RACE_VIDEOS_DIR = f"{debug_prefix}bar_races"
RAW_DATA_DIR_PATH = f"{debug_prefix}raw_scraped_data2"


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
    
    # print(unique_users_per_skill)
    # for k, v in unique_users_per_skill.items():
    #     print(f"{k}: {len(v)} users")

    return unique_users_per_skill


def create_df(data: list[dict], unique_users_per_skill: dict, skill: str, use_each_n=None) -> pd.DataFrame:
    """
    Produce a dataframe to be used for the bar race video
    index: date
    column for each unique player. each row is their xp at a given time
    their xp for each row is 0 unless they are recorded in the hiscores at that time
    """
    unique_players = unique_users_per_skill[skill]
    # print(unique_players)
    df = pd.DataFrame(
        data=None,
        columns=list(unique_players)
    )

    # iterate through the data points and determine if I want to use a certain data point
    # based on the timestamp and the increment i specified
    # if the data is empty for whatever reason, just duplicate the values from the last point
    # for each data point I want to add a new row with the values given by the hiscores data
    # add it with the index specified by the timestamp

    def is_valid_frame(frame_num, num_frames):
        """ determine if a given frame number is valid, given the value of use_each_n given to create_df"""
        return (use_each_n is None) or (frame_num % use_each_n == 0) or (iter_count == num_frames-1)


    # TODO - set each player's xp value to 1 less than the 10th
    # (or however many rows are visible on the eventual chart) highest xp value in the previous row
    # maybe also increase every player's xp by N xp per row, so the values are always increasing (not static)
    prev_row = {player:0 for player in df.columns}
    for iter_count, data_point in enumerate(data):

        new_row = prev_row # start all players with the same xp as their previous row
        if not is_valid_frame(iter_count, num_frames=len(data)):
            continue

        # check through the gathered data and add any matching xp values
        this_date = datetime.strptime(data_point["timestamp"], "%Y-%m-%d %H:%M:%S")
        print(this_date)
        try:
            this_hiscores_data = data_point["hiscores"][skill]
        except KeyError: # if no data, skip this data_point
            continue

        for player in this_hiscores_data:
            xp_int = int(player["score"].replace(",",""))
            new_row[player["name"]] = xp_int

        # add the row to the main dataframe
        new_row_df = pd.DataFrame(data=new_row, index=[this_date])
        df = pd.concat([df, new_row_df])

        prev_row = new_row # for the next iteration

        print(this_date)

    # Convert all columns to numeric dtype
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    print(df)
    return df


def create_bar_race(df):
    """
    Create a bar chart race from the dataframe given
    """
    time_now = datetime.strftime(datetime.now(), "%Y-%m-%d_%H_%M_%S")
    print(os.path.join(BAR_RACE_VIDEOS_DIR, f"bar_race_{time_now}.mp4"))
    bcr.bar_chart_race(
        df,
        filename=os.path.join(BAR_RACE_VIDEOS_DIR, f"bar_race_{time_now}.mp4"),
        figsize=(16,9),
        n_bars=10,
        dpi=120,
        interpolate_period=True,
        period_length=400,
        steps_per_period=12, # fps = steps_per_period * 10 (default fps is 20, aka steps_per_period is 10)
        filter_column_colors=True,
        shared_fontdict={'family': 'RuneScape Bold Font', 'weight': 'bold', 'color': 'black', 'size': '14'},
        period_label={'x': .70, 'y': .25, 'ha': 'right', 'va': 'center', 'size': '20', 'color': 'dimgray'},
        period_fmt="%b %-d %Y - %H:%m",
        period_summary_func=lambda v, r: {
            'x': .70,
            'y': .15,
            'ha': 'right',
            'va': 'center',
            's': f"""Total value: {v.nlargest(10).sum():,.0f}\n
                        Hello Chaps"""
        }
    )


def main():
    import time
    t1 = time.time()
    print(t1)
    print(time.time() - t1)
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
    df = create_df(
        data=all_sorted_data,
        unique_users_per_skill=unique_users_per_skill,
        skill="necromancy",
        use_each_n=4
    )
    bar_race_video = create_bar_race(df)

    # df = create_df(all_sorted_data)
    # print(df)

    # import pprint
    # for item in all_sorted_data:
    #     pprint.pprint(item)
    #     print()
    #     print()
    # print(len(all_sorted_data))





if __name__ == "__main__":
    main()
    


"""
all_file_data = [
    {
        "timestamp": <timestamp>,
        "hiscores": [
            <skill1>: {
            
            },
            <skill2>: {
            
            }
        ]
    },
    {
        "timestamp": <timestamp>,
        "hiscores": [
            <skill1>: {
            
            },
            <skill2>: {
            
            }
        ]
    },
]
"""

# def get_dict_size(obj):
#     size = sys.getsizeof(obj)
    
#     if isinstance(obj, dict):
#         for value in obj.values():
#             size += get_dict_size(value)
#     elif isinstance(obj, list) or isinstance(obj, tuple):
#         for item in obj:
#             size += get_dict_size(item)
#     elif isinstance(obj, str):
#         size += sys.getsizeof(obj)
    
#     return size

# print(get_dict_size((all_file_data)))