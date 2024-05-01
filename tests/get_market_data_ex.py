from xtquant import xtdata

res = xtdata.get_sector_list()
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
    with open('new_file.txt', 'w') as f:
        f.write(str(json.dumps(datas).encode('utf-8')))
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
