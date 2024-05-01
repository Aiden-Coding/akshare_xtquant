# import aiohttp
import pandas as pd
from sanic import Blueprint, response
from xtquant import xtdata

xtdata.enable_hello = False

xtDataApi = Blueprint("xtDataApi", url_prefix="/data")


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
