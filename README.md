MultipleDB
==========

Shell to run SQL commands on more than one DB at the same time. Currently, only below commands are implemented:

```
ORACLE: select, insert, update, delete
SYBASE: select
MySQL: select
```

Depending on the database you want to connect, one or more of the following modules are required:
- cx_Oracle (http://cx-oracle.sourceforge.net):
pip install cx_Oracle

- python-mysql (https://pypi.python.org/pypi/MySQL-python/1.2.5)

- python-sybase (http://python-sybase.sourceforge.net) 

Following module is required:

- tabulate (https://pypi.python.org/pypi/tabulate):
pip install tabulate

Readline module is optional, but it provides better interface like history, backspace/arrow keys, ..etc.

## Configuration
The config file under "conf" directory is used for DB configuration. 

- Under [DATABASES] section, dsn information is given for each database. 
- Under [USERS] section, username/password information is given for each database. The credentials are seperated by ";"

Example:
```
[DATABASES]
[DATABASES_ORACLE]
DB1 = (DESCRIPTION=(FAILOVER=on)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=db1_1-vip.foo.bar)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=db1_2-vip.foo.bar)(PORT=1521)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=session)(METHOD=basic)(RETRIES=180)(DELAY=5))(SERVER=dedicated)(SERVICE_NAME=testdb)))
DB2 = (DESCRIPTION=(FAILOVER=on)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=db2_1-vip.foo.bar)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=db2_2-vip.foo.bar)(PORT=1521)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=session)(METHOD=basic)(RETRIES=180)(DELAY=5))(SERVER=dedicated)(SERVICE_NAME=testdb)))

[USERS_ORACLE]
DB1 = user1;password1
DB2 = user2;password2

[DATABASES_SYBASE]
SYBASE_DB1 = database1
SYBASE_DB2 = database2

[USERS_SYBASE]
SYBASE_DB1 = user1;password1
SYBASE_DB2 = user2;password2

[DATABASES_MYSQL]
MYSQL_DB1 = 10.10.10.1:3306:database1
MYSQL_DB2 = 10.10.10.2:3306:database2

[USERS_MYSQL]
MYSQL_DB1 = user1;password1
MYSQL_DB2 = user2;password2
```


## Usage Example

```
$ ./multipledb.py
*** DB Type was not provided. ORACLE was selected by default!.. ***
Welcome to MultipleDB application.
Version: 0.3

(Cmd) list
Configured DBs:
* DB1
* DB2

(Cmd) connect all
DB1         : CONNECTED
DB2         : CONNECTED

(Cmd) select * from operator_timezones where mcc_mnc like '286%'
DB1
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|   OPERATOR_ID | OPERATOR_DESCRIPTION           |    MCC_MNC |   WINTER_NGEO_TIMEZONE |   SUMMER_NGEO_TIMEZONE | SUMMER_DAYLIGHT_SAVING_DATE   | WINTER_DAYLIGHT_SAVING_DATE   |
+===============+================================+============+========================+========================+===============================+===============================+
|            26 | Turkcell                       | 2860128601 |                   8765 |                   8765 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1500 | Vodafone Telekomunikasyon A.S. |      28602 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1501 | Avea ?letisim Hizmetleri A.S.  |      28603 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1501 | Avea ?letisim Hizmetleri A.S.  |      28604 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+

DB2
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|   OPERATOR_ID | OPERATOR_DESCRIPTION           |    MCC_MNC |   WINTER_NGEO_TIMEZONE |   SUMMER_NGEO_TIMEZONE | SUMMER_DAYLIGHT_SAVING_DATE   | WINTER_DAYLIGHT_SAVING_DATE   |
+===============+================================+============+========================+========================+===============================+===============================+
|            26 | Turkcell                       | 2860128601 |                   8765 |                   8765 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1500 | Vodafone Telekomunikasyon A.S. |      28602 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1501 | Avea ?letisim Hizmetleri A.S.  |      28603 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1501 | Avea ?letisim Hizmetleri A.S.  |      28604 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+


(Cmd) delete from operator_timezones where mcc_mnc='28603'
DB1
Query OK, 1 row affected

DB2
Query OK, 1 row affected


(Cmd) commit
DB1 : committed
DB2 : committed

(Cmd) select * from operator_timezones where mcc_mnc like '286%'
DB1
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|   OPERATOR_ID | OPERATOR_DESCRIPTION           |    MCC_MNC |   WINTER_NGEO_TIMEZONE |   SUMMER_NGEO_TIMEZONE | SUMMER_DAYLIGHT_SAVING_DATE   | WINTER_DAYLIGHT_SAVING_DATE   |
+===============+================================+============+========================+========================+===============================+===============================+
|            26 | Turkcell                       | 2860128601 |                   8765 |                   8765 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1500 | Vodafone Telekomunikasyon A.S. |      28602 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1501 | Avea ?letisim Hizmetleri A.S.  |      28604 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+

DB2
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|   OPERATOR_ID | OPERATOR_DESCRIPTION           |    MCC_MNC |   WINTER_NGEO_TIMEZONE |   SUMMER_NGEO_TIMEZONE | SUMMER_DAYLIGHT_SAVING_DATE   | WINTER_DAYLIGHT_SAVING_DATE   |
+===============+================================+============+========================+========================+===============================+===============================+
|            26 | Turkcell                       | 2860128601 |                   8765 |                   8765 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1500 | Vodafone Telekomunikasyon A.S. |      28602 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1501 | Avea ?letisim Hizmetleri A.S.  |      28604 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+


(Cmd) insert into operator_timezones values ('1501', 'Avea Iletisim Hizmetleri A.S.', '28604', '8000', '8000', '1/1/2012', '1/1/2012')
DB1
Database exception ORA-00001: unique constraint (USER1.OPERATOR_TIMEZONES_PK) violated

DB2
Database exception ORA-00001: unique constraint (USER2.OPERATOR_TIMEZONES_PK) violated


(Cmd) insert into operator_timezones values ('1501', 'Avea Iletisim Hizmetleri A.S.', '28603', '8000', '8000', '1/1/2012', '1/1/2012')
DB1
Query OK, 1 row affected

DB2
Query OK, 1 row affected


(Cmd) select * from operator_timezones where mcc_mnc like '286%'
DB1
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|   OPERATOR_ID | OPERATOR_DESCRIPTION           |    MCC_MNC |   WINTER_NGEO_TIMEZONE |   SUMMER_NGEO_TIMEZONE | SUMMER_DAYLIGHT_SAVING_DATE   | WINTER_DAYLIGHT_SAVING_DATE   |
+===============+================================+============+========================+========================+===============================+===============================+
|            26 | Turkcell                       | 2860128601 |                   8765 |                   8765 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1500 | Vodafone Telekomunikasyon A.S. |      28602 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1501 | Avea Iletisim Hizmetleri A.S.  |      28603 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1501 | Avea ?letisim Hizmetleri A.S.  |      28604 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+

DB2
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|   OPERATOR_ID | OPERATOR_DESCRIPTION           |    MCC_MNC |   WINTER_NGEO_TIMEZONE |   SUMMER_NGEO_TIMEZONE | SUMMER_DAYLIGHT_SAVING_DATE   | WINTER_DAYLIGHT_SAVING_DATE   |
+===============+================================+============+========================+========================+===============================+===============================+
|            26 | Turkcell                       | 2860128601 |                   8765 |                   8765 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1500 | Vodafone Telekomunikasyon A.S. |      28602 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1501 | Avea Iletisim Hizmetleri A.S.  |      28603 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+
|          1501 | Avea ?letisim Hizmetleri A.S.  |      28604 |                   8000 |                   8000 | 1/1/2012                      | 1/1/2012                      |
+---------------+--------------------------------+------------+------------------------+------------------------+-------------------------------+-------------------------------+


(Cmd) disconnect
Still uncommitted transactions on DB1.
Do you want to commit? [y/n] y
DB1 : commmitted
Connection Closed: DB1
Still uncommitted transactions on DB2.
Do you want to commit? [y/n] y
DB2 : commmitted
Connection Closed: DB2

(Cmd) status
DB1         : NOT CONNECTED
DB2         : NOT CONNECTED

(Cmd) ?

Documented commands (type help <topic>):
========================================
EOF     connect  disconnect  list  rollback  status
commit  delete   insert      quit  select    update

Undocumented commands:
======================
help


(Cmd) ? connect

        You can connect to specific db with: connect [DB]
        If you want to connect all configured: connect all
        

(Cmd) quit
Bye...
$ ./multipledb.py oracle
Welcome to MultipleDB application.
Version: 0.3

(Cmd) quit
Bye...
$ ./multipledb.py sybase
Welcome to MultipleDB application.
Version: 0.3

(Cmd) quit
Bye...
$ ./multipledb.py mysql 
Welcome to MultipleDB application.
Version: 0.3

(Cmd) quit
Bye...
$ ./multipledb.py pgsql
*** DB Type must be ORACLE, SYBASE or MYSQL. Exiting...
```

