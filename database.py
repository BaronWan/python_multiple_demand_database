# -*- coding: utf-8 -*-
__Author__ = 'Wan, Pei-Zhi (Baron. Wan) <boytools@outlook.com>'
__Updated__ = '07 Jan, 2019'

from datetime import datetime
from sqlalchemy import create_engine
import re

class Database(object):
	def __init__(self, db_uri):
		self.DB_URI = db_uri
		self.NT = None
		self.NDT = None
		self.engine = None
		self.conn = None
		
		self.action = None
		self.require = {}
		self.patten = ""
		
		self.patten_module = {
			'db': '{db}',
			'table': '{table}',
			'select': 'SELECT',
			'update': 'UPDATE',
			'insert': 'INSERT INTO',
			'delete': 'DELETE FROM',
			'fields': '{fields} FROM',
			'where': 'WHERE {where}',
			'join': 'JOIN {join}',
			'on': 'ON {on}',
			'as': 'AS {as}',
			'set': 'SET {set}',
			'values': 'VALUES {values}',
			'group': 'GROUP {group}',
			'order': 'ORDER {order}',
			'limit': 'LIMIT {limit}',
		}
		self._sqlStr = ""
	
	def __enter__(self):
		self.NDT = datetime.strftime(datetime.now(), '%d/%m/%Y %H:%M:%S')
		self.NT = datetime.strftime(datetime.now(), '%s')
		self.engine = create_engine(self.DB_URI)
		self.conn = self.engine.connect()
		return self
	
	def __exit__(self, exc_type, exc_value, exc_trace):
		self.conn.close()
		
	def _convertosqlstr(self, patten, data):
		if not isinstance(data, dict):
			return False
		
		for k,v in data.items():
			r1 = re.sub('/[\d+]$/','',k)
			
			if r1 == 'on':
				data[k] = ' AND '.join([ "%s = %s" %(k1,v1) for k1,v1 in v.items() ])
			
			elif r1 == 'as':
				data[k] = v
			
			elif r1 == 'set':
				data[k] = ', '.join([ "%s = %s" %(k1,v1) if isinstance(v1,int) else "%s = '%s'" %(k1,v1) for k1,v1 in v.items() ])
			
			elif r1 == 'fields':
				data[k] = ','.join(v)
				
			elif r1 == 'where':
				dd = ''
				for k1,v1 in v.items():
					dd += '('
					for k2,v2 in v1.items():
						if isinstance(v2, dict):
							for k3,v3 in v2.items():
								cc = k3.split(' ')
								if len(cc) >= 2:
									# ex: k3v1 >= k3v2 AND
									dd += "%s %s %s" %(k3,v3,k1)
								elif len(cc) == 1:
									dd += "%s LIKE '%%%s%%' %s " %(k3,v3,k1)
						else:
							cc = k2.split(' ')
							if len(cc) >= 2:
								dd += "%s %s %s" %(k2,v2,k1)
							elif len(cc) == 1:
								dd += "%s LIKE '%%%s%%' %s " %(k2,v2,k1)
							
					dd = re.sub(' '+k1+' $', '', dd) +') AND '
				dd = re.sub(' '+k1+' $', '', dd)
				data[k] = dd
				
			elif r1 == 'values':
				dd = ''
				dd += '(%s) VALUES ' %( ','.join(v.keys()) )
				dd += '(' + '),('.join( [",".join([ v[k][n] if isinstance(v[k][n],int) else "'%s'" %v[k][n] for k in v.keys() ]) for n in range(len([vc for vc in v.values()][0])) ] ) + ')'
				data[k] = dd	
			
			elif r1 == 'join':
				data[k] = v
			
			elif (r1 == 'group') or (r1 == 'order'):
				data[k] = 'BY %s' % v
			
			elif r1 == 'limit':
				data[k] = int(v)
			
			self.require = {}
			self.patten = ''
		return patten.format(**data)


	def dbname(self,name):
		self.require['db'] = name
		return self

	def table(self,name):
		self.require['table'] = name
		return self
		
	def fields(self,data):
		self.require['fields'] = data
		return self
		
	def where(self,data):
		self.require['where'] = data
		return self
	
	def group(self,data):
		self.require['group'] = data
		return self
		
	def order(self,data):
		self.require['order'] = data
		return self
	
	def limit(self,num):
		self.require['limit'] = num
		return self
	
	def join(self,data):
		self.require['join'] = data
		return self
	
	def _as(self,data):
		self.require['as'] = data
		return self
		
	def on(self,data):
		self.require['on'] = data
		return self
		
	def set(self,data):
		self.require['set'] = data
		return self
		
	def values(self,data):
		self.require['values'] = data
		return self
	
	def _action(self,name):
		setattr(self, 'action', name)
		# print (self.action)
		return self
	
	def _outsql(self):
		listSort = {
			'select': ['fields','table','join','as','where','on','group','order','limit'],
			'update': ['table','set','where'],
			'insert': ['table','values'],
			'delete': ['table','where']
		}	
		
		# Initial (select|update|insert|delete)
		if self._sqlStr == '':
			self.patten = self.patten_module[self.action] + ' '
		
		for keyName in listSort[self.action]:
			if keyName in self.require.keys():
				# print ('%s : %s' %(self.patten, self.patten_module[keyName]) )
				self.patten += self.patten_module[keyName] + ' '
				
		self._sqlStr = self._convertosqlstr(self.patten, self.require)
		return self._sqlStr

	def _clrAbout(self):
		self.require = {}
		self.patten = ""
		return self

	# 指定 SQL 字串
	# ex: db._specSqlStr(sql_string).select()
	def _specSqlStr(self, sqlstr):
		self._sqlStr = sqlstr
		return self

	def execute(self):
		def chkout():
			trans = self.conn.begin()
			try:
				executed = self.conn.execute(self._sqlStr)
			except Exception as e:
				print (e)
				return False
			
			if self.action == 'select':
				return executed.fetchall()
			else:
				try:
					trans.commit()
					return True
				except Exception as e:
					# print (e)
					trans.rollback()
					return False
		
		# print (self.require); print (self.patten); print (self._sqlStr)
		if self._sqlStr != "":
			# print(1)
			return chkout()
			
		elif self.require == {}:
			# print(2)
			if self._sqlStr == "":
				return False
			else:	# require is None but _sqlStr have sql command string
				return chkout()
			
		elif self.patten != None:	# require and patten are have files
			# print(3)	
			if self._sqlStr == "":
				self._outsql()
				
			return chkout()
				
		else: 	# only require have files but patten is None !
			# print(4)
			return False
	
		
	
