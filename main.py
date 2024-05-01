# -*- coding:utf-8 -*-
import json


from sanic import Sanic, empty
from utils import redis_util

from api.akshare import akshare_api
from config import enable_redis, enable_kafka
from config import enable_rabbitmq
from config import enable_xtquant

if enable_xtquant:
    from api.xtdata import xtDataApi
    from xtquant import xtdata

producer = None
if enable_kafka:
    from kafka3 import KafkaProducer
    producer = KafkaProducer(
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        bootstrap_servers=['localhost:9093'],
        max_request_size=10485760
    )
app = Sanic("ak_share")
if enable_redis:
    from middle.redis_config import redis_client

    app.ctx.redis_client = redis_client

if enable_rabbitmq:
    from middle.rabbitmq_config import rabbitmq_connection

    app.ctx.rabbitmq_connection = rabbitmq_connection

if enable_xtquant:
    from api.account import account_api

    app.blueprint(xtDataApi)
    app.blueprint(account_api)

app.blueprint(akshare_api)


def on_data(datas):
    if producer is not None:
        producer.send('stock_subscribe', datas)


@app.main_process_start
async def main_process_start(app, loop):
    if enable_xtquant:
        xtdata.enable_hello = False
        code_list = xtdata.get_stock_list_in_sector('沪深A股')
        subscribe_ids = [xtdata.subscribe_whole_quote(code_list, callback=on_data)]
        app.ctx.subscribe_ids = subscribe_ids


@app.main_process_stop
async def main_process_stop(app, loop):
    if hasattr(app.ctx, 'subscribe_ids'):
        if app.ctx.subscribe_ids:
            for i in app.ctx.subscribe_ids:
                xtdata.unsubscribe_quote(i)
    if hasattr(app.ctx, 'redis_client'):
        if redis_client is not None:
            try:
                # 可能引发异常的代码块
                redis_client.close()
            except Exception as e:
                # 处理异常的代码块
                print("捕获到零除异常:", e)
    if hasattr(app.ctx, 'rabbitmq_connection'):
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
