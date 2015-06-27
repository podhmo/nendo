# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
SELECT ALL e.emp_id AS f0,
           e.fname AS f1,
           e.lname AS f2,
           e.start_date AS f3
FROM employee AS e
WHERE ((e.start_date >= ?) AND (e.start_date <= ?))
"""

from nendo import Query, make_record, render, alias
from nendo.value import Prepared

Employee = make_record("employee", "emp_id, fname, lname, start_date, end_date, superior_emp_id, dept_id, title, assigned_branch_id")
e = alias(Employee, "e")
query = (Query()
         .from_(e)
         .where((e.start_date >= Prepared("start_date")) & (e.start_date <= Prepared("start_date"))))

print(render(query, start_date="2000-01-01"))
