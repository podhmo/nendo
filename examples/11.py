# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
SELECT a.account_id, a.cust_id, a.open_date, a.product_cd
FROM account a INNER JOIN employee e ON a.open_emp_id = e.emp_id
INNER JOIN branch b ON e.assigned_branch_id = b.branch_id
WHERE e.start_date <= date('2004-01-01') AND
     (e.title = 'Teller' OR e.title = 'Head Teller') AND
     b.name = 'Woburn Branch';
"""

from nendo import Query, make_record, render, alias
from datetime import date

Account = make_record("account", "account_id, product_cd, open_date, avail_balance, open_emp_id, cust_id")
Employee = make_record("employee", "emp_id, fname, lname, start_date, end_date, superior_emp_id, dept_id, title, assigned_branch_id")
Branch = make_record("branch", "branch_id, name")

a = alias(Account, "a")
e = alias(Employee, "e")
b = alias(Branch, "b")
query = (Query()
         .from_(a.join(e, a.open_emp_id == e.emp_id).join(b, e.assigned_branch_id == b.branch_id))
         .where(e.start_date <= date(2004, 1, 1),
                ((e.title == 'teller') | (e.title == 'Head Teller')),
                b.name == "Woburn Branch")
         .select(a.account_id, a.cust_id, a.open_date, a.product_cd))
print(render(query))
