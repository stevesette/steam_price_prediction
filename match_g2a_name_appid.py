import sqlite3
import os


# Calculates the mean of a list of tuples of prices
# Price - list of tuples with price at 0th index of the tuple
# Return - Mean of all prices (double)
def mean(prices):
    total_price = 0
    total_entries = 0
    for price in prices:
        total_price += price[0]
        total_entries += 1
    if total_entries != 0:
        return total_price / total_entries
    else:
        return 0

# Make connection to sqlite database and create cursor
conn = sqlite3.connect(os.getcwd() + "/g2a_vs_steam.db")
cur = conn.cursor()
# SELECT ALL GameName and AppIds from the steam database
select_steam_names = "SELECT GameName, AppId FROM appid_name"
cur.execute(select_steam_names)
results = cur.fetc
# For each result we are going to check if there is a g2a name similar to it and if so update the "G2AName" column with
# the name found on G2A
update_set = "UPDATE appid_name SET G2AMeanPrice = ? WHERE AppId = ?"
# The number of rows updated
count_updates = 0
# Loops through all of the results
for result in results:
    # Selects the prices from the g2a scrape whenever the game name is similar to a steam game name
    select_g2a_prices = "SELECT LowestOfferedPrice FROM g2a_scrape WHERE FullGameName LIKE "
    # Finishes formatting the like statement with wildcards before and after
    name = '\'%' + result[0].replace("'", "") + '%\''
    # Executes query
    cur.execute(select_g2a_prices + name)
    # Retrieves all results of the query
    g2a_prices = cur.fetchall()
    # If there is nothing that is similar to the g2a name (i.e. steam gift cards do not have a representation in
    # the steam store and should not be included) then skip the entry
    if len(g2a_prices) == 0:
        continue
    # By doing the manual entry method i tried earlier i discovered that whenever there are around 20 rows they usually
    # refer to different area versions of the game (i.e. a g2a code available for global use vs only for north america
    # and as a result we can average them out rather than picking one and getting rid of the other options
    elif len(g2a_prices) <= 20:
        count_updates += 1
        cur.execute(update_set, (mean(g2a_prices), result[1]))
    # If there are more than there are probably many things that apply and are irrelevant to the actual game so do
    # nothing
    else:
        pass

print("Rows updated: " + str(count_updates))

# commit updates and close connection
conn.commit()
conn.close()
