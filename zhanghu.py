from tigeropen.trade.trade_client import TradeClient
from tigeropen.tiger_open_config import get_client_config
from tigeropen.tiger_open_config import TigerOpenClientConfig
import json

client_config = TigerOpenClientConfig()
trade_client = TradeClient(client_config)

accounts = trade_client.get_managed_accounts()
# 查看第一个账户的相关属性
zhanghu = {}
for i in range(len(accounts)):
    print(i)
    account1 = accounts[i]
    print(account1.account)  # 账户号
    print(account1.account_type)  # 账户分类(综合/模拟)
    print(account1.capability)  # 账户能力(现金/保证金)
    zhanghu[account1.account_type] = account1.account
print(zhanghu)
# 写入文件
with open("zhanghu.json", "w") as f:
    json.dump(zhanghu, f, indent=4)  # indent 参数美化输出

