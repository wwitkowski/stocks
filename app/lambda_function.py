import os
import re
import time
import boto3
import logging
import requests
from datetime import datetime
from ticker import Ticker
from table import Stocks

if logging.getLogger().hasHandlers():
    logger = logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

dyn_resource = boto3.resource(
    'dynamodb', 
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

def lambda_handler(event, context):
    r = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies').text
    tickers = re.findall(r'<a rel="nofollow" class="external text" href=.+>([A-Z]{1,5})<.a>', r)
    today = datetime.today().strftime('%Y-%m-%d')
    items = []
    tickers_len = len(tickers)
    for i, ticker_name in enumerate(tickers):
        ticker = Ticker(ticker_name)
        logger.info('Downloading %s ticker data... [%d/%d]', ticker_name, i, tickers_len)
        items.append({
            'ticker': ticker_name,
            'date': today,
            'profile': ticker.profile,
            'short_info': ticker.short_info,
            'forward_dividends': ticker.forward_dividends,
            'recommendation_trend': ticker.recommendation_trend,
            'grades_history': ticker.grades_history,
            'income_statement': {
                'quarterly': ticker.quarterly_income_statement,
                'annual': ticker.annual_income_statement
            },
            'balance_sheet': {
                'quarterly': ticker.quarterly_balance_sheet,
                'annual': ticker.annual_balance_sheet
            },
            'cashflow': {
                'quarterly': ticker.quarterly_cashflow,
                'annual': ticker.annual_cashflow
            },
            'analysis': ticker.analysis,
            'price': ticker.history()
        })
        time.sleep(5)
    table = Stocks(dyn_resource)
    if table.exists():
        r = table.add_item(items)
    return {
        'statusCode': '200',
        'body': r
    }


lambda_handler(None, None)