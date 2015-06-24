from nendo import make_record, Query, alias
from nendo.query import ConflictName, MissingName
from nendo.compiler import compiler
import logging
logging.basicConfig(level=logging.DEBUG)


T = make_record("T", "id name")
T1 = alias(T, "T1")
G = make_record("G", "id name t_id")


def pp(q, context={}):
    print(compiler(q, context))


pp(Query().from_(T).select(T.id))
pp(Query().from_(T).select(alias(T.id, "t_id")))
pp(Query().from_(T.join(G, T.id == G.t_id)).select(T.name, G.name))
try:
    pp(Query().from_(T.join(T, T.id == T.id)).select(T.name, G.name))
except ConflictName as e:
    print("conflict:", e)
try:
    pp(Query().from_(T).where(G.id >= 1))
except MissingName as e:
    print("missing:", e)
try:
    pp(Query().from_(T1).where(T.id >= 1))
except MissingName as e:
    print("missing:", e)
try:
    pp(Query().from_(T).where(T1.id >= 1))
except MissingName as e:
    print("missing:", e)

pp(Query().from_(T.join(T1, T.id == T1.id)).select(T.name, T1.name))
subq = alias(Query().from_(T.join(G, T.id == G.t_id)).select(T.name, G.name), "subq")
pp(Query().from_(T.join(subq)).where(T.id >= 1, T.id <= 10).select(T.id, subq.G.name))

# pp(Query().from_(T).select(fn.count(T.id)))
# on, whereについてandとかorでつなげていく形が正しい
# subq.nameをエラーにしたい
# subqueryでselectに要素追加したい
# 関数適用したい

# 補完されて欲しい
# a = alias(Query().from_(T).where(T.id == 1), "a")
# b = alias(Query().from_(G).where(G.id == 1), "b")
# pp(Query().from_(a.join(b)).select(a.T.id, b.G.id))
