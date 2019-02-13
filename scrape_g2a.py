from lxml import html
import sqlite3
import requests
import os


# string: str - Name of game which may have unicode characters
# Removes all unicode superstring characters from the passed string and replaces them with a non superscript character
def superscript_to_number(string):
    # dict of unicode number representation in superscript to their non superscript string equivalent
    unicode_string = {u'\u2070': "0",
                      u'\xb9': "1",
                      u'\xb2': "2",
                      u'\xb3': "3",
                      u'\u2074': "4",
                      u'\u2075': "5",
                      u'\u2076': "6",
                      u'\u2077': "7",
                      u'\u2078': "8",
                      u'\u2079': "9"}
    for key in unicode_string.keys():
        string.replace(key, unicode_string[key])
    # Return: str - passed string but without unicode characters
    return string


# The beginning of the url we are scraping
start_url = "https://www.g2a.com/en-us/category/games?page="
# ensures that we only check for games available on the Steam platform
steam_platform = "&platform=1"
# connects to local sqlite database (assumes make_sqlite.py has been run)
conn = sqlite3.connect(os.getcwd() + "/g2a_vs_steam.db")
cur = conn.cursor()
# Remove all data we currently have so we can only pull the new data
cur.execute('DELETE FROM g2a_scrape')
conn.commit()
# Check that the deletion was successful
cur.execute("SELECT * FROM g2a_scrape")
print(cur.fetchall())
# Used for debugging exceptions so that the user can find which product (item/key for sale) is causing an issue
cur_page = 0
cur_item = 0
try:
    # Generic insert into string to be reused constantly
    insert_into = 'INSERT INTO g2a_scrape (FullGameName, LowestOfferedPrice) VALUES (?, ?)'
    # Beginning xpath to get to each product
    root_path = '//*[@id="app"]/div/div[2]/div/div/section/div/ul/li['
    # This is the ending path used for price when there are multiple offers on g2a
    price_path_end = ']/div/div/div[2]/div[2]/div/span[2]/text()'
    # This is the ending path used for price when there is only one offer on g2a
    price_path_end_no_from = ']/div/div/div[2]/div[2]/div/span/text()'
    # Ending path to retrieve name of game
    name_path_end = ']/div/div/div[2]/div[1]/div/h3/a/text()'
    for page_num in xrange(1, 501):
        cur_page = page_num
        if page_num % 10 == 0:
            # Print updates so the user knows that the scraper is working
            print(page_num)
        # full url of each page
        url = start_url + str(page_num) + steam_platform
        # returns html of url
        response = requests.get(url)
        # creates tree structure to parse through from the html
        tree = html.fromstring(response.content)
        how_many = len(tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "price", " " ))]'))
        for item_num in xrange(1, how_many + 1):
            cur_item = item_num
            price_path = root_path + str(item_num) + price_path_end
            try:
                r_price = float(tree.xpath(price_path)[0])
            except IndexError:
                r_price = float(tree.xpath(root_path + str(item_num) + price_path_end_no_from)[0])
            name_path = root_path + str(item_num) + name_path_end
            r_name = superscript_to_number(tree.xpath(name_path)[0])
            cur.execute(insert_into, (r_name, r_price))
    # Makes all insertions into the database permanent
    conn.commit()
# If something goes wrong show me both the error and what page we were on
except Exception as e:
    print(type(e))
    print(price_path)
    print(page_num)
    print(item_num)
    print(e)


# Retrieve everything inserted and view them to ensure that the scraper worked
cur.execute("SELECT * FROM g2a_scrape")
print(cur.fetchall())

# close the connection to the database
conn.close()
