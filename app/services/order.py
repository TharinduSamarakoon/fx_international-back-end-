from ibapi.contract import Contract
from ibapi.order import Order

from ..crud.users import update_balance
from ..ib.client import ib


async def create_order(symbol, currency, action, user, db):
    contract = Contract()
    contract.symbol = symbol.upper()
    contract.secType = "STK"
    contract.currency = currency.upper()
    contract.exchange = "SMART"

    order = Order()
    order.action = "SELL" if action == 1 else "BUY"
    order.orderType = "MKT"
    order.transmit = True
    order.totalQuantity = await get_quantity(user.balance)
    action = "+" if action == 1 else 0
    await update_balance(db, user.username, order.totalQuantity, action)
    nextID = 101
    ib.placeOrder(nextID, contract, order)


async def get_quantity(balance: float):
    if balance <= 100:
        return balance * 0.03
    else:
        return balance * 0.05
