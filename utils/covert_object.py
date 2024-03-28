from sanic import response


def covert_object(object_install=None):
    ret = {}
    if object_install:
        attrs = dir(object_install)
        for attr in attrs:
            if attr.startswith('__'):
                continue
            ret[attr] = getattr(object_install, attr)
    return ret


def covert_object_list(object_install=None):
    ret = []
    if object_install:
        for obj in object_install:
            ret_temp = {}
            attrs = dir(obj)
            for attr in attrs:
                if attr.startswith('__'):
                    continue
                ret_temp[attr] = getattr(obj, attr)
            ret.append(ret_temp)
    return ret


def covert_object_success_result(object_install=None):
    return response.json({"code": 0, "message": "ok", "data": object_install}, ensure_ascii=False)
