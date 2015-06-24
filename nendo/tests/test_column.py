# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


def _makeRecord(*args, **kwargs):
    from nendo import make_record
    return make_record(*args, **kwargs)


@test_target("nendo.query:Query")
class PropsTest(unittest.TestCase):
    def test_from_table(self):
        T = _makeRecord("T", "id, name")
        result = T.props()
        self.assertEqual(result, [T.id, T.name])

    def test_from_query_from_column_list(self):
        T = _makeRecord("T", "id, name")
        query = self._makeOne().from_(T).select(T.id)
        result = list(query._from.props())
        self.assertEqual(result, [T.id, T.name])

    def test_from_query_select_column_list(self):
        T = _makeRecord("T", "id, name")
        result = list(self._makeOne().from_(T).select(T.id).props())
        self.assertEqual(result, [T.id])

    def test_from_query(self):
        T = _makeRecord("T", "id, name")
        query = self._makeOne().from_(T)
        result = list(query.props())
        self.assertEqual(result, [T.id, T.name])

    def test_from_query__select(self):
        T = _makeRecord("T", "id, name")
        query = self._makeOne().from_(T).select(T.id)
        result = list(query.props())
        self.assertEqual(result, [T.id])

    def test_from_subquery(self):
        from nendo.alias import alias
        T = _makeRecord("T", "id, name")
        sub_q = alias(self._makeOne().from_(T), "sub_q")
        query = self._makeOne().from_(sub_q)
        result = list(query.props())
        self.assertEqual(result, [T.id, T.name])

    def test_from_subquery__select(self):
        from nendo.alias import alias
        T = _makeRecord("T", "id, name")
        sub_q = alias(self._makeOne().from_(T), "sub_q")
        query = self._makeOne().from_(sub_q).select(sub_q.T.id)
        result = list(query.props())
        self.assertEqual(result, [sub_q.T.id])

    def test_from_join(self):
        T = _makeRecord("T", "id, name")
        G = _makeRecord("G", "id, name, t_id")
        query = self._makeOne().from_(T.join(G, T.id == G.t_id))
        result = list(query.props())
        self.assertEqual(result, [T.id, T.name, G.id, G.name, G.t_id])

    def test_from_join__select(self):
        T = _makeRecord("T", "id, name")
        G = _makeRecord("G", "id, name, t_id")
        query = self._makeOne().from_(T.join(G, T.id == G.t_id)).select(T.id, G.id)
        result = list(query.props())
        self.assertEqual(result, [T.id, G.id])
