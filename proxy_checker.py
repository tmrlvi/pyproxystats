#!/bin/env python27
"""
The main script for managing the proxy list. Run with -h.
@author tmrlvi
"""
import sqlite3
import csv
import argparse

import proxy_db_manager
import stats


def add_proxy(args):
    manager = proxy_db_manager.ProxyDBManager(args.db_filename)
    try:
        manager.add_proxy(args.address, args.port, args.type)
    except sqlite3.IntegrityError, e:
        print "ERROR: The proxy you tried to add probably exists"
    
def load_csv(args):
    manager = proxy_db_manager.ProxyDBManager(args.db_filename)
    for row in csv.DictReader(open(args.filename)):
        if row["type"] == "socks4/5":
            row["type"] = "socks5"
        manager.add_proxy(row['ip'], int(row['port']), row["type"].lower())
        
def list_proxies(args):
    manager = proxy_db_manager.ProxyDBManager(args.db_filename)
    for row in manager.get_proxies_stats():
        print "\t".join(map(str, row))
        
def run_stats(args):
    manager = proxy_db_manager.ProxyDBManager(args.db_filename)
    proxies = manager.get_proxies_by_type()
    for type in proxies:
        for proxy, port in proxies[type]:
            success_rate, average_speed, error_desc = stats.get_stats(type, proxy, port)
            manager.update(proxy, port, type, success_rate, average_speed, error_desc)         

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--db", dest="db_filename", default=proxy_db_manager.ProxyDBManager.SQLITE_FILE,
                        help="the path to the proxies db")
                        
    subparsers = parser.add_subparsers(title='subcommands')
                                        
    addparser = subparsers.add_parser('add', description='Add new proxy to list')
    addparser.add_argument('type', metavar='type', type=str,
                       help='Proxy type', choices=["http", "https", "socks4", "socks5"])
    addparser.add_argument('address', metavar='ip', type=str,
                       help='IP address of the proxy')
    addparser.add_argument('port', metavar='port', type=int,
                        help='port of the proxy')
    addparser.set_defaults(run=add_proxy)

    csvparser = subparsers.add_parser('csv', description='Add new proxy to list from csv')
    csvparser.add_argument('filename', metavar='FILE', type=str,
                       help='CSV file to read from')
    csvparser.set_defaults(run=load_csv)
                       
    statparser = subparsers.add_parser('list')
    statparser.set_defaults(run=list_proxies)
                       
    statparser = subparsers.add_parser('stats')
    statparser.set_defaults(run=run_stats)

    args = parser.parse_args()
    args.run(args)

if __name__ == "__main__":
    main()
