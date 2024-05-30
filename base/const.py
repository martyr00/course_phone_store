from datetime import datetime

from base.utils import get_last_month

END_DATE_DEFAULT = datetime.now().strftime('%Y-%m-%d')
START_DATE_DEFAULT = get_last_month()
