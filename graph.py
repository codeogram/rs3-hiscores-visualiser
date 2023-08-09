import json
import os
import sys

RAW_DATA_DIR_PATH = "TEST_raw_scraped_data2"


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


def main():
    all_file_data = []
    for file_name in os.listdir(RAW_DATA_DIR_PATH):
        if ".json" not in file_name:
            continue
        full_file_path = get_full_file_path(raw_data_dir_path=RAW_DATA_DIR_PATH, file_name=file_name)
        data_dict = get_data_from_json_file(full_file_path)
        data_dict_organised = organise_dict_data(data_dict) if data_dict else data_dict
        all_file_data.append(data_dict_organised)
    all_sorted_data = sort_all_data_by_date(all_file_data)

    for item in all_sorted_data:
        print(item)
        print()
        print()
    print(len(all_sorted_data))

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