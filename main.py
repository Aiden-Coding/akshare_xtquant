from sanic import Sanic, empty
from middle.redis_config import redis_client
from utils import redis_util

app = Sanic("ak_share")

app.ctx.redis_client = redis_client


@app.main_process_start
async def main_process_start(app, loop):
    print("listener_1")


@app.main_process_stop
async def main_process_stop(app, loop):
    redis_client = app.ctx.redis_client
    if redis_client is not None:
        try:
            # 可能引发异常的代码块
            redis_client.close()
        except Exception as e:
            # 处理异常的代码块
            print("捕获到零除异常:", e)


@app.route("/", methods=["GET"])
async def index(request):
    redis_util.set_vale(request.app.redis_client, 'key', 'value')
    return empty(status=200)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, workers=4, access_log=True)
    # app.run(host="0.0.0.0", port=8888, single_process=True)
