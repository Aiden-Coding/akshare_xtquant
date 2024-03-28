import random

from sanic import Blueprint, response
from xtquant import xtconstant

from config import qmt_mini_path
from utils.covert_object import covert_object_list, covert_object, covert_object_success_result
from api.dto.trade_callback import MyXtQuantTraderCallback
from api.dto.trde import Trader

account_api = Blueprint("account_api", url_prefix="/account")

order_status = {
    xtconstant.ORDER_UNREPORTED: '未报',
    xtconstant.ORDER_WAIT_REPORTING: '待报',
    xtconstant.ORDER_REPORTED: '已报',
    xtconstant.ORDER_REPORTED_CANCEL: '已报待撤',
    xtconstant.ORDER_PARTSUCC_CANCEL: '部成待撤',
    xtconstant.ORDER_PART_CANCEL: '部撤',
    xtconstant.ORDER_CANCELED: '已撤',
    xtconstant.ORDER_PART_SUCC: '部成',
    xtconstant.ORDER_SUCCEEDED: '已成',
    xtconstant.ORDER_JUNK: '废单',
    xtconstant.ORDER_UNKNOWN: '未知'
}


@account_api.listener('before_server_start')
async def before_server_start(app, loop):
    global trader
    trader = Trader()
    session_id = random.randint(20000, 60000)
    trader.set_trader(qmt_mini_path, session_id)
    trader.set_account('18888681688', account_type='CREDIT')
    callback = MyXtQuantTraderCallback()
    # callback.set_rabbitmq_conntion(rabbitmq_connection)
    trader.account_register_callback(callback)


@account_api.listener('before_server_stop')
async def before_server_stop(app, loop):
    trader.un_subscribe_account()
    trader.stop()


@account_api.route('/assets', methods=['GET'])
async def assets(request):
    '''
    查询总资产
    '''
    asset = trader.query_stock_asset(trader.account)
    ret = covert_object(asset)
    return covert_object_success_result(ret)


@account_api.route('/assets_zh', methods=['GET'])
async def assets_zh(request):
    '''
    查询总资产
    '''
    asset = trader.query_stock_asset(trader.account)
    if asset is None:
        return response.json({
            "账号类型": trader.account.account_type,
            "资金账号": trader.account.account_id,
            "可用": 0.0,
            "冻结": 0.0,
            "持仓市值": 0.0,
            "总资产": 0.0,
        })
    return response.json({
        "账号类型": asset.account_type,
        "资金账号": asset.account_id,
        "可用": asset.cash,
        "冻结": asset.frozen_cash,
        "持仓市值": asset.market_value,
        "总资产": asset.total_asset,
    })


@account_api.route('/query_stock_orders', methods=['GET'])
async def query_stock_orders(request):
    '''
    查询当日所有委托
    '''
    ret = []
    xt_orders = trader.query_stock_orders()

    ret = covert_object_list(xt_orders)
    return covert_object_success_result(ret)


@account_api.route('/query_stock_orders_zh', methods=['GET'])
async def query_stock_orders_zh(request):
    '''
    查询当日所有委托
    '''
    ret = []
    xt_orders = trader.query_stock_orders()
    if xt_orders:
        for p in xt_orders:
            ret.append({
                "资金账号": p.account_id,
                "证券代码": p.stock_code,
                "委托编号": p.order_id,
                "柜台编号": p.order_sysid,
                "报单时间": p.order_time,
                "委托类型": p.order_type,  # 23: 买, 24: 卖
                "委托数量": p.order_volume,  # 股票以'股'为单位, 债券以'张'为单位
                "报价类型": p.price_type,
                "报价价格": p.price,
                "成交数量": p.traded_volume,  # 股票以'股'为单位, 债券以'张'为单位
                "成交均价": p.traded_price,
                "委托状态": p.order_status,
                "委托状态描述": p.status_msg,
                "策略名称": p.strategy_name,
                "委托备注": p.order_remark,
                "多空": p.direction,  # 多空, 股票不需要
                "交易操作": p.offset_flag  # 用此字段区分股票买卖，期货开、平仓，期权买卖等
            })

    return response.json(ret, ensure_ascii=False)


