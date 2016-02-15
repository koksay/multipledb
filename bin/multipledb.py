#!/usr/bin/env python

"""
Shell to run SQL commands on Multiple databases.
Runs select and DMLs on Oracle
Runs select on Sybase and MySQL

Koray Oksay <koray.oksay@gmail.com>

HISTORY
-------
  Version 0.1: Initial Release, 20141228
  Version 0.2: Sybase Connection added, 20150105
  Version 0.3: MySQL Connection added, 20150110
  Version 0.4: desc command added for Oracle, 20160215
"""

import cmd
import logging
import logging.handlers
import os
import sys
import tabulate
from ConfigParser import SafeConfigParser
from datetime import datetime
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
        if len(sys.argv) == 2:
            self.db_type = sys.argv[1].upper()
        else:
            print "*** DB Type was not provided. ORACLE was selected by default!.. ***"
            self.db_type = 'ORACLE'
        if self.db_type == 'ORACLE':
            import cx_Oracle
            self.database = cx_Oracle
            self.db_section = 'DATABASES_ORACLE'
            self.user_section = 'USERS_ORACLE'
        elif self.db_type == 'SYBASE':
            import Sybase
            self.database = Sybase
            interfaces_file = os.path.join(os.environ["SYBASE"], 'interfaces')
            if not os.path.exists(interfaces_file):
                print "Cannot find Sybase Interfaces file on: %s." % interfaces_file
                print "Exiting..."
                sys.exit(2)
            self.db_section = 'DATABASES_SYBASE'
            self.user_section = 'USERS_SYBASE'
        elif self.db_type == 'MYSQL':
            import MySQLdb
            self.database = MySQLdb
            self.db_section = 'DATABASES_MYSQL'
            self.user_section = 'USERS_MYSQL'
        else:
            print "*** DB Type must be ORACLE, SYBASE or MYSQL. Exiting..."
            sys.exit(1)
        dir_name = os.path.dirname(__file__)
        config_file = os.path.join(dir_name, '..', 'conf', 'multipledb.conf')
        log_file = os.path.join(dir_name, '..', 'log', 'multipledb.log')
        self.dbs = self.parse_config(config_file, self.db_section)
        self.credentials = self.parse_config(config_file, self.user_section)
        self.db_list = self.dbs.keys()
        self.prompt = "\n(SQL) "
        self.intro = "Welcome to MultipleDB application.\nVersion: 0.4"
        self.connection = {}
        self.logger = self.initiate_logger(log_file)
        self.logger.info('Application started. DB Type: %s' % self.db_type)

    @staticmethod
    def parse_config(config_file, section):
        """
        Parses config file which was given as command line argument.
        :param config_file: Config file path
        :param section: Section to read from the config file
        :return: Dictionary of the configuration
        """
        parser = SafeConfigParser()
        parser.read(config_file)
        config_dict = {}
        for k, v in parser.items(section):
            config_dict[k.upper()] = v

        return config_dict

    @staticmethod
    def initiate_logger(log_file):
        handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(process)5d %(message)s')
        handler.setFormatter(formatter)
        logger = logging.getLogger(__name__)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def do_connect(self, db_name):
        """
        You can connect to specific db with: connect [DB]
        If you want to connect all configured: connect all
        :param name: DB name from config file to connect. If not given, "ALL" will be used
        :return: None
        """
        credentials = self.credentials
        cons = self.connection
        if db_name.upper() in ("", "ALL"):
            db_names = self.db_list
        else:
            db_names = [db_name]

        for db in db_names:
            if db not in self.db_list:
                print "No such configured DB to connect!..."
                return
            user, passwd = credentials[db].split(';')
            try:
                if self.db_type == 'ORACLE':
                    con = self.database.connect(user, passwd, self.dbs[db])
                    con.outputtypehandler = self.NumbersAsString
                elif self.db_type == 'SYBASE':
                    con = self.database.connect(db, user, passwd, self.dbs[db])
                elif self.db_type == 'MYSQL':
                    hostname, port, schema = self.dbs[db].split(':')
                    con = self.database.connect(host=hostname, port=int(port), user=user, passwd=passwd, db=schema)
            except self.database.DatabaseError as e:
                print "Cannot connect to db: %s. %s" % (db, str(e))
                self.logger.error("Cannot connect to db: %s. %s" % (db, str(e)))
                continue
            print "%-12s: CONNECTED" % db
            self.logger.info('[%-11s] Connected' % db)
            cons[db] = [con, 0]
        self.connection = cons

    def complete_connect(self, text, line, beginidx, endidx):
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
        for db in sorted(self.db_list):
            print "* %s" % db

    def do_status(self, line):
        """
        Shows connection status information of DBs
        """
        try:
            for name in sorted(self.dbs.keys()):
                if name in self.connection.keys():
                    print "%-15s: CONNECTED" % name
                else:
                    print "%-15s: NOT CONNECTED" % name
        except AttributeError:
            print "Not connected to any DB. Run 'connect' command"
            return

    def NumbersAsString(self, cursor, name, defaultType, size, precision, scale): 
        if defaultType == self.database.NUMBER: 
            return cursor.var(str, 100, cursor.arraysize)

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
            cur.arraysize = 1000
            sql = "select " + line
            print name
            try:
                self.logger.info('[%-11s] %s' % (name, sql))
                start = datetime.now()
                cur.execute(sql)
                end = datetime.now()
            except (self.database.DatabaseError, self.database.InterfaceError) as e:
                print "Database exception %s" % (str(e).strip())
                self.logger.error(str(e).strip())
                cur.close()
                continue
            duration = end - start
            rows = cur.fetchall()
            if not rows:
                print "Empty set (%.3f sec)\n" % duration.total_seconds()
                cur.close()
                continue
            cols = ()
            for col in cur.description:
                cols += (col[0], )
            print tabulate.tabulate(rows, cols, tablefmt='grid')
            num_rows = len(rows)
            print "%s %s in set (%.3f sec)\n" % \
                  (num_rows, num_rows == 1 and 'row' or 'rows', duration.total_seconds())
            cur.close()

    def do_insert(self, line):
        if self.db_type == 'ORACLE':
            self.insert_oracle(line)
        elif self.db_type == 'SYBASE':
            print "Sybase insert not yet implemented!..."
        elif self.db_type == 'MYSQL':
            print "MySQL insert not yet implemented!..."

    def insert_oracle(self, line):
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
                self.logger.info('[%-11s] %s' % (name, sql))
                cur.execute(sql)
            except (self.database.DatabaseError, self.database.InterfaceError) as e:
                print "Database exception %s" % (str(e))
                self.logger.error(str(e).strip())
                continue
            num_rows = cur.rowcount
            print "Query OK, %d %s affected\n" % (num_rows, num_rows == 1 and 'row' or 'rows')
            self.logger.info("[%-11s] Query OK, %d %s affected" % (name, num_rows, num_rows == 1 and 'row' or 'rows'))
            if num_rows > 0:   # there is an uncommitted transaction
                self.connection[name][1] = 1
            cur.close()

    def do_update(self, line):
        if self.db_type == 'ORACLE':
            self.update_oracle(line)
        elif self.db_type == 'SYBASE':
            print "Sybase update not yet implemented!..."
        elif self.db_type == 'MYSQL':
            print "MySQL update not yet implemented!..."

    def update_oracle(self, line):
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
                self.logger.info('[%-11s] %s' % (name, sql))
                cur.execute(sql)
            except (self.database.DatabaseError, self.database.InterfaceError) as e:
                print "Database exception %s" % (str(e))
                self.logger.error(str(e).strip())
                continue

            num_rows = cur.rowcount
            print "Query OK, %d %s affected\n" % (num_rows, num_rows == 1 and 'row' or 'rows')
            self.logger.info("[%-11s] Query OK, %d %s affected" % (name, num_rows, num_rows == 1 and 'row' or 'rows'))
            if num_rows > 0:   # there is an uncommitted transaction
                self.connection[name][1] = 1
            cur.close()

    def do_delete(self, line):
        if self.db_type == 'ORACLE':
            self.delete_oracle(line)
        elif self.db_type == 'SYBASE':
            print "Sybase update not yet implemented!..."
        elif self.db_type == 'MYSQL':
            print "MySQL update not yet implemented!..."

    def delete_oracle(self, line):
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
                self.logger.info('[%-11s] %s' % (name, sql))
                cur.execute(sql)
            except (self.database.DatabaseError, self.database.InterfaceError) as e:
                print "Database exception %s" % (str(e))
                self.loggererror(str(e).strip())
                continue

            num_rows = cur.rowcount
            print "Query OK, %d %s affected\n" % (num_rows, num_rows == 1 and 'row' or 'rows')
            self.logger.info("[%-11s] Query OK, %d %s affected" % (name, num_rows, num_rows == 1 and 'row' or 'rows'))
            if num_rows > 0:   # there is an uncommitted transaction
                self.connection[name][1] = 1
            cur.close()

    def do_describe(self, table_name):
         self.do_desc(table_name)

    def do_desc(self, table_name):
        if self.db_type == 'ORACLE':
            self.desc_oracle(table_name)
        elif self.db_type == 'SYBASE':
            print "Sybase update not yet implemented!..."
        elif self.db_type == 'MYSQL':
            print "MySQL update not yet implemented!..."

    def desc_oracle(self, table_name):
        connections = self.connection
        if not connections:
            print "Not connected to any DB. Run 'connect' command"
            return

        for name, con in connections.items():
            cur = con[0].cursor()
            sql = 'select * from %s where 1=0' % table_name
            print name
            try:
                self.logger.info('[%-11s] %s' % (name, sql))
                start = datetime.now()
                cur.execute(sql)
                end = datetime.now()
            except (self.database.DatabaseError, self.database.InterfaceError) as e:
                print "Database exception %s" % (str(e).strip())
                self.logger.error(str(e).strip())
                cur.close()
                continue
            duration = end - start
            data = []
            columns = ['Column Name', 'Data Type', 'Data Length', 'Null?']
            for col in cur.description:
                col_name = col[0]
                data_type = col[1].__name__
                data_length = col[3]
                nullable = col[6]
                data.append([col_name, data_type, data_length, nullable])
                
            print tabulate.tabulate(data, columns, tablefmt='grid')
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
                    self.logger.info('[%-11s] Committed' % dbname)
                else:
                    print "%s : Nothing to commit" % dbname
                    self.logger.info('[%-11s] Nothing to commit' % dbname)
        else:
            try:
                con = connections[dbname.upper()]
            except KeyError:
                print "No such DB to commit: %s" % dbname
                self.logger.error("No such DB to commit: %s" % dbname)
                return
            if con[1] == 1:
                con[0].commit()
                # no more transactions
                self.connection[dbname][1] = 0
                print "%s : commmitted" % dbname.upper()
                self.logger.info('[%-11s] Committed' % dbname.upper())
            else:
                print "%s : Nothing to commit" % dbname.upper()
                self.logger.info('[%-11s] Nothing to commit' % dbname.upper())

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
                    self.logger.info('[%-11s] Rollbacked' % dbname)
                else:
                    print "%s : Nothing to rollback" % dbname
                    self.logger.info('[%-11s] Nothing to rollback' % dbname)
        else:
            try:
                con = connections[dbname.upper()]
            except KeyError:
                print "No such DB to rollback: %s" % dbname
                self.logger.error("No such DB to rollback: %s" % dbname)
                return
            if con[1] == 1:
                con[0].rollback()
                # no more transactions
                self.connection[dbname][1] = 0
                print "%s : rollbacked" % dbname.upper()
                self.logger.info('[%-11s] Rollbacked' % dbname.upper())
            else:
                print "%s : Nothing to rollback" % dbname.upper()
                self.logger.info('[%-11s] Nothing to rollback' % dbname.upper())

    def do_disconnect(self, db_name):
        """
        Disconnects from the databases.
        Asks to commit/rollback for transactions
        """
        if db_name.upper() in ("", "ALL"):
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
                    self.logger.info('[%-11s] Disconnected' % name)
                    del self.connection[name]
            except AttributeError:
                pass
        else:
            try:
                con = self.connection[db_name.upper()]
            except (AttributeError, KeyError):
                print "No such DB to disconnect: %s" % db_name
                self.logger.error("No such DB to disconnect: %s" % db_name)
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
            self.logger.info('[%-11s] Disconnected' % db_name.upper())
            del self.connection[db_name.upper()]

    def complete_disconnect(self, text, line, beginidx, endidx):
        if not text:
            completions = self.db_list[:]
        else:
            completions = [f for f in self.db_list if f.startswith(text.upper())]
        return completions

    def do_EOF(self, line):
        """
        You may exit by hitting Ctrl+D
        """
        self.do_quit(line)

    def do_quit(self, line):
        """
        Quits the shell
        If there is any open connection to databases, closes.
        Asks to commit/rollback for transactions
        """
        self.do_disconnect('ALL')
        print "Bye..."
        self.logger.info('Application terminated')
        sys.exit(0)

    def emptyline(self):
        pass


if __name__ == '__main__':
    MultipleDB().cmdloop()
