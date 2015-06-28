# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
-- join
SELECT e.fname, e.lname, d.name
FROM employee e INNER JOIN department d
USING (dept_id);
"""

from nendo import Query, make_record, render

Department = make_record("department", "dept_id, name")
Employee = make_record("employee", "emp_id, fname, lname, start_date, end_date, superior_emp_id, dept_id, title, assigned_branch_id")
query = (Query()
         .from_(Employee.join(Department, Employee.dept_id == Department.dept_id))
         .select(Employee.fname, Employee.lname, Department.name))
print(render(query))
