MultipleDB
==========

Shell to run SQL commands on more than one Oracle DB at the same time.

Following modules are required:
- cx_Oracle (http://cx-oracle.sourceforge.net):
pip install cx_Oracle

- tabulate (https://pypi.python.org/pypi/tabulate):
pip install tabulate

Readline module is optional, but it provides better interface like history, backspace/arrow keys, ..etc.


## USAGE EXAMPLE

```
$ ./multipledb.py
Welcome to MultipleDB application.
Version: 0.1

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
$ 
```

