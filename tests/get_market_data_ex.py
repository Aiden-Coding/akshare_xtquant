from xtquant import xtdata

data_dir = f"D:\gjzq\gjzqqmt_ceshi\datadir"


def get_market_data(
        field_list=[], stock_list=[], period='1d'
        , start_time='', end_time='', count=-1
        , dividend_type='none', fill_data=True
):
    '''
    获取历史行情数据
    :param field_list: 行情数据字段列表，[]为全部字段
        K线可选字段：
            "time"                #时间戳
            "open"                #开盘价
            "high"                #最高价
            "low"                 #最低价
            "close"               #收盘价
            "volume"              #成交量
            "amount"              #成交额
            "settle"              #今结算
            "openInterest"        #持仓量
        分笔可选字段：
            "time"                #时间戳
            "lastPrice"           #最新价
            "open"                #开盘价
            "high"                #最高价
            "low"                 #最低价
            "lastClose"           #前收盘价
            "amount"              #成交总额
            "volume"              #成交总量
            "pvolume"             #原始成交总量
            "stockStatus"         #证券状态
            "openInt"             #持仓量
            "lastSettlementPrice" #前结算
            "askPrice1", "askPrice2", "askPrice3", "askPrice4", "askPrice5" #卖一价~卖五价
            "bidPrice1", "bidPrice2", "bidPrice3", "bidPrice4", "bidPrice5" #买一价~买五价
            "askVol1", "askVol2", "askVol3", "askVol4", "askVol5"           #卖一量~卖五量
            "bidVol1", "bidVol2", "bidVol3", "bidVol4", "bidVol5"           #买一量~买五量
    :param stock_list: 股票代码 "000001.SZ"
    :param period: 周期 分笔"tick" 分钟线"1m"/"5m"/"15m" 日线"1d"
        Level2行情快照"l2quote" Level2行情快照补充"l2quoteaux" Level2逐笔委托"l2order" Level2逐笔成交"l2transaction" Level2大单统计"l2transactioncount" Level2委买委卖队列"l2orderqueue"
        Level1逐笔成交统计一分钟“transactioncount1m” Level1逐笔成交统计日线“transactioncount1d”
        期货仓单“warehousereceipt” 期货席位“futureholderrank” 互动问答“interactiveqa”
    :param start_time: 起始时间 "20200101" "20200101093000"
    :param end_time: 结束时间 "20201231" "20201231150000"
    :param count: 数量 -1全部/n: 从结束时间向前数n个
    :param dividend_type: 除权类型"none" "front" "back" "front_ratio" "back_ratio"
    :param fill_data: 对齐时间戳时是否填充数据，仅对K线有效，分笔周期不对齐时间戳
        为True时，以缺失数据的前一条数据填充
            open、high、low、close 为前一条数据的close
            amount、volume为0
            settle、openInterest 和前一条数据相同
        为False时，缺失数据所有字段填NaN
    :return: 数据集，分笔数据和K线数据格式不同
        period为'tick'时：{stock1 : value1, stock2 : value2, ...}
            stock1, stock2, ... : 合约代码
            value1, value2, ... : np.ndarray 数据列表，按time增序排列
        period为其他K线周期时：{field1 : value1, field2 : value2, ...}
            field1, field2, ... : 数据字段
            value1, value2, ... : pd.DataFrame 字段对应的数据，各字段维度相同，index为stock_list，columns为time_list
    '''
    if period in {'1m', '5m', '15m', '30m', '60m', '1h', '1d', '1w', '1mon', '1q', '1hy', '1y'}:
        import pandas as pd
        index, data = xtdata.get_market_data_ori(field_list, stock_list, period, start_time, end_time, count,
                                                 dividend_type, fill_data, data_dir=data_dir)

        result = {}
        for field in data:
            result[field] = pd.DataFrame(data[field], index=index[0], columns=index[1])
        return result

    return xtdata.get_market_data_ori(field_list, stock_list, period, start_time, end_time, count, dividend_type,
                                      fill_data, data_dir=data_dir)


