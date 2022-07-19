import requests
import json
import logging

_BASE_URL = 'https://finance.yahoo.com/quote'
_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}
logger = logging.getLogger(__name__)


class TickerBase:

    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.ticker_url = f'{_BASE_URL}/{ticker}'
        self._stats = False
        self._financials = False
        self._short_info = None
        self._forward_dividends = None
        self._profile = None
        self._upgrade_downgrade = None

    def _get_stats(self):
        if self._stats:
            return
        url = self.ticker_url
        logger.info('Downloading: %s', url)
        response = requests.get(url, headers=_HEADERS)
        html = response.text
        if "QuoteSummaryStore" not in html:
            html = requests.get(url=url).text
            if "QuoteSummaryStore" not in html:
                return {}
        json_str = html.split('root.App.main =')[1].split('(this)')[0].split(';\n}')[0].strip()
        data = json.loads(json_str)['context']['dispatcher']['stores']['QuoteSummaryStore']

        short_info_items = ['sharesPercentSharesOut', 'shortPercentOfFloat', 'shortRatio']
        if 'defaultKeyStatistics' in data:
            self._short_info = {}
            for item in short_info_items:
                self._short_info[item] = data['defaultKeyStatistics'][item]

        forward_dividends_items = ['dividendRate', 'dividendYield']
        if 'summaryDetail' in data:
            self._forward_dividends = {}
            for item in forward_dividends_items:
                self._forward_dividends[item] = data['summaryDetail'][item]
        
        profile_items = ['sector', 'industry', 'fullTimeEmployees']
        if 'summaryProfile' in data:
            self._profile = {}
            for item in profile_items:
                self._profile[item] = data['summaryProfile'][item]
        
        self._stats = True

    def get_short_info(self):
        self._get_stats()
        return self._short_info

    def get_forward_dividends(self):
        self._get_stats()
        return self._forward_dividends

    def get_profile(self):
        self._get_stats()
        return self._profile


class Ticker(TickerBase):
    
    @property
    def short_info(self):
        return self.get_short_info()
    
    @property
    def forward_dividends(self):
        return self.get_forward_dividends()
    
    @property
    def profile(self):
        return self.get_profile()


if __name__ == '__main__':
    intc = Ticker('INTC')
    print(intc.short_info)


# # Short    
# data['defaultKeyStatistics']['sharesPercentSharesOut']
# data['defaultKeyStatistics']['shortPercentOfFloat']
# data['defaultKeyStatistics']['shortRatio']
# # Dividends
# data['summaryDetail']['dividendRate']
# data['summaryDetail']['dividendYield']
# # Profile
# data['summaryProfile']['sector']
# data['summaryProfile']['fullTimeEmployees']
# data['summaryProfile']['industry']
# # Recommendation
# data['recommendationTrend']['trend']
# # Upgrade - Dwongrade
# data['upgradeDowngradeHistory']['history'][:10]

# # /financials
# https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/INTC?&region=US&symbol=INTC&type=quarterlyBasicAverageShares,querterlyTotalDebt,quarterlyFreeCashFlow&period1=493590046&period2=1658050390
# # Income Statement
# data['incomeStatementsHistoryQuarterly']['incomeStatementHistory'][i]['totalRevenue']
# data['incomeStatementsHistoryQuarterly']['incomeStatementHistory'][i]['costOfRevenue']
# data['incomeStatementsHistoryQuarterly']['incomeStatementHistory'][i]['operatingIncome']
# data['incomeStatementsHistoryQuarterly']['incomeStatementHistory'][i]['totalOperatingExpenses']
# data['incomeStatementsHistoryQuarterly']['incomeStatementHistory'][i]['netIncome']
# data['incomeStatementsHistoryQuarterly']['incomeStatementHistory'][i]['ebit']
# # Balance sheet
# data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][i]['totalAssets']
# data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][i]['totalCurrentLiabilities']
# data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][i]['totalLiab']
# data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][i]['totalStockholderEquity']
# data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][i]['cash']
# data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][i]['inventory']
# data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][i]['totalCurrentAssets']
# # Free cashflow
# data['cashflowStatementHistoryQuarterly']['cashflowStatements'][i]['totalCashFromOperatingActivities']


# /analysis
# data['earningsHistory']['history']
# data['targetMedianPrice']
# data['targetMeanPrice']
# data['earningsTrend']['trend']

# /history
# url = "{}/v8/finance/chart/{}".format('https://query2.finance.yahoo.com', ticker)
# params = dict()
# params["interval"] = '1d'
# params["range"] = '1mo'
# params["events"] = "div,splits"
# r = requests.get(
#     url=url,
#     params=params,
#     headers=headers,
# )
# data = json.loads(r.text)
# timestamps = data["timestamp"]
# ohlc = data["indicators"]["quote"][0]
# volumes = ohlc["volume"]
# opens = ohlc["open"]
# closes = ohlc["close"]
# lows = ohlc["low"]
# highs = ohlc["high"]

# adjclose = closes
# if "adjclose" in data["indicators"]:
#     adjclose = data["indicators"]["adjclose"][0]["adjclose"]