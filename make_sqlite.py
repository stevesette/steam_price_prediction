import sqlite3
from sqlite3 import Error
import os


def make_g2a(connection):
    cur = connection.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS g2a_scrape (FullGameName varchar(255), LowestOfferedPrice double(6))")
    print "Made g2a_scrape table"


def make_steam(connection):
    cur = connection.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS steam_scrape (AppID int NOT NULL PRIMARY KEY, OriginalPrice double, "
                "DiscountedPrice double, ReleaseDate date, MetacriticScore int, IsGame bit, Developer text, "
                "Publisher text, Genre text, IsWindows bit, IsMac bit, IsLinux bit, Categories text)")
    print "Made steam_scrape table"


def make_appid_name(connection):
    cur = connection.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS appid_name (AppID int NOT NULL PRIMARY KEY, GameName varchar(255),"
                " G2AMeanPrice double)")
    print "Made appid_name table"


def make_appid_api_timeouts(connection):
    cur = connection.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS appid_api_timeouts (AppID int NOT NULL PRIMARY KEY, Resolved BIT)")
    print "Made appid_api_timeouts"


def make_connection():
    try:
        conn = sqlite3.connect(os.getcwd() + "/g2a_vs_steam.db")
        make_g2a(conn)
        make_steam(conn)
        make_appid_name(conn)
        make_appid_api_timeouts(conn)
    except Error:
        print(Error)
    finally:
        conn.commit()
        conn.close()


if __name__ == "__main__":
    make_connection()
