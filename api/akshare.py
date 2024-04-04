# -*- coding:utf-8 -*-
from datetime import datetime
import json

from sanic import Blueprint, response
import akshare
import pandas as pdname

akshare_api = Blueprint("akshare_api", url_prefix="/ak")


@akshare_api.route("/method", methods=["POST"])
async def pyMethod(request):
    method_args = request.json
    if method_args['args'] is None or len(method_args['args']) < 1:
        data = akshare.call_function_no_args(method_args['method'])
        if isinstance(data, pdname.DataFrame):
            data = data.to_json(orient='records', force_ascii=False)
        return response.json({"code": 0, "data": json.loads(data)}, ensure_ascii=False)
    else:
        data = akshare.call_function(
            method_args['method'], method_args['args'])
        if isinstance(data, pdname.DataFrame):
            data = data.to_json(orient='records', force_ascii=False)
        return response.json({"code": 0, "data": json.loads(data)}, ensure_ascii=False)
