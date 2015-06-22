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
        expected = "SELECT * FROM T WHERE (NOT (T.pt = 3))"
        self.assertEqual(result, expected)

    def test_bop(self):
        T = self._makeRecord("T", "id pt")
        target = self._makeQuery().from_(T).where(T.pt != 3)
        result = self._callFUT(target, {})
        expected = "SELECT * FROM T WHERE (T.pt <> 3)"
        self.assertEqual(result, expected)

    def test_in(self):
        T = self._makeRecord("T", "id pt")
        target = self._makeQuery().from_(T).where(T.pt.in_(["3", "4", "5"]))
        result = self._callFUT(target, {})
        expected = "SELECT * FROM T WHERE (T.pt IN ('3', '4', '5'))"
        self.assertEqual(result, expected)

    def test_between(self):
        T = self._makeRecord("T", "id, l, r")
        target = self._makeQuery().from_(T).where(T.l.between(T.r))
        result = self._callFUT(target, {})
        expected = "SELECT * FROM T WHERE (T.l BETWEEN T.r)"
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
        target = self._makeQuery().from_(alias(T, "t")).select(alias(T, "t").id)
        result = self._callFUT(target, {})
        expected = "SELECT t.id FROM T as t"
        self.assertEqual(result, expected)

    def test_order_by(self):
        T = self._makeRecord("T", "id")
        target = self._makeQuery().from_(T).select(T.id).order_by(T.id.desc())
        result = self._callFUT(target, {})
        expected = "SELECT T.id FROM T ORDER BY T.id DESC"
        self.assertEqual(result, expected)