@account_api.route('/query_stock_trades', methods=['GET'])
async def query_stock_trades(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_stock_trades()
    ret = covert_object_list(xt_orders)
    return covert_object_success_result(ret)


@account_api.route('/query_stock_trades_zh', methods=['GET'])
async def query_stock_trades_zh(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_stock_trades()
    if xt_orders:
        for p in xt_orders:
            ret.append({
                "资金账号": p.account_id,
                "证券代码": p.stock_code,
                "委托类型": p.order_type,
                "成交编号": p.traded_id,
                "成交时间": p.traded_time,
                "成交均价": p.traded_price,
                "成交数量": p.traded_volume,
                "成交金额": p.traded_amount,
                "委托编号": p.order_id,
                "柜台编号": p.order_sysid,
                "策略名称": p.strategy_name,
                "委托备注": p.order_remark,
                "多空": p.direction,
                "交易操作": p.offset_flag,
            })

    return response.json(ret, ensure_ascii=False)


@account_api.route('/query_stock_positions', methods=['GET'])
async def query_stock_positions(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_stock_positions()
    ret = covert_object_list(xt_orders)
    return covert_object_success_result(ret)


@account_api.route('/query_stock_positions_zh', methods=['GET'])
async def query_stock_positions_zh(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_stock_positions()
    if xt_orders:
        for p in xt_orders:
            ret.append({
                "资金账号": p.account_id,
                "证券代码": p.stock_code,
                "持仓数量": p.volume,
                "可用数量": p.can_use_volume,
                "开仓价": p.open_price,
                "市值": p.market_value,
                "冻结数量": p.frozen_volume,
                "在途股份": p.on_road_volume,
                "昨夜拥股": p.yesterday_volume,
                "成本价": p.avg_price,
                "多空": p.direction,
            })

    return response.json(ret, ensure_ascii=False)


@account_api.route('/query_credit_detail_test', methods=['GET'])
async def query_credit_detail_test(request):
    '''
    查询当前持仓
    '''
    xt_orders = trader.query_credit_detail()
    ret = covert_object_list(xt_orders)
    return covert_object_success_result(ret)
    # ret = covert_object(asset)
    # return response.json(ret, ensure_ascii=False)


@account_api.route('/query_credit_detail', methods=['GET'])
async def query_credit_detail(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_credit_detail()
    ret = covert_object_list(xt_orders)
    return covert_object_success_result(ret)


@account_api.route('/query_credit_detail_zh', methods=['GET'])
async def query_credit_detail_zh(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_credit_detail()
    if xt_orders:
        for p in xt_orders:
            ret.append({
                "账号类型": p.account_type,
                "资金账号": p.account_id,
                "账号状态": p.m_nStatus,
                "更新时间": p.m_nUpdateTime,
                "计算参数": p.m_nCalcConfig,
                "冻结金额": p.m_dFrozenCash,
                "总资产": p.m_dBalance,
                "可用金额": p.m_dAvailable,
                "持仓盈亏": p.m_dPositionProfit,
                "总市值": p.m_dMarketValue,
                "可取金额": p.m_dFetchBalance,
                "股票市值": p.m_dStockValue,
                "基金市值": p.m_dFundValue,
                "总负债": p.m_dTotalDebt,
                "可用保证金": p.m_dEnableBailBalance,
                "维持担保比例": p.m_dPerAssurescaleValue,
                "净资产": p.m_dAssureAsset,
                "融资负债": p.m_dFinDebt,
                "融资本金": p.m_dFinDealAvl,
                "融资息费": p.m_dFinFee,
                "融券负债": p.m_dSloDebt,
                "融券市值": p.m_dSloMarketValue,
                "融券息费": p.m_dSloFee,
                "其它费用": p.m_dOtherFare,
                "融资授信额度": p.m_dFinMaxQuota,
                "融资可用额度": p.m_dFinEnableQuota,
                "融资冻结额度": p.m_dFinUsedQuota,
                "融券授信额度": p.m_dSloMaxQuota,
                "融券可用额度": p.m_dSloEnableQuota,
                "融券冻结额度": p.m_dSloUsedQuota,
                "融券卖出资金": p.m_dSloSellBalance,
                "已用融券卖出资金": p.m_dUsedSloSellBalance,
                "剩余融券卖出资金": p.m_dSurplusSloSellBalance,

            })

    return response.json(ret, ensure_ascii=False)


@account_api.route('/query_stk_compacts', methods=['GET'])
async def query_stk_compacts(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_stk_compacts()
    ret = covert_object_list(xt_orders)

    return covert_object_success_result(ret)


@account_api.route('/query_stk_compacts_zh', methods=['GET'])
async def query_stk_compacts_zh(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_stk_compacts()
    if xt_orders:
        for p in xt_orders:
            ret.append({
                "账号类型": p.account_type,
                "资金账号": p.account_id,
                "合约类型": p.compact_type,
                "头寸来源": p.cashgroup_prop,
                "证券市场": p.exchange_id,
                "开仓日期": p.open_date,
                "合约证券数量": p.business_vol,
                "未还合约数量": p.real_compact_vol,
                "到期日": p.ret_end_date,
                "合约金额": p.business_balance,
                "合约息费": p.businessFare,
                "未还合约金额": p.real_compact_balance,
                "未还合约息费": p.real_compact_fare,
                "已还息费": p.repaid_fare,
                "已还金额": p.repaid_balance,
                "证券代码": p.instrument_id,
                "合约编号": p.compact_id,
                "定位串": p.position_str,

            })

    return response.json(ret, ensure_ascii=False)


@account_api.route('/query_credit_subjects', methods=['GET'])
async def query_credit_subjects(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_credit_subjects()
    ret = covert_object_list(xt_orders)

    return covert_object_success_result(ret)


@account_api.route('/query_credit_subjects_zh', methods=['GET'])
async def query_credit_subjects_zh(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_credit_subjects()
    if xt_orders:
        for p in xt_orders:
            ret.append({
                "账号类型": p.account_type,
                "资金账号": p.account_id,
                "融券状态": p.slo_status,
                "融资状态": p.fin_status,
                "证券市场": p.exchange_id,
                "融券保证金比例": p.slo_ratio,
                "融资保证金比例": p.fin_ratio,
                "证券代码": p.instrument_id,

            })

    return response.json(ret, ensure_ascii=False)


@account_api.route('/query_credit_slo_code', methods=['GET'])
async def query_credit_slo_code(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_credit_slo_code()
    ret = covert_object_list(xt_orders)

    return covert_object_success_result(ret)


@account_api.route('/query_credit_slo_code_zh', methods=['GET'])
async def query_credit_slo_code_zh(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_credit_slo_code()
    if xt_orders:
        for p in xt_orders:
            ret.append({
                "账号类型": p.account_type,
                "资金账号": p.account_id,
                "头寸来源": p.cashgroup_prop,
                "证券市场": p.exchange_id,
                "融券可融数量": p.enable_amount,
                "证券代码": p.instrument_id,

            })

    return response.json(ret, ensure_ascii=False)


@account_api.route('/query_credit_assure', methods=['GET'])
async def query_credit_assure(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_credit_assure()
    ret = covert_object_list(xt_orders)

    return covert_object_success_result(ret)


@account_api.route('/query_credit_assure_zh', methods=['GET'])
async def query_credit_assure_zh(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_credit_assure()
    if xt_orders:
        for p in xt_orders:
            ret.append({
                "账号类型": p.account_type,
                "资金账号": p.account_id,
                "是否可做担保": p.assure_status,
                "证券市场": p.exchange_id,
                "担保品折算比例": p.assure_ratio,
                "证券代码": p.instrument_id,

            })

    return response.json(ret, ensure_ascii=False)


@account_api.route('/query_new_purchase_limit', methods=['GET'])
async def query_new_purchase_limit(request):
    '''
    查询当前持仓
    '''
    ret = {}
    xt_orders = trader.query_new_purchase_limit()
    if xt_orders:
        return response.json(xt_orders, ensure_ascii=False)

    return covert_object_success_result(ret)


@account_api.route('/query_new_purchase_limit_zh', methods=['GET'])
async def query_new_purchase_limit_zh(request):
    '''
    查询当前持仓
    '''
    # channel = rabbitmq_connection.channel()
    # # 声明durable=True可以保证RabbitMQ服务挂掉之后队列中的消息也不丢失，原理是因为
    # # RabbitMQ会将queue中的消息保存到磁盘中
    # channel.queue_declare(queue='task_queue')
    #
    # message = 'Hello World! 555'
    # channel.basic_publish(
    #     exchange='',
    #     routing_key='task_queue',
    #     body=message,
    #     # delivery_mode=2可以指定此条消息持久化，防止RabbitMQ服务挂掉之后消息丢失
    #     # 但是此属性设置并不能百分百保证消息真的被持久化，因为RabbitMQ挂掉的时候
    #     # 它可能还保存在缓存中，没来得及同步到磁盘中
    #     # properties=pika.BasicProperties(delivery_mode=2)
    # )

    ret = []
    xt_orders = trader.query_new_purchase_limit()
    if xt_orders:
        for key, value in xt_orders.items():
            # type - str 品种类型 KCB - 科创板，SH - 上海，SZ - 深圳

            ret.append({
                "品种类型": key,
                "数量": value,

            })

    return response.json(ret, ensure_ascii=False)


@account_api.route('/query_ipo_data', methods=['GET'])
async def query_ipo_data(request):
    '''
    查询当前持仓
    '''
    ret = {}
    xt_orders = trader.query_ipo_data()
    if xt_orders:
        return response.json(xt_orders, ensure_ascii=False)

    return covert_object_success_result(ret)


@account_api.route('/query_ipo_data_zh', methods=['GET'])
async def query_ipo_data_zh(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_ipo_data()
    if xt_orders:
        for key, value in xt_orders.items():
            # type - str 品种类型 KCB - 科创板，SH - 上海，SZ - 深圳
            ret.append({
                "品种代码": key,
                "品种名称": value.name,
                "品种类型": value.type,
                # "品种名称": value.name,
                "申购日期": value.purchaseDate,
                "发行价": value.issuePrice,

            })

    return response.json(ret, ensure_ascii=False)


@account_api.route('/query_account_infos', methods=['GET'])
async def query_account_infos(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_account_infos()
    if xt_orders:
        ret = covert_object_list(xt_orders)
        return response.json(ret, ensure_ascii=False)

    return covert_object_success_result(ret)


@account_api.route('/query_account_infos_zh', methods=['GET'])
async def query_account_infos_zh(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_account_infos()
    if xt_orders:
        for p in xt_orders:
            ret.append({
                "账号类型": p.account_type,
                "资金账号": p.account_id,
                "平台号": p.platform_id,
                # "账号分类": p.account_classification,
                "账号状态": p.login_status,

            })

    return response.json(ret, ensure_ascii=False)


@account_api.route('/query_com_fund', methods=['GET'])
async def query_com_fund(request):
    '''
    查询当前持仓
    '''
    ret = {}
    xt_orders = trader.query_com_fund()
    if xt_orders:
        if xt_orders.success:
            return response.json(xt_orders, ensure_ascii=False)

    return covert_object_success_result(ret)


@account_api.route('/query_com_fund_zh', methods=['GET'])
async def query_com_fund_zh(request):
    '''
    查询当前持仓
    '''
    ret = {}
    xt_orders = trader.query_com_fund()
    if xt_orders:
        if xt_orders.success:
            ret = {
                "当前余额": xt_orders.currentBalance,
                "可用余额": xt_orders.enableBalance,
                "可取金额": xt_orders.fetchBalance,
                "待入账利息": xt_orders.interest,
                "总资产": xt_orders.assetBalance,
                "可取现金": xt_orders.fetchCash,
                "市值": xt_orders.marketValue,
                "负债": xt_orders.debt,
            }

    return response.json(ret, ensure_ascii=False)


@account_api.route('/query_com_position', methods=['GET'])
async def query_com_position(request):
    '''
    查询当前持仓
    '''
    ret = []
    xt_orders = trader.query_com_position()
    if xt_orders:
        ret = covert_object_list(xt_orders)
        return response.json(ret, ensure_ascii=False)

    return covert_object_success_result(ret)


@account_api.route('/query_com_position_zh', methods=['GET'])
async def query_com_position_zh(request):
    '''
    查询当前持仓
    '''
    ret = {}
    xt_orders = trader.query_com_position()
    if xt_orders:
        for p in xt_orders:
            ret.append({
                "账号类型": p.account_type,
                "资金账号": p.account_id,
                "平台号": p.platform_id,
                "账号分类": p.account_classification,
                "账号状态": p.login_status,

            })
    return response.json(ret, ensure_ascii=False)


@account_api.route('/place_order', methods=['GET'])
async def trade_place_order(request):
    '''
    下单
    '''
    stock_code = request.args.get('stock_code', '510300.SH')
    direction = xtconstant.STOCK_BUY if request.args.get('direction', 'buy') == 'buy' else xtconstant.STOCK_SELL
    volumn = int(request.args.get('volumn', '100'))
    price = float(request.args.get('price', '4.4'))
    order_id = trader.xt_trader.order_stock(trader.account, stock_code, direction, volumn, xtconstant.FIX_PRICE, price,
                                            'strategy_name', 'remark')
    return response.json({'order_id': order_id}, ensure_ascii=False)


@account_api.route('/cancel_order', methods=['GET'])
async def trade_cancel_order(request):
    '''
    撤单
    '''
    order_id = int(request.args.get('order_id', '0'))
    cancel_order_result = trader.xt_trader.cancel_order_stock(trader.account, order_id)
    return response.json({'cancel_order_result': cancel_order_result}, ensure_ascii=False)
