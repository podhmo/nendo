examples/01.py

.. code-block:: python

  
  """
  SELECT account_id, product_cd, open_date, avail_balance
  FROM account
  ORDER BY avail_balance DESC;
  """
  
  from nendo import Query, make_record, render
  
  Account = make_record("account", "account_id product_cd open_date avail_balance")
  query = Query().from_(Account).order_by(Account.avail_balance.desc())
  print(render(query))

.. code-block:: sql

  ('SELECT account.account_id, account.product_cd, account.open_date, account.avail_balance FROM account ORDER BY account.avail_balance DESC', [])

examples/02.py

.. code-block:: python

  
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

.. code-block:: sql

  ('SELECT account.open_emp_id, account.product_cd FROM account ORDER BY account.open_emp_id, account.product_cd DESC', [])

examples/03.py

.. code-block:: python

  
  """
  SELECT *
  FROM employee
  WHERE end_date IS NULL AND (title = 'Teller' OR start_date < '2003-01-01');
  """
  
  from nendo import Query, make_record, render
  from nendo.value import NULL
  from datetime import date
  
  Employee = make_record("employee", "emp_id, fname, lname, start_date, end_date, superior_emp_id, dept_id, title, assigned_branch_id")
  query = (Query()
           .from_(Employee)
           .where((Employee.end_date.is_(NULL))
                  & (Employee.title == "Teller")
                  | (Employee.start_date < date(2003, 1, 1))))
  print(render(query))

.. code-block:: sql

  ("SELECT employee.emp_id, employee.fname, employee.lname, employee.start_date, employee.end_date, employee.superior_emp_id, employee.dept_id, employee.title, employee.assigned_branch_id FROM employee WHERE (((employee.end_date IS NULL) AND (employee.title = 'Teller')) OR (employee.start_date < '2003-01-01'))", [])

