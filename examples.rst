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

result:

.. code-block:: sql

  ('SELECT account_id, product_cd, open_date, avail_balance FROM account ORDER BY avail_balance DESC', [])

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

result:

.. code-block:: sql

  ('SELECT open_emp_id, product_cd FROM account ORDER BY open_emp_id, product_cd DESC', [])

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

result:

.. code-block:: sql

  ("SELECT emp_id, fname, lname, start_date, end_date, superior_emp_id, dept_id, title, assigned_branch_id FROM employee WHERE (((end_date IS NULL) AND (title = 'Teller')) OR (start_date < '2003-01-01'))", [])

examples/04.py

.. code-block:: python

  
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

result:

.. code-block:: sql

  ("SELECT emp_id, fname, lname, start_date, end_date, superior_emp_id, dept_id, title, assigned_branch_id FROM employee as e WHERE (start_date BETWEEN '2001-01-01' AND '2002-12-31')", [])

examples/05.py

.. code-block:: python

  
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

result:

.. code-block:: sql

  ("SELECT emp_id, fname, lname, start_date, end_date, superior_emp_id, dept_id, title, assigned_branch_id FROM employee as e WHERE (start_date BETWEEN '2001-01-01' AND '2002-12-31')", [])

examples/06.py

.. code-block:: python

  
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

result:

.. code-block:: sql

  ('SELECT emp_id, fname, lname, start_date, end_date, superior_emp_id, dept_id, title, assigned_branch_id FROM employee as e WHERE ((start_date >= %s) AND (start_date <= %s))', ['2000-01-01', '2000-01-01'])

examples/07.py

.. code-block:: python

  
  """
  SELECT account_id, product_cd, cust_id, avail_balance
  FROM account
  WHERE product_cd IN ('CHK', 'SAV', 'CD', 'MM');
  """
  
  from nendo import Query, make_record, render
  
  Account = make_record("account", "account_id product_cd open_date avail_balance")
  query = (Query()
           .from_(Account)
           .where(Account.product_cd.in_(["CHK", "SAV", "CD", "MM"])))
  print(render(query))

result:

.. code-block:: sql

  ("SELECT account_id, product_cd, open_date, avail_balance FROM account WHERE (product_cd IN ('CHK', 'SAV', 'CD', 'MM'))", [])

examples/08.py

.. code-block:: python

  
  """
  SELECT account_id, product_cd, cust_id, avail_balance
  FROM account
  WHERE account_id = (SELECT MAX(account_id)
                      FROM account);
  """
  
  from nendo import Query, make_record, render, subquery
  from nendo.value import fn
  
  Account = make_record("account", "account_id product_cd open_date avail_balance")
  subq = (Query().from_(Account).select(fn.count(Account.account_id)))
  query = (Query()
           .from_(Account)
           .where(Account.account_id == subquery(subq)))
  print(render(query))

result:

.. code-block:: sql

  ('SELECT account_id, product_cd, open_date, avail_balance FROM account WHERE (account_id = (SELECT count(account_id) FROM account))', [])

examples/09.py

.. code-block:: python

  
  """
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

result:

.. code-block:: sql

  ("SELECT account_id, product_cd, cust_id, avail_balance FROM account WHERE (product_cd IN (SELECT product_cd as product_product_cd FROM product WHERE (product_type_cd = 'ACCOUNT')))", [])

examples/10.py

.. code-block:: python

  
  """
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

result:

.. code-block:: sql

  ('SELECT employee.fname, employee.lname, department.name FROM employee JOIN department ON (employee.dept_id = department.dept_id)', [])

examples/11.py

.. code-block:: python

  
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

result:

.. code-block:: sql

  ("SELECT a.account_id, a.cust_id, a.open_date, a.product_cd FROM account as a JOIN employee as e ON (a.open_emp_id = e.emp_id) JOIN branch as b ON (e.assigned_branch_id = b.branch_id) WHERE (((e.start_date <= '2004-01-01') AND ((e.title = 'teller') OR (e.title = 'Head Teller'))) AND (b.name = 'Woburn Branch'))", [])

examples/12.py

.. code-block:: python

  
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

result:

.. code-block:: sql

  ('SELECT e.fname, e.lname, e_mgr.fname as mgr_fname, e_mgr.lname as mgr_lname FROM employee as e JOIN employee as e_mgr WHERE (e.superior_emp_id = e_mgr.emp_id)', [])

