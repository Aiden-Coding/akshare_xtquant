import redis

# 创建 Redis 连接池
pool = redis.ConnectionPool(host='localhost', port=8018, db=0, password='ningzaichun')

# 获取 Redis 客户端实例
redis_client = redis.Redis(connection_pool=pool)
redis_client.close()
# import redis
#
# # Redis 数据库连接信息
# HOST = 'localhost'
# PORT = 8018
# POOL_NAME = 'redis_pool'
# PASSWORD = 'ningzaichun'
#
# # 创建 Redis 连接池
# redis_pool = redis.ConnectionPool(host=HOST, port=PORT, db=0, password=PASSWORD, max_connections=10)
#
# # 获取 Redis 数据库连接
# redis_client = redis_pool.get_connection()
#
# # 关闭 Redis 数据库连接
# redis_client.close()
