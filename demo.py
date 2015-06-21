from nendo import make_record, Query
from nendo.compiler import compiler
import logging
# logging.basicConfig(level=logging.DEBUG)


T = make_record("T", "id name")
G = make_record("G", "id name t_id")


def pp(q, context={}):
    print(compiler(q, context))

pp(Query().from_(T).select(T.id))
pp(Query().from_(T.join(G, T.id == G.t_id)).select(T.name, G.name))
q = Query().from_(T.join(G, T.id == G.t_id)).select(T.name, G.name)
pp(Query().from_(T.join(q)))
