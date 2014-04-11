"""
The DB managing module.
@author: tmrlvi
"""
import sqlite3
import time
import datetime
import os

class ProxyDBManager(object):
    SQLITE_FILE="test.sqlite"
    
    def __init__(self, filename=SQLITE_FILE):
        """
        Creates a new DB or loads an existing one
        """
        create = False
        if not os.path.exists(filename):
            create = True
        self.con = sqlite3.connect(filename)
        if create:
            self._create_tables()
        
    def _create_tables(self):
        """
        Creates the tables that need to be in order for the DB to be
        functional
        """
        self.con.execute("DROP TABLE IF EXISTS proxies")
        self.con.execute("DROP TABLE IF EXISTS status")
        self.con.execute("""CREATE TABLE proxies
                        ( id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          url TEXT NOT NULL,
                          port INTEGER,
                          type TEXT NOT NULL,
                          last_checked INTEGER,
                          success_rate REAL,
                          average_speed REAL,
                          common_error TEXT,
                          CONSTRAINT unq UNIQUE (url, port, type)
                        )""")
        self.con.commit()

    def add_proxy(self, url, port, type):
        self.con.execute("""INSERT INTO proxies (url, port, type) 
                            VALUES (:url, :port, :type)""", {"url" : url, "port" : port, "type" : type})
        self.con.commit()
        
    def update_proxy(self, url, port, type, success_rate, average_speed, common_error):
        last_checked = time.time()
        self.con.execute("""UPDATE proxies SET success_rate = :success_rate,
                                               average_speed = :average_speed,
                                               last_checked = :last_checked, 
                                               common_error = :common_error
                            WHERE url = :url AND port = :port AND type = :type""",
                            { "success_rate"    : success_rate,
                              "average_speed"   : average_speed,
                              "last_checked"    : last_checked,
                              "common_error"    : common_error,
                              "url"             : url,
                              "port"            : port,
                              "type"            : type,
                            })
        self.con.commit()
    
    def __del__(self):
        self.con.rollback()
        self.con.close()
        
    def get_proxies_by_type(self):
        proxies = {}
        for url, port, type in self.con.execute("SELECT url, port, type FROM proxies"):
            proxies.setdefault(type, []).append((url, port))
        return proxies
        
    def get_proxies_stats(self):
        """
        Returns a list of proxies and statistics. Intended to be printed.
        """
        proxies = [["url", "port", "type", "last_checked", "success_rate",  "average_speed", "common_error"]]
        for row in self.con.execute("""SELECT url, port, type, datetime(last_checked, 'unixepoch') last_checked, 
                                              success_rate, average_speed, common_error FROM proxies"""):
            proxies.append(row)
        return proxies
