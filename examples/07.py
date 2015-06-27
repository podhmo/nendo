# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
SELECT account_id, product_cd, cust_id, avail_balance
FROM account
WHERE product_cd IN ('CHK', 'SAV', 'CD', 'MM');
"""

from nendo import Query, make_record, render

Account = make_record("account", "account_id product_cd open_date avail_balance")
query = (Query()
         .from_(Account)
         .where(Account.product_cd.in_(["CHK", "SAV", "CD", "MM"])))
print(render(query))
