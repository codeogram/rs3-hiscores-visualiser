# RuneScape 3 Hiscores Scraper & Bar Chart Race Generator

Functionality for scraping the RuneScape 3 Hiscores, using the [official Hiscores API](https://runescape.wiki/w/Application_programming_interface#Hiscores), and using the data to produce a "bar chart race", which can dynamically illustrate how the XP of each of the top players varies over time.

For example, I used it to create a visualisation of the **Race to 200m Necromancy**, which began on 7th August 2023 and lasted 5 days.

![bar_chart_race_example](https://github.com/codeogram/rs-hiscores-scraper/assets/87808600/eb7c6281-b0a2-42d4-9e8e-83fece1907d3)

---

## File Breakdown

- **scrape.py** - a script that allows the user to scrape the RuneScape 3 hiscores at specified intervals, with one or more specified in-game skills.

- **graph.py** - having created a dataset from running **scrape.py** for a period of time, **graph.py** converts the raw data into a "bar chart race", using the Python package **[bar-chart-race](https://pypi.org/project/bar-chart-race/)**.

- **for_logging.py** - defines the `MyLogger` class, which is used to log relevant actions and changes in **Logs/**

- **raw_data/** - raw data that is scraped from the Hiscores API is stored here

- **raw_data_scraped/** - once you are ready to run **graph.py**, move your raw data (from **raw_data/**) into this directory

- **bar_races/** - stores the bar chart race video files; the final output from **graph.py**

- **helper_files/** - stores helper/helpful files, including **xp_per_level.csv** and **skills.json**, which are used in the scripts

- **logs/** - stores logs

## Setup & Usage

- Ensure you have Python 3.9 (or newer) installed on your system.

- Whilst running a Python virtual environment, navigate to the root of this repository and run `python -r requirements.txt` in the terminal to install the required dependencies.

- Create an environment variable called `DEBUG` (all caps) and set its value to `"false"`.

  **Linux terminal:** `export DEBUG=false`<br>
  **Windows (CMD):** `set DEBUG=false`<br>
  **Windows (PS):** `$env:DEBUG="false"`<br>

  This is to ensure that the raw data and bar chart races are saved to the correct locations.

- Run **scrape.py** to gather a collection of data over a period of time:

  `python scrape.py <scrape_interval_in_mins> [specified_skills]`<br>
  **example usage** - _python scrape.py 5 mining woodcutting necromancy_ - "every 5 minutes, scrape the Mining, Woodcutting and Necromancy hiscores"<br>
  Note: if no skills are specified, by default the _overall_ leaderboard will be scraped.

- Once the raw data has been generated, use **graph.py** to use the data to create bar chart race:

  `python graph.py` (no additional arguments required)<br>

### Additional Notes

- Although **graph.py** takes no additional command-line arguments, you can still modify the styling of the bar chart race by changing the values of the keyword arguments in the `bcr.bar_chart_race()` function call, inside the script. Note the default values as laid out in the script: you may wish to modify these depending on what data you are illustrating.

- If you do not have the RuneScape font installed on your system, you can either install it and proceed, or remove the selected font from `bcr.bar_chart_race()`.

- If there are specific users you wish to exclude from your bar chart race (for example, if they were bug-abusing XP), create a **banned_users.txt** file and place it in **helper_files/**. In the text file, list each banned player on a new line (case sensitive), and they will be excluded from the final bar chart race.
