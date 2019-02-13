import sqlite3
import os
import json

# Make connection to sqlite database and create cursor
conn = sqlite3.connect(os.getcwd() + "/g2a_vs_steam.db")
cur = conn.cursor()

# Retrieve json file and read it
json_data = open(os.getcwd() + "/steam_json_appids.json").read()
# load it as a json object
app_ids = json.loads(json_data)
# get to the point at which the json changes
base_level = app_ids['applist']['apps']['app']

# Base insertion statement
insert_into = "INSERT INTO appid_name (AppId, GameName, G2AMeanPrice) VALUES (?,?,?)"
for app in xrange(0, len(base_level)):
    # Grab appid and name and insert them as well as none which will be edited later
    cur.execute(insert_into, (base_level[app]['appid'], base_level[app]['name'], None))
# Finalize all changes
conn.commit()

# verify that the insertion worked
cur.execute("SELECT * FROM appid_name")
print(cur.fetchall())

# close the connection
conn.close()
