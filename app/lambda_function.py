import os
import boto3
from datetime import datetime
from .ticker import Ticker
from .table import Stocks


dyn_resource = boto3.resource(
    'dynamodb', 
    # aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    # aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    # region_name='us-east-1'
)

def lambda_handler(event, context):
    today = datetime.today().strftime('%Y-%m-%d')
    ticker_name = 'INTC'
    ticker = Ticker(ticker_name)
    item = {
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
        'analysis': ticker.analysis
    }
    table = Stocks(dyn_resource)
    if table.exists():
        r = table.add_item(item)
    return {
        'statusCode': '200',
        'body': r
    }
