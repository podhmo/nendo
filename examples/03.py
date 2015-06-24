# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

"""
SELECT *
FROM employee
WHERE end_date IS NULL AND (title = 'Teller' OR start_date < '2003-01-01');
"""

from nendo import Query, make_record, render
from nendo.value import NULL
from datetime import date

Employee = make_record("Employee", "emp_id, fname, lname, start_date, end_date, superior_emp_id, dept_id, title, assigned_branch_id")
query = (Query()
         .from_(Employee)
         .where((Employee.end_date.is_(NULL))
                & (Employee.title == "Teller")
                | (Employee.start_date < date(2003, 1, 1))))
print(render(query))
