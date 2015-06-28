# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
SELECT open_emp_id, COUNT(*) how_many
FROM account
GROUP BY open_emp_id
ORDER BY open_emp_id;
"""

from nendo import Query, make_record, render, alias
from nendo.value import fn, ALL

Account = make_record("account", "account_id product_cd open_date avail_balance open_emp_id")

query = (Query()
         .from_(Account)
         .group_by(Account.open_emp_id)
         .order_by(Account.open_emp_id)
         .select(Account.open_emp_id, alias(fn.count(ALL), "how_many")))
print(render(query))
