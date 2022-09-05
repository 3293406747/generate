import random

from gen_data import GenData, inner_func, default


def job():
	job_list = ["开发经理", "开发工程师", "测试工程师", "产品经理", "运维工程师"]
	j = random.choice(job_list)
	return j


gen_data = GenData()
gen_data.generate_testdata(
	id=default,
	username=inner_func('name'),
	phone=inner_func('phone_number'),
	ssn=inner_func('ssn'),
	address=inner_func('address'),
	email=inner_func('email'),
	job=job,
	num=20
)
gen_data.insert_mysql(table='user', database='test_db', user='root', password='111111')
gen_data.insert_csv('test.csv', headers=True)
