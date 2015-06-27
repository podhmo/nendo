# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
SELECT emp_id, fname, lname, start_date FROM employee
WHERE start_date
BETWEEN date('2001-01-01') AND date('2002-12-31');
"""

from nendo import Query, make_record, render, alias
from datetime import date

Employee = make_record("employee", "emp_id, fname, lname, start_date, end_date, superior_emp_id, dept_id, title, assigned_branch_id")
e = alias(Employee, "e")
query = (Query()
         .from_(e)
         .where((e.start_date.between(date(2001, 1, 1), date(2002, 12, 31)))))
print(render(query))
