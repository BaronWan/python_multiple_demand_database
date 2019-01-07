# SQLAlchemy 資料庫公用物件  

> Updated of 07 Jan, 2019.



## 一. 架構說明  

### 1.1 共用屬性

#### - table 

> Table Name; (string)

#### - fields  

> [field1, field2, field3,...]; (list)

#### - where  

```python
{
    'AND': {
        'key1': 'val1',
        'key2 >': 'val2'
    },
    'OR': {
        'key3': 'val3',
        'key4': 'val4'
    },
}; (multi-layer dict)
等於 WHERE key1 LIKE '%val1%' AND key2 > 'val2' AND key3 LIKE '%val3%' OR key4 LIKE '%val4'
```



### 1.2 一般屬性  

#### - SELECT  

- 需求屬性：
  1. table
  2. fields

##### 3. join  

> Table Name; (string)

##### 4. _as  

> Alias Name; (string)

 	5. where

##### 6. on  

```python
{'kk': 'vv'} ; (dict)
```



##### 7. group | order  

> Field Name; (string)

##### 8. limit  

> numbers; (int)



#### - UPDATE  

1. table

##### 2. set  

```python
{'k1': 'v1', 
 'k2': 'v2'}; (dict)

等於 SET k1='v1', k2='v2'
```



3. where

#### - INSERT  

1. table

##### 2. values

```python
values = {
    'name': ['jacky','bob','john'],
    'password': ['jKy3509','bO305l','o0h35v7'],
    'email': ['jacky.wang@gmail.com','bob-su@qq.com','john.li@yahoo.com'],
} ; (dict + list)

# 等於 (name,password,email) VALUES 
# 	('jacky','jKy3509','jacky.wang@gmail.com'),
# 	('bob','bO305l','bob-su@qq.com'),
# 	('john','o0h35v7','john.li@yahoo.com')
```

#### - DELETE  

1. table
2. where



## 二. 運作方式

### 2.1	物件導向模式 (oop mode)

#### 第一步 設定要處理的動作類型

- (select | update | insert | delete)  

```python
db._action(actionName)
```



#### 第二步 開始進行資料整合應用  

```python
# example
db.table('tblName')
db.fields(['tb1.name','tb2.email','tb3.info'])
r1 = db._as('tb1')._outsql()
r2 = db.join('tblName2')._as('tb2').on({'tb1.sessionid': 'tb2.id'})._outsql()
r3 = db.join('tblName3')._as('tb3').on({'tb1.uid': 'tb3.uid'})._outsql()

```



#### 第三步 輸出為 SQL String

- db._outsql()

> 例如第二步中的 db._as(...)._outsql()



#### 第四步 匯入 SQL String

- db._specSqlStr( SQL_String )

```python
db._specSqlStr("%s%s%s" %(r1,r2,r3))
```



#### 第五步 執行  

- db.execute()

```python
result = db.execute()
for row in result:
    print(row)	# 每列列表 (name1,email1,info1),(name2,email2,info2),...
```



### 2.2	套版模式 (template mode)  

#### 第一步 設計 patten & require

```python
# example
require = {
    'table': 'permission',
    'fields': ['username','password','groups','ctime'],
    'where': {'AND':
              {'groups': 'admin'},
             },
    'order': 'username',
}
patten = 'SELECT {fields} FROM {table} WHERE {where} ORDER {order};'
```



#### 第二步 轉換為 SQL 字串輸出  

- db._convertosqlstr ( *patten*,  *require*)  



#### 第三步 匯入及執行  

- db._specSqlStr (*sql_string*).execute()

