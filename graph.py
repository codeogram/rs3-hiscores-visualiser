import json
import os

RAW_DATA_PATH = "TEST_raw_scraped_data2"

# loading raw_data into memory
all_file_data = []
for file_name in os.listdir(RAW_DATA_PATH):
    if file_name == ".gitignore":
        continue
    # extract file contents
    full_file_path = os.path.join(os.path.dirname(__file__), RAW_DATA_PATH, file_name) # absolute path to the json file
    with open(full_file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
        file_content_dict = json.loads(file_content)

    # organise hiscores data by skill
    if file_content_dict["data"]: # if not an empty list
        hiscores_data = {}
        for hiscores_item in file_content_dict["data"]:
            skill_name = hiscores_item["skill"]["skill"]
            skill_data = json.loads(hiscores_item["skill_data"]) # convert json str into list 
            hiscores_data[skill_name] = skill_data
    else:
        hiscores_data = {}

    # append all the data corresponding to this timestamp, to all_file_data
    file_data = {
        "timestamp": file_content_dict["timestamp"],
        "hiscores": hiscores_data
    }
    all_file_data.append(file_data)


all_file_data = sorted(all_file_data, key=lambda file_data: file_data["timestamp"])
for item in all_file_data:
    # pprint.pprint(item) # for pretty printing of the dictionaries
    print(item)
    print()
    print()


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