# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
-- subquery
SELECT account_id, product_cd, cust_id, avail_balance
FROM account
WHERE account_id = (SELECT MAX(account_id)
                    FROM account);
"""

from nendo import Query, make_record, render, subquery
from nendo.value import fn

Account = make_record("account", "account_id product_cd open_date avail_balance")
subq = (Query().from_(Account).select(fn.count(Account.account_id)))
query = (Query()
         .from_(Account)
         .where(Account.account_id == subquery(subq)))
print(render(query))
