#!/usr/bin/env python

"""
Shell to run SQL commands (select, insert, delete, update) on Multiple Oracle DBs.
Koray Oksay <koray.oksay@gmail.com>

HISTORY
-------
  Version 0.1: Initial Release, 20141228 
"""

import cmd
import sys
import cx_Oracle
import tabulate
import logging
from os import path
from ConfigParser import SafeConfigParser
try:
    import readline
except ImportError:
    print "*** readline cannot be imported, history would not be used!.. ***"


class MultipleDB(cmd.Cmd):
    """
    Multiple Databases SQL command processor
    """

    def __init__(self):
        cmd.Cmd.__init__(self)
        dir_name = path.dirname(__file__)
        config_file = path.join(dir_name, '..', 'conf', 'multipledb.conf')
        log_file = path.join(dir_name, '..', 'log', 'multipledb.log')
        logging.basicConfig(filename=log_file, level='INFO', format='%(asctime)s [%(levelname)s] %(message)s',
                            datefmt='%Y%m%d%H%M%S')
        logging.info('Application started')
        self.dbs = self.parse_config(config_file, 'DATABASES')
        self.credentials = self.parse_config(config_file, 'USERS')
        self.db_list = self.dbs.keys()
        self.db_list.append("all")
        self.prompt = "\n(Cmd) "
        self.intro = "Welcome to MultipleDB application.\nVersion: 0.1"
        self.connection = {}

    @staticmethod
    def parse_config(config_file, section):
        """
        Parses config file which was given as command line argument.
        Returns a dictionary
        """
        parser = SafeConfigParser()
        parser.read(config_file)
        config_dict = {}
        for k, v in parser.items(section):
            config_dict[k.upper()] = v 

        return config_dict

    def do_connect(self, name):
        """
        You can connect to specific db with: connect [DB]
        If you want to connect all configured: connect all
        """
        if name == '':
            print "Please provide DB name to connect!...\nRun 'list' command to view available DBs."
            return
        self.connection = self.connect_db(name.upper())

    def complete_connect(self, text, line, beginidx, endidx):
        if not text:
            completions = self.db_list[:]
        else:
            completions = [f for f in self.db_list if f.startswith(text.upper())]
        return completions

    def complete_disconnect(self, text, line, beginidx, endidx):
        if not text:
            completions = self.db_list[:]
        else:
            completions = [f for f in self.db_list if f.startswith(text.upper())]
        return completions

    def do_list(self, line):
        """
        Lists the configured DB names to connect
        """
        print "Configured DBs:"
        for db in sorted(self.dbs.keys()):
            print "* %s" % db

    def do_select(self, line):
        """
        Runs the given SELECT SQL statement
        """
        connections = self.connection
        if not connections:
            print "Not connected to any DB. Run 'connect' command"
            return

        for name, con in connections.items():
            cur = con[0].cursor()
            sql = "select " + line
            print name
            try:
                logging.info('[%-11s] %s' % (name, sql))
                cur.execute(sql)
            except (cx_Oracle.DatabaseError, cx_Oracle.InterfaceError) as e:
                print "Database exception %s" % (str(e).strip())
                logging.error(str(e).strip())
                continue
            rows = cur.fetchall()
            if not rows:
                print "No Data Found...\n"
                cur.close()
                continue
            cols = ()
            for col in cur.description:
                cols += (col[0], )
            print tabulate.tabulate(rows, cols, tablefmt='grid')
            print ""
            cur.close()

    def do_insert(self, line):
        """
        Runs the given INSERT SQL statement
        AutoCommit if OFF, you must run 'commit' command!!!
        """
        connections = self.connection
        if not connections:
            print "Not connected to any DB. Run 'connect' command"
            return

        for name, con in connections.items():
            cur = con[0].cursor()
            sql = "insert " + line
            print name
            try:
                logging.info('[%-11s] %s' % (name, sql))
                cur.execute(sql)
            except (cx_Oracle.DatabaseError, cx_Oracle.InterfaceError) as e:
                print "Database exception %s" % (str(e))
                logging.error(str(e).strip())
                continue

            print "Query OK, %d %s affected\n" % (cur.rowcount, cur.rowcount == 1 and 'row' or 'rows')
            num_rows = cur.rowcount
            logging.info("[%-11s] Query OK, %d %s affected" % (name, num_rows, num_rows == 1 and 'row' or 'rows'))
            if num_rows > 0:
                # there is uncommitted transaction
                self.connection[name][1] = 1
            cur.close()

    def do_update(self, line):
        """
        Runs the given UPDATE SQL statement
        AutoCommit if OFF, you must run 'commit' command!!!
        """
        connections = self.connection
        if not connections:
            print "Not connected to any DB. Run 'connect' command"
            return

        for name, con in connections.items():
            cur = con[0].cursor()
            sql = "update " + line
            print name
            try:
                logging.info('[%-11s] %s' % (name, sql))
                cur.execute(sql)
            except (cx_Oracle.DatabaseError, cx_Oracle.InterfaceError) as e:
                print "Database exception %s" % (str(e))
                logging.error(str(e).strip())
                continue

            print "Query OK, %d %s affected\n" % (cur.rowcount, cur.rowcount == 1 and 'row' or 'rows')
            num_rows = cur.rowcount
            logging.info("[%-11s] Query OK, %d %s affected" % (name, num_rows, num_rows == 1 and 'row' or 'rows'))
            if num_rows > 0:
                # there is uncommitted transaction
                self.connection[name][1] = 1
            cur.close()

    def do_delete(self, line):
        """
        Runs the given DELETE SQL statement
        AutoCommit if OFF, you must run 'commit' command!!!
        """
        connections = self.connection
        if not connections:
            print "Not connected to any DB. Run 'connect' command"
            return

        for name, con in connections.items():
            cur = con[0].cursor()
            sql = "delete " + line
            print name
            try:
                logging.info('[%-11s] %s' % (name, sql))
                cur.execute(sql)
            except (cx_Oracle.DatabaseError, cx_Oracle.InterfaceError) as e:
                print "Database exception %s" % (str(e))
                logging.error(str(e).strip())
                continue

            print "Query OK, %d %s affected\n" % (cur.rowcount, cur.rowcount == 1 and 'row' or 'rows')
            num_rows = cur.rowcount
            logging.info("[%-11s] Query OK, %d %s affected" % (name, num_rows, num_rows == 1 and 'row' or 'rows'))
            if num_rows > 0:
                # there is uncommitted transaction
                self.connection[name][1] = 1
            cur.close()

    def do_commit(self, dbname):
        """
        Commits the transactions on the given database.
        If DB name is not provided, commits on all connected
        """
        connections = self.connection
        if not connections:
            print "Not connected to any DB. Run 'connect' command"
            return

        if dbname == '':
            for dbname, con in connections.items():
                if con[1] == 1:
                    con[0].commit()
                    # no more transactions
                    self.connection[dbname][1] = 0
                    print "%s : committed" % dbname 
                    logging.info('[%-11s] Committed' % dbname)
                else:
                    print "%s : Nothing to commit" % dbname 
                    logging.info('[%-11s] Nothing to commit' % dbname)
        else:
            try:
                con = connections[dbname.upper()]
            except KeyError:
                print "No such DB to commit: %s" % dbname
                logging.error("No such DB to commit: %s" % dbname)
                return
            if con[1] == 1:
                con[0].commit()
                # no more transactions
                self.connection[dbname][1] = 0
                print "%s : commmitted" % dbname.upper()
                logging.info('[%-11s] Committed' % dbname.upper())
            else:
                print "%s : Nothing to commit" % dbname.upper()
                logging.info('[%-11s] Nothing to commit' % dbname.upper())

    def do_rollback(self, dbname):
        """
        Rollbacks the transactions on the given database.
        If DB name is not provided, rollbacks on all connected
        """
        connections = self.connection
        if not connections:
            print "Not connected to any DB. Run 'connect' command"
            return

        if dbname == '':
            for dbname, con in connections.items():
                if con[1] == 1:
                    con[0].rollback()
                    # no more transactions
                    self.connection[dbname][1] = 0
                    print "%s : rollbacked" % dbname
                    logging.info('[%-11s] Rollbacked' % dbname)
                else:
                    print "%s : Nothing to rollback" % dbname
                    logging.info('[%-11s] Nothing to rollback' % dbname)
        else:
            try:
                con = connections[dbname.upper()]
            except KeyError:
                print "No such DB to rollback: %s" % dbname
                logging.error("No such DB to rollback: %s" % dbname)
                return
            if con[1] == 1:
                con[0].rollback()
                # no more transactions
                self.connection[dbname][1] = 0
                print "%s : rollbacked" % dbname.upper()
                logging.info('[%-11s] Rollbacked' % dbname.upper())
            else:
                print "%s : Nothing to rollback" % dbname.upper()
                logging.info('[%-11s] Nothing to rollback' % dbname.upper())

    def do_status(self, line):
        """
        Shows connection status information of DBs
        """
        try:
            for name in sorted(self.dbs.keys()):
                if name in self.connection.keys():
                    print "%-12s: CONNECTED" % name
                else:
                    print "%-12s: NOT CONNECTED" % name
        except AttributeError:
            print "Not connected to any DB. Run 'connect' command"
            return

    def do_EOF(self, line):
        """
        You may exit by hitting Ctrl+D
        """
        self.do_disconnect('all')
        print "Bye..."
        logging.info('Application terminated')
        return True

    def do_quit(self, line):
        """
        Quits the shell
        If there is any open connection to databases, closes.
        Asks to commit/rollback for transactions
        """
        self.do_disconnect('all')
        print "Bye..."
        logging.info('Application terminated')
        sys.exit(0)

    def connect_db(self, db_name):
        credentials = self.credentials
        cons = self.connection

        if db_name == "ALL":
            db_names = self.dbs.keys()
        else:
            db_names = [db_name]

        for db in db_names:
            try:
                dsn = self.dbs[db]
            except KeyError:
                print "No such configured DB to connect!..."
                return
            user = credentials[db].split(';')[0]
            passwd = credentials[db].split(';')[1]

            try:
                con = cx_Oracle.connect(user, passwd, dsn)
            except cx_Oracle.DatabaseError as e:
                print "Cannot connect to db: %s. %s" % (db, str(e))
                logging.error("Cannot connect to db: %s. %s" % (db, str(e)))
                continue

            print "%-12s: CONNECTED" % db
            logging.info('[%-11s] Connected' % db)
            cons[db] = [con, 0]

        return cons

    def do_disconnect(self, db_name):
        """
        Disconnects from the databases.
        Asks to commit/rollback for transactions
        """
        if not db_name or db_name.upper() == "ALL":
            try:
                for name, con in sorted(self.connection.items()):
                    if con[1] == 1:
                        print "Still uncommitted transactions on %s." % name
                        reply = raw_input("Do you want to commit? [y/n] ")
                        if reply.upper() == 'Y':
                            self.do_commit(name)
                        else:
                            self.do_rollback(name)
                        self.connection[name][1] = 0
                    con[0].close()
                    print "Connection Closed: %s" % name
                    logging.info('[%-11s] Disconnected' % name)
                    del self.connection[name]
            except AttributeError:
                pass
        else:
            try:
                con = self.connection[db_name.upper()]
            except (AttributeError, KeyError):
                print "No such DB to disconnect: %s" % db_name
                logging.error("No such DB to disconnect: %s" % db_name)
                return
            if con[1] == 1:
                print "Still uncommitted transactions on %s." % db_name.upper()
                reply = raw_input("Do you want to commit? [y/n] ")
                if reply.upper() == 'Y':
                    self.do_commit(db_name.upper())
                else:
                    self.do_rollback(db_name.upper())
                self.connection[db_name.upper()][1] = 0
            con[0].close()
            print "Connection Closed: %s" % db_name.upper()
            logging.info('[%-11s] Disconnected' % db_name.upper())
            del self.connection[db_name.upper()]

    def emptyline(self):
        pass


if __name__ == '__main__':
    MultipleDB().cmdloop()
