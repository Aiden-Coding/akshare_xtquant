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
        soup = BeautifulSoup(r.text, features="lxml")
        url_list = []
        for item in (
                soup.find(name="table", attrs={"class": "m-table m-pager-table"})
                        .find("tbody")
                        .find_all("tr")
        ):
            inner_url = item.find_all("td")[1].find("a")["href"]
            if inner_url:
                inner_url = str(inner_url)
                split_string = inner_url.split("/")
                last_part = split_string[-1]
                if last_part == '':
                    last_part = split_string[-2]
                url_list.append(last_part)
            else:
                url_list.append(inner_url)
        temp_df = pd.read_html(StringIO(r.text))[0]
        temp_df["ths_code"] = url_list
        big_df = pd.concat(objs=[big_df, temp_df], ignore_index=True)
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
        "ths_code",
    ]
    return big_df


def stock_board_industry_index_ths(
        symbol: str = "1A0001",
        start_date: str = "20200101",
        end_date: str = "20240108",
) -> pd.DataFrame:
    """
    同花顺-板块-行业板块-指数数据
    https://q.10jqka.com.cn/gn/detail/code/301558/
    :param start_date: 开始时间
    :type start_date: str
    :param end_date: 结束时间
    :type end_date: str
    :param symbol: 指数数据
    :type symbol: str
    :return: 指数数据
    :rtype: pandas.DataFrame
    """
    big_df = pd.DataFrame()
    current_year = int(end_date[:4])
    begin_year = int(start_date[:4])
    add_today_data = False
    if end_date and is_date_greater(end_date):
        add_today_data = True
    for year in tqdm(range(begin_year, current_year + 1), leave=False):
        url = f"http://d.10jqka.com.cn/v4/line/zs_{symbol}/01/{year}.js"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
            "Referer": "http://q.10jqka.com.cn",
            "Host": "d.10jqka.com.cn",
        }
        r = requests.get(url, headers=headers)
        data_text = r.text
        try:
            demjson.decode(data_text[data_text.find("{"): -1])
        except:
            continue
        temp_df = demjson.decode(data_text[data_text.find("{"): -1])
        temp_df = pd.DataFrame(temp_df["data"].split(";"))
        temp_df = temp_df.iloc[:, 0].str.split(",", expand=True)
        big_df = pd.concat(objs=[big_df, temp_df], ignore_index=True)

    if len(big_df.columns) == 11:
        big_df.columns = [
            "日期",
            "开盘价",
            "最高价",
            "最低价",
            "收盘价",
            "成交量",
            "成交额",
            "_",
            "_",
            "_",
            "_",
        ]
    else:
        big_df.columns = [
            "日期",
            "开盘价",
            "最高价",
            "最低价",
            "收盘价",
            "成交量",
            "成交额",
            "_",
            "_",
            "_",
            "_",
            "_",
        ]
    big_df = big_df[
        [
            "日期",
            "开盘价",
            "最高价",
            "最低价",
            "收盘价",
            "成交量",
            "成交额",
        ]
    ]
    big_df["日期"] = pd.to_datetime(big_df["日期"], errors="coerce").dt.date
    big_df.index = pd.to_datetime(big_df["日期"], errors="coerce")
    big_df = big_df[start_date:end_date]
    big_df.reset_index(drop=True, inplace=True)
    big_df["开盘价"] = pd.to_numeric(big_df["开盘价"], errors="coerce")
    big_df["最高价"] = pd.to_numeric(big_df["最高价"], errors="coerce")
    big_df["最低价"] = pd.to_numeric(big_df["最低价"], errors="coerce")
    big_df["收盘价"] = pd.to_numeric(big_df["收盘价"], errors="coerce")
    big_df["成交量"] = pd.to_numeric(big_df["成交量"], errors="coerce")
    big_df["成交额"] = pd.to_numeric(big_df["成交额"], errors="coerce")
    big_df.columns = [
        "日期",
        "开盘",
        "最高",
        "最低",
        "收盘",
        "成交量",
        "成交额",
    ]
    if add_today_data:
        url = f"http://d.10jqka.com.cn/v4/line/zs_{symbol}/01/today.js"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
            "Referer": "http://q.10jqka.com.cn",
            "Host": "d.10jqka.com.cn",
        }
        r = requests.get(url, headers=headers)
        data_text = r.text
        try:
            temp_data = demjson.decode(data_text[data_text.find("{"): -1])
            if temp_data:
                for key in temp_data.keys():
                    value = temp_data[key]
                    if value:
                        new_row = {'日期': [datetime.strptime(value['1'], '%Y%m%d').date()], '开盘': [float(value['7'])],
                                   '最高': [float(value['8'])], '最低': [float(value['9'])], '收盘': [float(value['11'])],
                                   '成交量': [float(value['13'])], '成交额': [float(value['19'])]}
                        td = pd.DataFrame(new_row)
                        # 添加新行
                        big_df = pd.concat(objs=[big_df, td], ignore_index=True)

        except Exception as e:
            # 处理异常的代码
            print("发生异常:", e)

    return big_df


def is_date_greater(target_date):
    today = datetime.now().date()
    target = datetime.strptime(target_date, '%Y%m%d').date()
    return target > today


if __name__ == "__main__":
    stock_index_list_ths()
