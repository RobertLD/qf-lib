#     Copyright 2016-present CERN – European Organization for Nuclear Research
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
import unittest

from qf_lib.backtesting.contract.contract_to_ticker_conversion.bloomberg_mapper import \
    DummyBloombergContractTickerMapper
from qf_lib.backtesting.data_handler.daily_data_handler import DailyDataHandler
from qf_lib.common.enums.frequency import Frequency
from qf_lib.common.enums.price_field import PriceField
from qf_lib.common.tickers.tickers import BloombergTicker
from qf_lib.common.utils.dateutils.relative_delta import RelativeDelta
from qf_lib.common.utils.dateutils.string_to_date import str_to_date
from qf_lib.common.utils.dateutils.timer import SettableTimer
from qf_lib.containers.futures.future_ticker import BloombergFutureTicker
from qf_lib.data_providers.bloomberg import BloombergDataProvider
from qf_lib.data_providers.futures.futures_prefetching_data_provider import FuturesPrefetchingDataProvider
from qf_lib_tests.unit_tests.config.test_settings import get_test_settings

settings = get_test_settings()
bbg_provider = BloombergDataProvider(settings)
bbg_provider.connect()


@unittest.skipIf(not bbg_provider.connected, "No Bloomberg connection")
class TestFuturesPresetDataProvider(unittest.TestCase):
    timer = SettableTimer()
    frequency = Frequency.DAILY
    TICKER_1 = BloombergFutureTicker("Cotton", "CT{} Comdty", timer, bbg_provider, 1, 3)
    TICKER_2 = BloombergFutureTicker("Corn", 'C Z9 Comdty', timer, bbg_provider, 1, 5)
    contract_ticker_mapper = DummyBloombergContractTickerMapper()

    def setUp(self):
        self.end_date = str_to_date('2015-10-08')
        self.start_date = self.end_date - RelativeDelta(years=2)

        data_provider = FuturesPrefetchingDataProvider(bbg_provider,
                                                       self.TICKER_2,
                                                       PriceField.ohlcv(),
                                                       self.start_date, self.end_date,
                                                       self.frequency,
                                                       check_data_availability=True)

        self.timer.set_current_time(self.end_date)

        self.data_handler = DailyDataHandler(data_provider, self.timer)

    def test_data_provider_init(self):

        self.assertCountEqual(self.data_handler.data_provider.supported_ticker_types(),
                              {BloombergTicker})

    def test_get_futures_chain_1_ticker(self):
        # Check if the include_expired_contracts flag works in the same way for the Futures Preset Data Provider as for
        # the Bloomberg Data Provider
        bbg_fut_chain_tickers_non_expired = bbg_provider.get_futures_chain_tickers(self.TICKER_2,
                                                                                   self.end_date,
                                                                                   include_expired_contracts=False)
        preset_fut_chain_tickers_non_expired = self.data_handler.data_provider.get_futures_chain_tickers(
            self.TICKER_2,
            self.end_date,
            include_expired_contracts=False)

        self.assertCountEqual(bbg_fut_chain_tickers_non_expired[self.TICKER_2],
                              preset_fut_chain_tickers_non_expired[self.TICKER_2])

    def test_get_futures_chain_multiple_tickers(self):
        # Check if the include_expired_contracts flag works in the same way for the Futures Preset Data Provider as for
        # the Bloomberg Data Provider
        tickers = [self.TICKER_2]
        bbg_fut_chain_tickers_non_expired = bbg_provider.get_futures_chain_tickers(tickers,
                                                                                   self.end_date,
                                                                                   include_expired_contracts=False)
        preset_fut_chain_tickers_non_expired = self.data_handler.data_provider.get_futures_chain_tickers(
            tickers,
            self.end_date,
            include_expired_contracts=False)

        for ticker in tickers:
            self.assertCountEqual(bbg_fut_chain_tickers_non_expired[ticker],
                                  preset_fut_chain_tickers_non_expired[ticker])
