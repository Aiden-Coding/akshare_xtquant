def set_vale(redis_client, key, value):
    redis_client.set(key, value)


def get_value(redis_client, key):
    return redis_client.get(key)


def delete_key(redis_client, key):
    redis_client.delete(key)
