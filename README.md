# python_multiple_demand_database
> @Author: Wan Pei Chih  

設計一可應付各種存取資料庫需求的 資料庫模組

## 創見一 config.py
```python
class Config:
  dbinfo = {
    'db': 'dbName',
    'host': '127.0.0.1',
    'user': 'db_user',
    'password': 'db_pswd',
    'socket': '/var/lib/mysql/mysql.sock'
  }
  SQLALCHEMY_MYSQL_URI = "mysql+pymysql://{user}:{password}@{host}/{db}?unix_socket={socket}&charset=utf8mb4".format(**dbinfo)
```

## 使用實例
```python
from config import Config
from pyLibs import Database
with Database(Config.SQLALCHEMY_MYSQL_URI) as db:
  db._action('select')
  sqlstr = db.table('tblName').fields(['name','password','email']).where({'AND': {'name =': 'jacky'}})._outsql()
  db._specSqlStr(sqlstr)
  res = db.execute()
  for row in res:
    print (row)
```

詳細說明請參閱 Docs/ 文件說明
