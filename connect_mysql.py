import pymysql.cursors

# 连接数据库
connect = pymysql.Connect(
    host='localhost',
    port=3306,
    user='admin',
    passwd='abc.123',
    db='niewu',
    charset='utf8'
)

# 获取游标
cursor = connect.cursor()

# 建立数据表
sql_build = "CREATE TABLE MOT (id INT)"
table =

# 查询数据
sql_query = "SELECT * FROM ('%s')"
table = ('python')
cursor.execute(sql_query % table)
print('当前表:', cursor.fetchall())

# 插入数据
sql_insert = "INSERT INTO trade (name, account, saving) VALUES ( '%s', '%s', %.2f )"
data = ('雷军', '13512345678', 10000)
cursor.execute(sql_insert % data)
connect.commit()
print('成功插入', cursor.rowcount, '条数据')

# 修改数据
sql_modify = "INSERT INTO trade (name, account, saving) VALUES ( '%s', '%s', %.2f )"
data = ('雷军', '13512345678', 10000)
cursor.execute(sql_insert % data)
connect.commit()
print('成功插入', cursor.rowcount, '条数据')


# 关闭连接
cursor.close()
connect.close()