import pika

# 指定远程 RabbitMQ 的用户名密码
username = 'rabbit'
pwd = '123456'

# 建立连接
cr = pika.PlainCredentials(username, pwd)
rabbitmq_connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1',8011,'/', cr))
# channel = connection.channel()
# channel.close()
# rabbitmq_connection.close()