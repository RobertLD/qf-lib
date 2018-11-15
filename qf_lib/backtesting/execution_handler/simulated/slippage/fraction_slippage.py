import math
from typing import Sequence

from qf_lib.backtesting.execution_handler.simulated.slippage.base import Slippage
from qf_lib.backtesting.order.execution_style import MarketOrder, StopOrder
from qf_lib.backtesting.order.order import Order
from qf_lib.common.utils.logging.qf_parent_logger import qf_logger


class FractionSlippage(Slippage):
    """
    Calculates the slippage by using some fixed fraction of the current securities' price (e.g. always 0.01%).
    """

    def __init__(self, slippage_rate: float):
        self.slippage_rate = slippage_rate
        self._logger = qf_logger.getChild(self.__class__.__name__)

    def apply_slippage(self, orders: Sequence[Order], no_slippage_fill_prices: Sequence[float]) -> Sequence[float]:
        fill_prices = []

        for order, no_slippage_price in zip(orders, no_slippage_fill_prices):
            execution_style = order.execution_style
            if isinstance(execution_style, (MarketOrder, StopOrder)):
                fill_price = self._get_single_fill_price(order, no_slippage_price)
            else:
                self._logger.warning("Unsupported execution style: {}. No slippage was applied".format(execution_style))
                fill_price = no_slippage_price

            fill_prices.append(fill_price)

        return fill_prices

    def _get_single_fill_price(self, order, no_slippage_price):
        if math.isnan(no_slippage_price):
            fill_price = float('nan')
        else:
            if order.quantity > 0:  # BUY Order
                multiplier = 1 + self.slippage_rate
            else:  # SELL Order
                multiplier = 1 - self.slippage_rate

            fill_price = no_slippage_price * multiplier

        return fill_price
