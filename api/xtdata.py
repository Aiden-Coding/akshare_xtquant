import datetime
import json

# import aiohttp
import pandas as pd
import requests
from sanic import Blueprint, response
from xtquant import xtdata, xtconstant

xtDataApi = Blueprint("xtDataApi", url_prefix="/data")


@xtDataApi.listener('before_server_start')
async def before_server_start(app, loop):
    '''全局共享session'''
    # url = 'http://localhost:8022/common/listStock'
    # response = requests.get(url)
    # data = json.loads(response.text)
    global session, subscribe_ids, trader, channel
    # jar = aiohttp.CookieJar(unsafe=True)
    # session = aiohttp.ClientSession(cookie_jar=jar, connector=aiohttp.TCPConnector(ssl=False))
    # subscribe_ids = []
    # codeList = []
    # market = {'深市A': 'SZ', '沪市A': 'SH', '北交': 'BJ'}
    # for x in data['data']:
    #     if x['market'] == '北交':
    #         continue
    #     if x['market'] == '其他A股':
    #         continue
    #     code = x['code'] + '.' + market[x['market']]
    #     codeList.append(code)
    # channel = rabbitmq_connection.channel()
    # channel.exchange_declare(exchange='交换机', exchange_type='fanout')
    # subscribe_ids.append(xtdata.subscribe_whole_quote(codeList, callback=on_data))


def on_data(datas):
    for stock_code in datas:
        # channel.basic_publish(exchange='交换机', routing_key='', body=json.loads(datas[stock_code]))
        print(stock_code, datas[stock_code])


@xtDataApi.listener('after_server_stop')
async def after_server_stop(app, loop):
    '''关闭session'''
    for seq_num in subscribe_ids:
        xtdata.unsubscribe_quote(seq_num)
    await session.close()


@xtDataApi.route('/subscribe', methods=['GET'])
async def subscribe(request, ticker_input=''):
    '''
    订阅单股行情: 获得tick/kline行情
    '''
    if ticker_input == '':
        ticker = request.args.get("ticker", "000001.SH")
    else:
        ticker = ticker_input
    period = request.args.get("period", "1m")
    start_time = request.args.get("start_time", "")
    end_time = request.args.get("end_time", "")
    subscribe_ids.append(xtdata.subscribe_quote(ticker, period, start_time=start_time, end_time=end_time, count=10))
    if ticker_input == '':
        return response.json({"data": subscribe_ids[-1]})
    else:
        return {"data": subscribe_ids[-1]}


@xtDataApi.route('/quote/kline', methods=['GET'])
async def quote_kline(request):
    '''
    查询市场行情: 获得kline数据
    '''
    tickers = request.args.get("tickers", "IM00.IF,159919.SZ,00700.HK,10004407.SHO")
    period = request.args.get("period", "1d")
    start_time = request.args.get("start_time", "20231207")
    end_time = request.args.get("end_time", "")
    count = request.args.get("count", "-1")
    dividend_type = request.args.get("dividend_type",
                                     "none")  # none 不复权 front 前复权 back 后复权 front_ratio 等比前复权 back_ratio 等比后复权
    stock_list = tickers.split(',')

    kline_data = xtdata.get_market_data(
        field_list=["time", "open", "high", "low", "close", "volume", "amount", "settelementPrice", "openInterest",
                    "preClose", "suspendFlag"],
        stock_list=stock_list, period=period, start_time=start_time, end_time=end_time,
        count=int(count), dividend_type=dividend_type, fill_data=True)

    quote_data = {}
    for stock in stock_list:
        df = pd.concat(
            [kline_data[i].loc[stock].T for i in
             ["time", "open", "high", "low", "close", "volume", "amount", "settelementPrice", "openInterest",
              "preClose", "suspendFlag"]], axis=1)
        df.columns = ["time", "open", "high", "low", "close", "volume", "amount", "settelementPrice", "openInterest",
                      "preClose", "suspendFlag"]
        # df = df[df.volume != 0]
        # df['time'] = df['time'].apply(
        #     lambda x: datetime.datetime.fromtimestamp(x / 1000.0).strftime("%Y-%m-%d %H:%M:%S"))
        df = df[["time", "open", "high", "low", "close", "volume", "amount", "settelementPrice", "openInterest",
                 "preClose", "suspendFlag"]].values.tolist()
        quote_data[stock] = df

    return response.json({"data": quote_data})


@xtDataApi.route('/quote/download', methods=['GET'])
async def download(request):
    tickers = request.args.get("tickers", "IM00.IF,159919.SZ,00700.HK,10004407.SHO")
    xtdata.download_history_data(tickers, '1d', start_time='20231207', end_time='')
    return response.json("ok")


@xtDataApi.route('/get_market_data_ex', methods=['GET'])
async def d(request):
    data = xtdata.get_market_data_ex(
        period='northfinancechange1d'
    )
    print(data)

