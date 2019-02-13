import tinydb
import os
import sqlite3
import datetime


# Creates a Date for a passed date string
# Args: dat_string - date in the format "Mon Day, Year"
# Retruns : Date or none if there are errors
def date_string_to_date(date_string):
    dates = date_string.split()
    try:
        dates[0] = month_to_int(dates[0])
        dates[1] = int(dates[1].replace(",", ""))
        dates[2] = int(dates[2])
        return datetime.date(year=dates[2], month=dates[0], day=dates[1])
    except Exception as e:
        print e.message
        print "Error for your Date, you passed " + date_string
        return None


# Creates a number that represents the passed month
# Args: month (string) in 3 letter format
# Returns: An int between 1-12 or None if there was an error
def month_to_int(month):
    month_num = {"Jan": 1,
                 "Feb": 2,
                 "Mar": 3,
                 "Apr": 4,
                 "May": 5,
                 "Jun": 6,
                 "Jul": 7,
                 "Aug": 8,
                 "Sep": 9,
                 "Oct": 10,
                 "Nov": 11,
                 "Dec": 12}
    if month not in month_num:
        print "Your month is not in month_num, you passed " + str(month)
        return None
    return month_num[month]


# Creates a string representation of a passed list
# Args: l (list of strings) which will be used to make the string
# Returns: a String representation of l
def list_to_string(l):
    first = True
    rtn = ""
    for item in l:
        if not first:
            rtn += ","
        rtn += item
        first = False
    return rtn


# Creates a string representation of the passed dict's values
# Args: l (list of dict of string) which will be parsed into a string
#       kw (string) keyword of the dict
# Returns: A string representation of all dictionary values
def list_dict_to_string(l, kw):
    first = True
    rtn = ""
    for item in l:
        if not first:
            rtn += ","
        rtn += item[kw]
        first = False
    return rtn

# Make sqlite connection and cursor
conn = sqlite3.Connection(os.getcwd() + "/g2a_vs_steam.db")
cur = conn.cursor()
insert_into = "INSERT INTO steam_scrape (AppID, OriginalPrice, DiscountedPrice, ReleaseDate, MetacriticScore, " \
              "IsGame, Developer, Publisher, Genre, IsWindows, IsMac, IsLinux, Categories) " \
              "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"

# Create connection to tinydb nosql db
tiny_db = tinydb.TinyDB(os.getcwd() + "/steam_raw_scrape.json")
# For every document in the tinydb we need to extract the values that we need for the transactional sql db
for doc in iter(tiny_db):
    # Set the variables initially to none in case an entry is missing a dictionary key that we use
    is_game = None
    is_linux = None
    is_mac = None
    is_windows = None
    meta_score = None
    initial_price = None
    final_price = None
    genre_string = None
    publisher_string = None
    developer_string = None
    date = None
    categories_string = None

    # All entries should have an app id which we will use both as a primary key for the sql db but also as dict key
    app_id = doc.keys()[0]
    if 'data' not in doc[app_id].keys():
        print "No 'data' key in JSON", app_id, doc
    else:
        list_of_keys = doc[app_id]['data'].keys()
        if 'type' in list_of_keys:
            is_game = int(doc[app_id]['data']['type'] == 'game')
        if 'platforms' in list_of_keys:
            platforms = doc[app_id]['data']['platforms']
            is_windows = int(platforms['windows'])
            is_mac = int(platforms['mac'])
            is_linux = int(platforms['linux'])
        if 'price_overview' in list_of_keys:
            initial_price = doc[app_id]['data']['price_overview']['initial'] / 100.
            final_price = doc[app_id]['data']['price_overview']['final'] / 100.
        if 'genres' in list_of_keys:
            genre_string = list_dict_to_string(doc[app_id]['data']['genres'], 'description')
        if 'metacritic' in list_of_keys:
            meta_score = doc[app_id]['data']['metacritic']['score']
        if 'publishers' in list_of_keys:
            publisher_string = list_to_string(doc[app_id]['data']['publishers'])
        if 'developers' in list_of_keys:
            developer_string = list_to_string(doc[app_id]['data']['developers'])
        if 'release_date' in list_of_keys:
            date = date_string_to_date(doc[app_id]['data']['release_date']['date'])
        if 'categories' in list_of_keys:
            categories_string = list_dict_to_string(doc[app_id]['data']['categories'], 'description')
        tuple_to_insert = (int(app_id), initial_price, final_price, date, meta_score, is_game, developer_string,
                           publisher_string, genre_string, is_windows, is_mac, is_linux, categories_string)
        try:
            cur.execute(insert_into, tuple_to_insert)
        except sqlite3.IntegrityError:
            pass

# commit insertion and close connection
conn.commit()
conn.close()
