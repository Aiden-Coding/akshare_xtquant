#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Desc: 同花顺-指数
https://q.10jqka.com.cn/zs/
"""
from datetime import datetime
from io import StringIO

import pandas as pd
import requests
from bs4 import BeautifulSoup
from py_mini_racer import py_mini_racer
from tqdm import tqdm

from akshare.datasets import get_ths_js
from akshare.utils import demjson


def _get_file_content_ths(file: str = "ths.js") -> str:
    """
    获取 JS 文件的内容
    :param file:  JS 文件名
    :type file: str
    :return: 文件内容
    :rtype: str
    """
    setting_file_path = get_ths_js(file)
    with open(setting_file_path) as f:
        file_data = f.read()
    return file_data


def stock_index_list_ths() -> pd.DataFrame:
    """
    同花顺-指数-列表
    https://q.10jqka.com.cn/zs/
    """
    js_code = py_mini_racer.MiniRacer()
    js_content = _get_file_content_ths("ths.js")
    js_code.eval(js_content)
    v_code = js_code.call("v")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/89.0.4389.90 Safari/537.36",
        "Cookie": f"v={v_code}",
    }
    url = f"https://q.10jqka.com.cn/zs/index/field/indexcode/order/asc/page/1/ajax/1/"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, features="lxml")
    try:
        page_num = int(
            soup.find_all(name="a", attrs={"class": "changePage"})[-1]["page"]
        )
    except IndexError:
        page_num = 1
    big_df = pd.DataFrame()
    for page in tqdm(range(1, page_num + 1), leave=False):
        v_code = js_code.call("v")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/89.0.4389.90 Safari/537.36",
            "Cookie": f"v={v_code}",
        }
        url = f"https://q.10jqka.com.cn/zs/index/field/indexcode/order/asc/page/{page}/ajax/1/"
        r = requests.get(url, headers=headers)
        temp_df = pd.read_html(StringIO(r.text))[0]
        big_df = pd.concat(objs=[big_df, temp_df], ignore_index=True)
        break
    if not big_df.empty:
        # 对指定列进行预处理，确保 0 不被去掉
        big_df['指数代码'] = big_df['指数代码'].astype(str).str.pad(width=6, side='left', fillchar='0')
    # 序号、指数代码、指数名称、最新价、 涨跌额、 涨跌幅（％）、 昨收、今开， 最高价、 最低价、 成交量（万手） 成交额（亿元）
    big_df.columns = [
        "number",
        "index_code",
        "index_name",
        "latest_price",
        "price_change",
        "price_change_percentage",
        "yesterday_close",
        "today_open",
        "highest_price",
        "lowest_price",
        "volume_in_million_hands",
        "turnover_in_billion_yuan",
    ]
    return big_df


if __name__ == "__main__":
    stock_index_list_ths()
