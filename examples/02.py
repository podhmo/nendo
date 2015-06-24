# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
SELECT open_emp_id, product_cd
FROM account
ORDER BY open_emp_id, product_cd;
"""

from nendo import Query, make_record, render
from nendo.value import List

Account = make_record("account", "account_id product_cd open_date avail_balance open_emp_id")
query = (Query()
         .from_(Account)
         .order_by(List([Account.open_emp_id, Account.product_cd]).desc())
         .select(Account.open_emp_id, Account.product_cd))
print(render(query))
