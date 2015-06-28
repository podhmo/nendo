# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
-- The order by clause
SELECT account_id, product_cd, open_date, avail_balance
FROM account
ORDER BY avail_balance DESC;
"""

from nendo import Query, make_record, render

Account = make_record("account", "account_id product_cd open_date avail_balance")
query = Query().from_(Account).order_by(Account.avail_balance.desc())
print(render(query))
