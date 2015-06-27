# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
SELECT e.fname, e.lname, e_mgr.fname mgr_fname, e_mgr.lname mgr_lname
FROM employee e INNER JOIN employee e_mgr
ON e.superior_emp_id = e_mgr.emp_id
"""

from nendo import Query, make_record, render, alias
from datetime import date

Employee = make_record("employee", "emp_id, fname, lname, start_date, end_date, superior_emp_id, dept_id, title, assigned_branch_id")
e = alias(Employee, "e")
e_mgr = alias(Employee, "e_mgr")

query = (Query()
         .from_(e.join(e_mgr))
         .where(e.superior_emp_id == e_mgr.emp_id)
         .select(e.fname, e.lname, alias(e_mgr.fname, "mgr_fname"), alias(e_mgr.lname, "mgr_lname")))
print(render(query))
