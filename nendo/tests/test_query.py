# -*- coding:utf-8 -*-
import unittest
from evilunit import test_function


@test_function("nendo.compiler:compiler")
class Tests(unittest.TestCase):
    maxDiff = None

    def _makeRecord(self, *args, **kwargs):
        from nendo import make_record
        return make_record(*args, **kwargs)

    def _makeQuery(self):
        from nendo.query import Query
        return Query()

    def test_select__constant(self):
        target = (self._makeQuery().select(1))
        result = self._callFUT(target, {})
        expected = 'SELECT 1'
        self.assertEqual(result, expected)

    def test_select__constant__expr(self):
        from nendo.value import Value
        target = (self._makeQuery().select(Value(0) == Value(0)))
        result = self._callFUT(target, {})
        expected = 'SELECT (0 = 0)'
        self.assertEqual(result, expected)

    def test_join(self):
        T1 = self._makeRecord("T1", "id")
        T2 = self._makeRecord("T2", "id t1_id")
        T3 = self._makeRecord("T3", "id t2_id")
        T4 = self._makeRecord("T4", "id t3_id")
        target = (self._makeQuery().from_(T1
                                          .left_outer_join(T2, T2.t1_id == T1.id)
                                          .cross_join(T3, T3.t2_id == T2.id)
                                          .right_outer_join(T4, T4.t3_id == T3.id))
                  .select(T1.id))
        result = self._callFUT(target, {})
        expected = 'SELECT T1.id FROM T1 LEFT OUTER JOIN T2 ON (T2.t1_id = T1.id) CROSS JOIN T3 ON (T3.t2_id = T2.id) RIGHT OUTER JOIN T4 ON (T4.t3_id = T3.id)'
        self.assertEqual(result, expected)

    def test_prefix(self):
        T = self._makeRecord("T", "id pt")
        target = self._makeQuery().from_(T).where(~(T.pt == 3))
        result = self._callFUT(target, {})
        expected = "SELECT T.id, T.pt FROM T WHERE (NOT (T.pt = 3))"
        self.assertEqual(result, expected)

    def test_bop(self):
        T = self._makeRecord("T", "id pt")
        target = self._makeQuery().from_(T).where(T.pt != 3)
        result = self._callFUT(target, {})
        expected = "SELECT T.id, T.pt FROM T WHERE (T.pt <> 3)"
        self.assertEqual(result, expected)

    def test_in(self):
        T = self._makeRecord("T", "id pt")
        target = self._makeQuery().from_(T).where(T.pt.in_(["3", "4", "5"]))
        result = self._callFUT(target, {})
        expected = "SELECT T.id, T.pt FROM T WHERE (T.pt IN ('3', '4', '5'))"
        self.assertEqual(result, expected)

    def test_between(self):
        T = self._makeRecord("T", "id, l, r")
        target = self._makeQuery().from_(T).where(T.l.between(T.r))
        result = self._callFUT(target, {})
        expected = "SELECT T.id, T.l, T.r FROM T WHERE (T.l BETWEEN T.r)"
        self.assertEqual(result, expected)

    def test_alias_column(self):
        from nendo.alias import alias
        T = self._makeRecord("T", "id")
        target = self._makeQuery().from_(T).select(alias(T.id, "t_id"))
        result = self._callFUT(target, {})
        expected = "SELECT T.id as t_id FROM T"
        self.assertEqual(result, expected)

    def test_alias_table(self):
        from nendo.alias import alias
        T = self._makeRecord("T", "id")
        t = alias(T, "t")
        target = self._makeQuery().from_(t).select(t.id)
        result = self._callFUT(target, {})
        expected = "SELECT t.id FROM T as t"
        self.assertEqual(result, expected)

    def test_order_by(self):
        T = self._makeRecord("T", "id")
        target = self._makeQuery().from_(T).select(T.id).order_by(T.id.desc())
        result = self._callFUT(target, {})
        expected = "SELECT T.id FROM T ORDER BY T.id DESC"
        self.assertEqual(result, expected)

    def test_subquery_as_record(self):
        from nendo.alias import alias
        tb1 = self._makeRecord("tb1", "id tb2_id")
        tb2 = self._makeRecord("tb2", "id id2")
        q = self._makeQuery().from_(tb2, tb1).where(tb2.id == tb1.tb2_id).select(tb2.id2)
        sub_q = alias(q, "sub_q")
        target = self._makeQuery().from_(tb1.join(sub_q, tb1.id <= sub_q.tb2.id2))
        result = self._callFUT(target, {})
        expected = "SELECT tb1.id, tb1.tb2_id, sub_q.tb2_id2 FROM tb1 JOIN (SELECT tb2.id2 as tb2_id2 FROM tb2, tb1 WHERE (tb2.id = tb1.tb2_id)) as sub_q ON (sub_q.tb2_id2 >= tb1.id)"
        self.assertEqual(result, expected)

    def test_subquery_as_record__conflict__at_select(self):
        from nendo.alias import alias
        from nendo.exceptions import ConflictName
        tb2 = self._makeRecord("tb2", "id id2")
        tb1 = self._makeRecord("tb1", "id tb2_id")
        q = self._makeQuery().from_(tb2, tb1).where(tb2.id == tb1.tb2_id).select(tb2.id2)
        sub_q = alias(q, "sub_q")
        target = self._makeQuery().from_(tb1.join(sub_q)).select(sub_q.tb1.id)
        with self.assertRaises(ConflictName):
            self._callFUT(target, {})

    def test_subquery_as_record__conflict__at_join(self):
        from nendo.alias import alias
        from nendo.exceptions import ConflictName
        tb2 = self._makeRecord("tb2", "id id2")
        tb1 = self._makeRecord("tb1", "id tb2_id")
        q = self._makeQuery().from_(tb2, tb1).where(tb2.id == tb1.tb2_id).select(tb2.id2)
        sub_q = alias(q, "sub_q")
        target = self._makeQuery().from_(tb1.join(sub_q, tb1.id <= sub_q.tb1.id))
        with self.assertRaises(ConflictName):
            self._callFUT(target, {})

    def test_subquery_as_column(self):
        from nendo.alias import alias
        tb2 = self._makeRecord("tb2", "id id2")
        tb1 = self._makeRecord("tb1", "id tb2_id")
        q = self._makeQuery().from_(tb2, tb1).where(tb2.id == tb1.tb2_id).select(tb2.id2)
        sub_q = alias(q, "sub_q")
        target = self._makeQuery().from_(tb1).where(tb1.tb2_id == sub_q().tb2.id).select(tb1.id)
        result = self._callFUT(target, {})
        expected = "SELECT tb1.id FROM tb1 WHERE ((SELECT tb2.id2 as tb2_id2 FROM tb2, tb1 WHERE (tb2.id = tb1.tb2_id)) = tb1.tb2_id)"
        self.assertEqual(result, expected)
