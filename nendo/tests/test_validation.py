# -*- coding:utf-8 -*-
import unittest
from evilunit import test_target


@test_target("nendo.query:Query")
class ValidationTests(unittest.TestCase):
    def _makeRecord(self, *args, **kwargs):
        from nendo.record import make_record
        return make_record(*args, **kwargs)

    def test_ok(self):
        T = self._makeRecord("T", "id")
        query = self._makeOne()
        target = (query.from_(T).select(T.id))
        context = {}
        target.validate(context)

    def test_confict_column(self):
        from nendo.exceptions import ConflictName

        T = self._makeRecord("T", "id")
        query = self._makeOne()
        target = (query.from_(T, T))
        context = {}
        with self.assertRaises(ConflictName):
            target.validate(context)

    def test_confict_column__with_alias(self):
        from nendo.alias import alias

        T = self._makeRecord("T", "id")
        query = self._makeOne()
        target = (query.from_(T, alias(T, "T1")))
        context = {}
        target.validate(context)

    def test_missing_table(self):
        from nendo.exceptions import MissingName

        T = self._makeRecord("T", "id")
        G = self._makeRecord("G", "id")
        query = self._makeOne()
        target = (query.from_(T).select(G.id))
        context = {}
        with self.assertRaises(MissingName):
            target.validate(context)

    def test_missing_table__where_clause(self):
        from nendo.exceptions import MissingName

        T = self._makeRecord("T", "id")
        G = self._makeRecord("G", "id")
        query = self._makeOne()
        target = (query.from_(T).where(G.id == 1))
        context = {}
        with self.assertRaises(MissingName):
            target.validate(context)

    def test_missing_table_with_alias(self):
        from nendo.exceptions import MissingName
        from nendo.alias import alias

        T = self._makeRecord("T", "id")
        T1 = alias(T, "T1")
        query = self._makeOne()
        target = (query.from_(T).select(T1.id))
        context = {}
        with self.assertRaises(MissingName):
            target.validate(context)

    def test_missing_table_with_alias2(self):
        from nendo.exceptions import MissingName
        from nendo.alias import alias

        T = self._makeRecord("T", "id")
        T1 = alias(T, "T1")
        query = self._makeOne()
        target = (query.from_(T1).select(T.id))
        context = {}
        with self.assertRaises(MissingName):
            target.validate(context)
