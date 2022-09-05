import sys

import pymysql
from faker import Faker
import pandas as pd
from loguru import logger

# 控制台日志
logger.remove()
logger.add(
	sink=sys.stderr,
	level="DEBUG",
	format="<green>{time:YYYY-MM-DD HH:mm:ss}</green>[<level>{level}</level>]<level>{message}</level>",
	backtrace=True,
	diagnose=False
)


class GenData:
	"""
	这是一个批量生成测试数据并导入数据库或CSV文件的脚本，
	可扩展：有内置的方法用于生成测试数据，也可以自己编写方法用于生成测试数据。
	插入数据库的方式包括`insert into table_name values(datas)`,
	`insert into table_name(lines) values(datas)`两种方式。

	脚本设计：采用生成测试数据后再插入数据库的设计方式，避免了每次打开连接占用连接池。
	采用了递归、回调函数、动态导包等设计。
	"""

	def __init__(self):
		self.testdata = []

	def generate_testdata(self, *args, num=1, **kwargs) -> list:
		"""
		生成测试数据，*args与**kwargs只能选其中一种方式传参。
		:param args:
		:param num: 需要生成的测试数据数量
		:param kwargs:
		:return: 生成的测试数据列表
		"""
		if num <= 0:
			logger.info("测试数据已全部生成")
			return self.testdata
		else:
			logger.info(f"还剩{num}条测试数据未生成")
			if args:
				seq = []
				for i in args:
					seq.append(i())
				self.testdata.append(tuple(seq))
			elif kwargs:
				seq = {}
				for k, v in kwargs.items():
					seq[k] = v()
				self.testdata.append(seq)
			return self.generate_testdata(*args, num=num - 1, **kwargs)

	def insert_mysql(self, table, database, password, user='root', host='localhost', port=3306) -> None:
		"""
		生成的测试数据插入mysql数据库
		:param table: 数据库表名
		:param database: 数据库名
		:param password: 数据库密码
		:param host: 数据库地址
		:param port: 数据库端口
		:param user: 数据库账号
		:return:
		"""
		try:
			conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
			cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
		except Exception as why:
			raise Exception(f"MYSQL连接失败，失败原因:{why}")
		try:
			if isinstance(self.testdata[0], tuple):
				seq = []
				for i in self.testdata:
					s = str(i).replace(
						"'default'", "default").replace(
						"'not null'", "not null").replace(
						"'null'", "null")
					if s[-2] == ",":
						s = s[:-2] + s[-1]
					seq.append(s)
				sql = f"insert into {table} values%s" % ",".join(seq)
			else:
				seq = []
				for i in self.testdata:
					s = str(tuple(i.values())).replace(
						"'default'", "default").replace(
						"'not null'", "not null").replace(
						"'null'", "null")
					if s[-2] == ",":
						s = s[:-2] + s[-1]
					seq.append(s)
				sql = f"insert into {table}({','.join(self.testdata[0].keys())}) values%s" % ",".join(seq)
			logger.info(f"sql语句:{sql}")
			cursor.execute(sql)
			conn.commit()
			logger.info("数据insert到MYSQL成功。")
		except Exception as why:
			conn.rollback()
			raise Exception(f"数据insert到MYSQL失败，insert失败原因:{why}") from None

	def insert_csv(self, file, mode="a", index=False, headers=False) -> None:
		"""
		生成的测试数据插入csv文件
		:param file: 文件路径
		:param mode: 写入模式，可选"a"或"w"。"a"为追加写入，"w"为覆盖写入
		:param index: 是否写入索引
		:param headers: 是否写入列名
		:return:
		"""
		try:
			p = pd.DataFrame(self.testdata)
			p.to_csv(file, mode=mode, index=index, header=headers)
			logger.info("数据insert到CSV文件成功。")
		except Exception as why:
			raise Exception(f"数据insert到CSV文件失败，insert失败原因:{why}")


def inner_func(target, locale='zh-CN'):
	"""
	获取内置数据
	:param target: 要获取的内置数据
	:param locale: 语言
	:return: 获取内置数据的方法，供generate_testdata方法回调
	"""
	try:
		faker = Faker(locale=locale)

		def get_target():
			if hasattr(faker, target):
				func = getattr(faker, target)
				return func()

		return get_target
	except Exception as why:
		raise Exception(f"获取内置数据失败，失败原因:{why}")


def default():
	""" mysql中的默认值 """
	return 'default'


def null():
	""" mysql中的空值 """
	return 'null'


def not_null():
	""" mysql中的非空值 """
	return 'not null'


if __name__ == '__main__':
	gdata = GenData()
	gdata.generate_testdata(id=default, name=inner_func('name'), num=5)
	gdata.insert_mysql('user', 'faker', '111111')
	gdata.insert_csv('test1.csv')