def get_market_data_ex(
        field_list=[], stock_list=[], period='1d'
        , start_time='', end_time='', count=-1
        , dividend_type='none', fill_data=True
):
    if period == 'hkbrokerqueue' or period == 'hkbrokerqueue2' or period == (1820, 0):
        showbrokename = period == 'hkbrokerqueue2'
        return xtdata.get_broker_queue_data(stock_list, start_time, end_time, count, showbrokename)

    period = xtdata._get_tuple_period(period) or period
    if isinstance(period, tuple):
        return xtdata._get_market_data_ex_tuple_period(field_list, stock_list, period, start_time, end_time, count,
                                                       dividend_type, fill_data)

    if period in {'1m', '5m', '15m', '30m', '60m', '1h', '1d', '1w', '1mon', '1q', '1hy', '1y'}:
        return xtdata._get_market_data_ex_ori_221207(field_list, stock_list, period, start_time, end_time, count,
                                                     dividend_type, fill_data, data_dir=data_dir)

    import pandas as pd
    result = {}

    ifield = 'time'
    query_field_list = field_list if (not field_list) or (ifield in field_list) else [ifield] + field_list
    ori_data = xtdata.get_market_data_ex_ori(query_field_list, stock_list, period, start_time, end_time, count,
                                             dividend_type,
                                             fill_data, data_dir=data_dir)

    if not ori_data:
        return result

    fl = field_list
    stime_fmt = '%Y%m%d' if period == '1d' else '%Y%m%d%H%M%S'
    if fl:
        fl2 = fl if ifield in fl else [ifield] + fl
        for s in ori_data:
            sdata = pd.DataFrame(ori_data[s], columns=fl2)
            sdata2 = sdata[fl]
            sdata2.index = [xtdata.timetag_to_datetime(t, stime_fmt) for t in sdata[ifield]]
            result[s] = sdata2
    else:
        needconvert, metaid = xtdata._needconvert_period(period)
        if needconvert:
            convert_field_list = xtdata.get_field_list(metaid)

            for s in ori_data:
                odata = ori_data[s]
                if convert_field_list:
                    convert_data_list = []
                    for data in odata:
                        convert_data = xtdata._convert_component_info(data, convert_field_list)
                        convert_data_list.append(convert_data)
                    odata = convert_data_list

                sdata = pd.DataFrame(odata)
                sdata.index = [xtdata.timetag_to_datetime(t, stime_fmt) for t in sdata[ifield]]
                result[s] = sdata
        else:
            for s in ori_data:
                sdata = pd.DataFrame(ori_data[s])
                sdata.index = [xtdata.timetag_to_datetime(t, stime_fmt) for t in sdata[ifield]]
                result[s] = sdata

    return result


data = get_market_data([], ["000001.SZ"], period="1d", start_time="", end_time="", count=10)
# print(data)

res = xtdata.get_market_data_ori(stock_list=['600519.SH'], period='1d')
# print(res)
# 获取指定合约历史行情
day_data = get_market_data_ex(field_list=[], stock_list=['000001.SH'], period='1m', start_time='',
                              end_time='20231026', count=5, dividend_type='none', fill_data=True)
print(day_data)

res = xtdata.get_sector_list()
# print(res)
res = xtdata.get_stock_list_in_sector('沪深指数')
# print(res)
res = xtdata.get_stock_list_in_sector('上证A股')
# print(res)
res = xtdata.get_stock_list_in_sector('深证A股')
# print(res)
res = xtdata.get_stock_list_in_sector('京市A股')
# print(res)
res = xtdata.get_stock_list_in_sector('沪深A股')
# print(res)

import json

from kafka3 import KafkaProducer
from xtquant import xtdata

producer = KafkaProducer(
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    bootstrap_servers=['localhost:9093'],
    max_request_size=10485760
)


def on_data(datas):
    # print(datas)
    if producer is not None:
        producer.send('test', datas)


def main_process_start():
    xtdata.enable_hello = False
    code_list = xtdata.get_stock_list_in_sector('沪深A股')
    subscribe_ids = [xtdata.subscribe_whole_quote(code_list, callback=on_data)]


if __name__ == '__main__':
    main_process_start()
    xtdata.run()
