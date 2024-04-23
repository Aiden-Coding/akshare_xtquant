# -*- coding:utf-8 -*-
from sanic import Sanic, empty
from utils import redis_util

from api.akshare import akshare_api
from config import enable_redis
from config import enable_rabbitmq
from config import enable_xtquant

app = Sanic("ak_share")
if enable_redis:
    from middle.redis_config import redis_client
    app.ctx.redis_client = redis_client

if enable_rabbitmq:
    from middle.rabbitmq_config import rabbitmq_connection
    app.ctx.rabbitmq_connection = rabbitmq_connection

if enable_xtquant:
    from api.account import account_api
    app.blueprint(account_api)

app.blueprint(akshare_api)


@app.main_process_start
async def main_process_start(app, loop):
    print("listener_1")


@app.main_process_stop
async def main_process_stop(app, loop):
    redis_client = app.ctx.redis_client
    rabbitmq_connection = app.ctx.rabbitmq_connection
    if redis_client is not None:
        try:
            # 可能引发异常的代码块
            redis_client.close()
        except Exception as e:
            # 处理异常的代码块
            print("捕获到零除异常:", e)
    if rabbitmq_connection is not None:
        try:
            # 可能引发异常的代码块
            rabbitmq_connection.close()
        except Exception as e:
            # 处理异常的代码块
            print("捕获到零除异常:", e)


@app.route("/", methods=["GET"])
async def index(request):
    redis_util.set_vale(request.app.ctx.redis_client, 'key', 'value')
    return empty(status=200)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, workers=4, access_log=True)
    # app.run(host="0.0.0.0", port=8888, single_process=True)
