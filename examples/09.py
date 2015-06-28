# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
-- Membership conditions using subqueries
SELECT account_id, product_cd, cust_id, avail_balance
FROM account
WHERE product_cd IN (SELECT product_cd
                     FROM product
                     WHERE product_type_cd = 'ACCOUNT');
"""

from nendo import Query, make_record, render, subquery

Account = make_record("account", "account_id product_cd open_date avail_balance cust_id")
Product = make_record("product", "product_id product_cd product_type_cd")
subq = (Query()
        .from_(Product)
        .where(Product.product_type_cd == "ACCOUNT")
        .select(Product.product_cd))
query = (Query()
         .from_(Account)
         .where(Account.product_cd.in_(subquery(subq)))
         .select(Account.account_id, Account.product_cd, Account.cust_id, Account.avail_balance))
print(render(query))
