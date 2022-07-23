from audioop import add
import requests
import json
import logging
from datetime import datetime

_BASE_URL = 'https://finance.yahoo.com/quote'
_ADDITIONAL_ITEMS_URL = 'https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/INTC?'\
                        'region=US&symbol=INTC&type={items}&period1=493590046&period2={today_timestamp}'
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
        self._financials = False
        self._short_info = None
        self._forward_dividends = None
        self._profile = None
        self._recommendation_trend = None
        self._grades_history = None
        self._income_statement = None
        self._balance_sheet = None
        self._cashflow = None
        self._analysis = None

    @staticmethod
    def _get_json(url):
        r = requests.get(url, headers=_HEADERS)
        response = r.text
        if "QuoteSummaryStore" not in response:
            response = requests.get(url=url).text
            if "QuoteSummaryStore" not in response:
                return {}
        json_str = response.split('root.App.main =')[1].split('(this)')[0].split(';\n}')[0].strip()
        data = json.loads(json_str)['context']['dispatcher']['stores']['QuoteSummaryStore']
        return data

    def _get_stats(self):
        if self._stats:
            return
        data = self._get_json(self.ticker_url)
        
        def get_items(key, items):
            items_dict = {item: data[key].get(item) for item in items}
            return items_dict

        self._short_info = get_items(
            'defaultKeyStatistics', 
            ['sharesPercentSharesOut', 'shortPercentOfFloat', 'shortRatio']
        )
        self._forward_dividends = get_items(
            'summaryDetail',
            ['dividendRate', 'dividendYield']
        )
        self._profile = get_items(
            'summaryProfile',
            ['sector', 'industry', 'fullTimeEmployees']
        )
        self._recommendation_trend = get_items('recommendationTrend', ['trend'])

        history = get_items('upgradeDowngradeHistory', ['history'])
        if isinstance(history, list):
            self._grades_history = history[:10]

        self._stats = True

    def _get_financials(self):
        if self._financials:
            return
        data = self._get_json(self.ticker_url + '/financials')
        additional_items = [
            'quarterlyBasicAverageShares','quarterlyTotalDebt','annualBasicAverageShares','annualTotalDebt',
        ]
        url = _ADDITIONAL_ITEMS_URL.format(
            today_timestamp=int(datetime.today().timestamp()),
            items=','.join(additional_items))
        additional_items = json.loads(requests.get(url, headers=_HEADERS).text)
        for item in range(len(additional_items['timeseries']['result'])):
            item_name = additional_items['timeseries']['result'][item]['meta']['type'][0]
            n_periods = len(additional_items['timeseries']['result'][item][item_name])
            for period in range(n_periods):
                if 'quarterly' in item_name:
                    data['balanceSheetHistoryQuarterly']['balanceSheetStatements'][period].update({
                        item_name.replace('quarterly', ''): 
                        additional_items['timeseries']['result'][item][item_name][n_periods-item-1]['reportedValue']
                    })
                else:
                    data['balanceSheetHistory']['balanceSheetStatements'][period].update({
                        item_name.replace('annual', ''): 
                        additional_items['timeseries']['result'][item][item_name][n_periods-item-1]['reportedValue']
                    })

        def get_items(key, items):
            items_dict = {}
            if key in data:
                second_lvl_key = list(data[key].keys())[0]
                items_dict['annual'] = [
                    {item: data[key][second_lvl_key][timestamp].get(item) for item in items} 
                    for timestamp in range(len(data[key][second_lvl_key]))
                ]
            key += 'Quarterly'
            if key in data:
                second_lvl_key = list(data[key].keys())[0]
                items_dict['quarterly'] = [
                    {item: data[key][second_lvl_key][timestamp].get(item) for item in items} 
                    for timestamp in range(len(data[key][second_lvl_key]))
                ]
            return items_dict

        self._income_statement = get_items(
            'incomeStatementHistory',
            items=[
                'totalRevenue', 
                'costOfRevenue', 
                'operatingIncome', 
                'totalOperatingExpenses', 
                'netIncome', 
                'ebit',
                'endDate'
            ]
        )

        self._balance_sheet = get_items(
            'balanceSheetHistory',
            items=[
                'totalAssets',
                'totalCurrentLiabilities',
                'totalLiab',
                'totalStockholderEquity',
                'cash',
                'inventory',
                'totalCurrentAssets',
                'totalDebt',
                'basicAverageShares',
                'endDate'
            ]
        )

        self._cashflow = get_items(
            'cashflowStatementHistory',
            items=[
                'totalCashFromOperatingActivities', 
                'capitalExpenditures', 
                'endDate']
        )

        self._financials = True

    def _get_analysis(self):
        if self._analysis:
            return
        print('download')
        data = self._get_json(self.ticker_url + '/analysis')
        
        def get_items(key, items):
            items_dict = {item: data[key].get(item) for item in items}
            return items_dict

        self._analysis = {
            'earningsHistory': get_items('earningsHistory', items=['history']),
            'earningsTrend': get_items('earningsTrend', items=['trend']),
            **get_items('financialData', items=['targetMedianPrice', 'targetMeanPrice'])
        }


    def get_short_info(self):
        self._get_stats()
        return self._short_info

    def get_forward_dividends(self):
        self._get_stats()
        return self._forward_dividends

    def get_profile(self):
        self._get_stats()
        return self._profile

    def get_recommendation_trend(self):
        self._get_stats()
        return self._recommendation_trend

    def get_grades_history(self):
        self._get_stats()
        return self._profile
    
    def get_income_statement(self, freq='quarterly'):
        self._get_financials()
        return self._income_statement[freq]

    def get_balance_sheet(self, freq='quarterly'):
        self._get_financials()
        return self._balance_sheet[freq]
    
    def get_cashflow(self, freq='quarterly'):
        self._get_financials()
        return self._cashflow[freq]
    
    def get_analysis(self):
        self._get_analysis()
        return self._analysis

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
    
    @property
    def recommendation_trend(self):
        return self.get_recommendation_trend()

    @property
    def grades_history(self):
        return self.get_grades_history()

    @property
    def quarterly_income_statement(self):
        return self.get_income_statement()
    
    @property
    def annual_income_statement(self):
        return self.get_income_statement(freq='annual')

    @property
    def quarterly_balance_sheet(self):
        return self.get_balance_sheet()

    @property
    def annual_balance_sheet(self):
        return self.get_balance_sheet(freq='annual')

    @property
    def quarterly_cashflow(self):
        return self.get_cashflow()

    @property
    def annual_cashflow(self):
        return self.get_cashflow(freq='annual')

    @property
    def analysis(self):
        return self.get_analysis()

if __name__ == '__main__':
    intc = Ticker('INTC')
    print(intc.analysis)
    print()

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