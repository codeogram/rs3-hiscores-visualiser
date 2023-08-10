import pandas as pd
from datetime import datetime, timedelta
import bar_chart_race as bcr
import os

if os.environ.get("DEBUG") == "false": # if in production
    debug_prefix = ""
else:
    debug_prefix = "TEST_"

BAR_RACE_VIDEOS_DIR = f"{debug_prefix}bar_races"
print(BAR_RACE_VIDEOS_DIR)


# creating random values
dates = [datetime.strftime(datetime.now()+timedelta(days=n), "%Y-%m-%d") for n in range(10)]
values = {
    "apple": [x for x in range(10)],
    "banana": [x+5 for x in range(10)],
    "cheese": [x*2 for x in range(10)]
}
df = pd.DataFrame(data=values, index=dates)
print(df)

import time
t1 = time.time()
print(t1)
# bar chart race
time_now = datetime.strftime(datetime.now(), "%Y-%m-%d_%H_%M_%S")
bcr.bar_chart_race(
    df,
    filename=os.path.join(BAR_RACE_VIDEOS_DIR, f"bar_race_{time_now}.mp4"),
    figsize=(16,9),
    period_label=True,
    dpi=120,
    steps_per_period=30, # fps = steps_per_period * 10 (default fps is 20, aka steps_per_period is 10)
)
print(time.time() - t1)