# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
SELECT emp_id, assigned_branch_id
FROM employee
WHERE title = 'Teller'
UNION
SELECT open_emp_id, open_branch_id
FROM account
WHERE product_cd = 'SAV'
ORDER BY emp_id;
"""

from nendo import Query, make_record, render, alias

Employee = make_record("employee", "emp_id, fname, lname, start_date, end_date, superior_emp_id, dept_id, title, assigned_branch_id")
Account = make_record("account", "account_id product_cd open_date avail_balance open_emp_id open_branch_id")

q0 = (Query()
      .from_(Employee)
      .where(Employee.title == "Teller")
      .select(Employee.emp_id, alias(Employee.assigned_branch_id, "branch_id")))
q1 = (Query()
      .from_(Account)
      .where(Account.product_cd == "SAV")
      .select(alias(Account.open_emp_id, "emp_id"), alias(Account.open_branch_id, "branch_id")))
query = q0.union(q1)
print(render(query))
query = q0.union(q1).select(q0.emp_id, q0.branch_id).order_by(q0.emp_id)
print(render(query))
