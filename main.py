from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # 关键导入
from typing import Union
from pydantic import BaseModel
###调试用
import uvicorn
from tigeropen.common.consts import (Language,        # 语言
                                Market,           # 市场
                                BarPeriod,        # k线周期
                                QuoteRight)       # 复权类型
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.common.util.contract_utils import stock_contract, option_contract, option_contract_by_symbol, \
    future_contract, war_contract_by_symbol, iopt_contract_by_symbol
#以下为目前支持的几种订单类型对象
from tigeropen.common.util.order_utils import (market_order,        # 市价单
                                                    limit_order,         # 限价单
                                                    stop_order,          # 止损单
                                                    stop_limit_order,    # 限价止损单
                                                    trail_order,         # 移动止损单
                                                    order_leg)           # 附加订单
from tigeropen.trade.trade_client import TradeClient
from tigeropen.common.consts import Market, SecurityType, Currency
from tigeropen.common.util.contract_utils import stock_contract
from  tigeropen.trade.domain.order import Order



def get_client_config():
    """
    https://quant.itigerup.com/#developer 开发者信息获取
    """
    # 港股牌照需用 props_path 参数指定token路径，如 '/Users/xxx/xxx/', 如不指定则取当前路径
    # 必须使用关键字参数指定 props_path
    client_config = TigerOpenClientConfig()
    client_config.language = Language.zh_CN
    return client_config

# 调用上方定义的函数生成用户配置ClientConfig对象
client_config = get_client_config()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*","null"],  # 允许所有域名，生产环境建议改成具体域名如 ["http://你的前端域名"]
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法 (GET/POST等)
    allow_headers=["*"],  # 允许所有头
)

## 定义请求参数
# 依赖项函数
class Item(BaseModel):
    account: str
    ###"账户id"
    id: int
    ###"001"
    symbol: str
    ## "883"
    action: str
    ##"BUY"
    type: str
    ##"MKT"  
    contracts: float
    price: float
    sec_type: str
    ##"STK"
    adjust_limit: float
    # 0.005
    outside_rth: bool
    ##false      
    market: str
    ##"US/HK"
    currency:str
    ##"USD/HKD" 
    time_in_force:str
    ##"DAY"
    timestamp: str
    ##"2025-04-25T05:12:10Z"



@app.post("/order/")
def read_items(item: Item):
    print(item)
    qty = abs(int(item.contracts))
    code = item.symbol
    currency = item.currency
    market = item.market
    trd_side = item.action.lower()
    client_config = get_client_config()
    client_config.account = item.account

    order_id = int(item.id)
    sec_type = item.sec_type
    order_type = item.type
    limit_price = item.price
    outside_rth = item.outside_rth
    adjust_limit = item.adjust_limit
    time_in_force = item.time_in_force
    timestamp = item.timestamp

    trade_client = TradeClient(client_config)

    #下单需要先初始化一个contract对象，contract对象中保存着合约信息，详情请见合约对象。创建contract对象的方法请参考文档 基本操作-交易类-获取合约 部分，示例如下：
    #方法1: 直接本地构造contract对象。 期货 contract 的构造方法请参考文档 基本操作-交易类-获取合约 部分
    ####获取交易对像
    if currency == "USD" or market == "US":
        # 美股
        contract = stock_contract(symbol=code,currency='USD')
    elif currency == "HDK" or market == "HK":
        # 港股
        contract = stock_contract(symbol=code,currency='HKD')
    
    if trd_side == "buy" or trd_side == "买":
        trd_side = "BUY"
    elif trd_side == "sell" or trd_side == "卖":
        trd_side = "SELL"
    else:
        print("方向错误")
    # if order_type == "MKT" or order_type == "市价":
    #     order_type = "MKT"
    #     #创建订单对象，订单对象中保存了下单所需的账户、目标合约等信息，详情请见订单对象。这里以限价单为例
    #     # order = market_order(account=client_config.account,contract=contract,action=trd_side,quantity=qty)

    #     #提交订单。注意：提交订单前，order对象的id为None, 提交成功后， order对象的id会变为全局订单id
    #     oid = trade_client.place_order(account=client_config.account,contract=contract,action=trd_side,quantity=qty, order_id = order_id,sec_type=sec_type,time_in_force=time_in_force)
    #     print(oid)
    #     print(order)
    # elif order_type == "LMT" or order_type == "限价":
    #     order_type = "LMT"
    #创建订单对象，订单对象中保存了下单所需的账户、目标合约等信息，详情请见订单对象。这里以限价单为例
    order = Order(account=client_config.account,id = order_id,order_type=order_type,contract=contract,sec_type=sec_type,action=trd_side, quantity=qty,limit_price=limit_price,time_in_force=time_in_force,outside_rth=outside_rth,adjust_limit=adjust_limit)
    # order = Order(account=client_config.account,contract=contract,action=trd_side, quantity=qty,limit_price=limit_price)
    #提交订单。注意：提交订单前，order对象的id为None, 提交成功后， order对象的id会变为全局订单id
    oid = trade_client.place_order(order)
    print(oid)
    print(order)
    return item

# 调试用
if __name__ == "__main__":
    # uvicorn.run(app,host="0.0.0.0",port=80, reload=False)
    uvicorn.run(app,host="127.0.0.1",port=80, reload=False)