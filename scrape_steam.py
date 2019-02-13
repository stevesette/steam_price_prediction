import os
import requests
import json
import tinydb
import sqlite3

# Create connection to sqlite db and make a cursor for it
conn = sqlite3.connect(os.getcwd() + "/g2a_vs_steam.db")
cur = conn.cursor()

# selection query for appids
select_appids = "SELECT appid FROM appid_name WHERE G2AMeanPrice IS NOT NULL"
cur.execute(select_appids)
appids = cur.fetchall()

# Create connection to tinydb nosql db
tiny_db = tinydb.TinyDB(os.getcwd() + "/steam_raw_scrape.json")

# The steam api allows us to get json data for each appid but since there is a limit to the api calls its best to store
# the returned json in the nosql db so that we do not hit our limit while still figuring out the best parsing patterns
# and for ease of finding each value that we need
steam_api_string_1 = "http://store.steampowered.com/api/appdetails?appids="
steam_api_string_2 = "&cc=us"

# For every appid that we found a g2a price for we need to retrieve the json data and insert it into the tinydb
count = 0
count_timeouts = 0
for appid in appids:
    steam_api_string = steam_api_string_1 + str(appid[0]) + steam_api_string_2
    api_rtn = requests.get(steam_api_string)
    # makes json value of the returned request
    json_val = json.loads(api_rtn.text)
    # insert into tinydb json database
    try:
        tiny_db.insert(json_val)
        count += 1
    except ValueError as e:
        cur.execute("INSERT INTO appid_api_timeouts (AppID, Resolved) VALUES (?,?)", (appid[0], 0))
        count_timeouts += 1
        conn.commit()

print str(count) + " - documents entered"
print str(count_timeouts) + " - documents returned null because of timeout-errors"

# if there are any timeout errors lets try to resolve them
while count_timeouts > 0:
    cur.execute("SELECT AppID FROM appid_api_timeouts WHERE Resolved = 0")
    failed_appids = cur.fetchall()
    for failed_appid in failed_appids:
        steam_api_string = steam_api_string_1 + str(appid[0]) + steam_api_string_2
        api_rtn = requests.get(steam_api_string)
        # makes json value of the returned request
        json_val = json.loads(api_rtn.text)
        # insert into tinydb json database
        try:
            # Try to insert this value again
            tiny_db.insert(json_val)
            # If it succeeds we reach this line which updates successful count and the status in the sql table
            count += 1
            count_timeouts -= 1
            update_string = "UPDATE appid_api_timeouts SET Resolved=1 WHERE AppID=" + str(failed_appid[0])
            # We should execute and commit right away in case any other errors ruin our data
            cur.execute(update_string)
            conn.commit()
        # if the document continues to fail the value in the table should stay at 0 (failed)
        except ValueError as e:
            pass

    # Update user on the failed documents correction attempt
    print str(count) + " - previously failed documents corrected"
    print str(count_timeouts) + " - previously failed documents could not be corrected"


# closes connection to sqlite db
conn.close()
