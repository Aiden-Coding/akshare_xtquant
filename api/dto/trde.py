from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class Trader(Singleton):
    xt_trader = None
    account = None
    account_subscribe_result = None

    def set_trader(self, qmt_dir, session_id):
        self.xt_trader = XtQuantTrader(qmt_dir, session_id)
        # 启动交易线程
        self.xt_trader.start()
        # 建立交易连接，返回0表示连接成功
        connect_result = self.xt_trader.connect()
        return connect_result

    def set_account(self, account_id, account_type):
        self.account = StockAccount(account_id, account_type=account_type)
        self.account_subscribe_result = self.xt_trader.subscribe(self.account)
        return self.account

    @property
    def get_account(self):
        return self.account

    @property
    def get_trader(self):
        return self.xt_trader

    def account_register_callback(self, callback):
        self.xt_trader.register_callback(callback)

    def un_subscribe_account(self):
        self.xt_trader.unsubscribe(self.account)

    def stop(self):
        self.xt_trader.stop()

    def query_stock_asset(self, account):
        return self.xt_trader.query_stock_asset(account)

    # http://dict.thinktrader.net/nativeApi/xttrader.html#%E8%B5%84%E4%BA%A7%E6%9F%A5%E8%AF%A2
    # 该账号对应的当日所有委托对象R组成的list或者None
    def query_stock_orders(self, cancelable_only=False):
        return self.xt_trader.query_stock_orders(self.account, cancelable_only=cancelable_only)

    def query_stock_trades(self):
        return self.xt_trader.query_stock_trades(self.account)

    def query_stock_positions(self):
        return self.xt_trader.query_stock_positions(self.account)

    def query_credit_detail(self):
        return self.xt_trader.query_credit_detail(self.account)

    def query_stk_compacts(self):
        return self.xt_trader.query_stk_compacts(self.account)

    def query_credit_subjects(self):
        return self.xt_trader.query_credit_subjects(self.account)

    def query_credit_slo_code(self):
        return self.xt_trader.query_credit_slo_code(self.account)

    def query_credit_assure(self):
        return self.xt_trader.query_credit_assure(self.account)

    def query_new_purchase_limit(self):
        return self.xt_trader.query_new_purchase_limit(self.account)

    def query_ipo_data(self):
        return self.xt_trader.query_ipo_data()

    def query_account_infos(self):
        return self.xt_trader.query_account_infos()

    def query_com_fund(self):
        return self.xt_trader.query_com_fund(self.account)

    def query_com_position(self):
        return self.xt_trader.query_com_position(self.account)
