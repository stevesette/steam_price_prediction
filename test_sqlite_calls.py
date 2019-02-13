import sqlite3
import os

# Make connection to sqlite database and create cursor
conn = sqlite3.connect(os.getcwd() + "/g2a_vs_steam.db")
cur = conn.cursor()

# cur.execute("SELECT * FROM appid_name")
# results = cur.fetchall()
# cur.execute("DROP TABLE appid_name")
# conn.commit()
# cur.execute("CREATE TABLE IF NOT EXISTS appid_name (AppID int NOT NULL PRIMARY KEY, GameName varchar(255),"
#                 " G2AMeanPrice double)")
# conn.commit()
# insert_data = "INSERT INTO appid_name (AppId, GameName, G2AMeanPrice) VALUES (?,?,?)"
# count = 0
# for result in results:
#     cur.execute(insert_data, result)
#     count += 1
# print str(count) + " - Rows inserted"

# cur.execute("SELECT * FROM appid_api_timeouts WHERE Resolved=0")
# print cur.fetchall()
# # cur.execute("UPDATE appid_api_timeouts SET Resolved=1 WHERE AppID=10")
# conn.commit()
# cur.execute("SELECT COUNT(appid) FROM appid_api_timeouts")
# print cur.fetchall()
# cur.execute("DELETE FROM appid_api_timeouts")
cur.execute("SELECT appid_name.G2AMeanPrice, steam_scrape.AppID, OriginalPrice, DiscountedPrice, ReleaseDate, "
            "MetacriticScore, " \
              "IsGame, Developer, Publisher, Genre, IsWindows, IsMac, IsLinux, Categories FROM [steam_scrape] "
            "JOIN appid_name ON [steam_scrape].AppID = appid_name.AppID")
print cur.fetchall()
# cur.execute("DELETE FROM steam_scrape")
# conn.commit()
cur.execute("SELECT COUNT(appid) FROM steam_scrape")
print cur.fetchall()
conn.commit()
conn.close()
