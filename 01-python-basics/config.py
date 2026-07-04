import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

OUTPUT_FILENAME = 'summary_report.csv'
ERROR_LOG_FILENAME = 'errors.log'

STATUS_COLUMN = 'status'
TARGET_STATUS = 'Delivered'
AMOUNT_COLUMN = 'total_amount'
ORDER_ID_COLUMN = 'order_id'

OUTPUT_COLUMNS = [
    'filename',
    'total_revenue',
    'average_order_value',
    'order_count'
]