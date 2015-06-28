# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
-- Correlated Subqueries
SELECT c.cust_id, c.cust_type_cd, c.city
FROM customer c
WHERE 2 = (SELECT COUNT(*)
           FROM account a
           WHERE a.cust_id = c.cust_id);
"""

from nendo import Query, make_record, render, alias, subquery
from nendo.value import fn, ALL, Value

Account = make_record("account", "account_id product_cd open_date avail_balance cust_id")
Customer = make_record("customer", "cust_id cust_type_cd city")
a = alias(Account, "a")
c = alias(Customer, "c")
sub_q = (Query()
         .select(fn.count(ALL))
         .from_(a)
         .where(a.cust_id == c.cust_id.correlated()))
query = (Query()
         .from_(c)
         .where(Value(2) == subquery(sub_q, "sub_q"))
         .select(c.cust_id, c.cust_type_cd, c.city))
print(render(query))
