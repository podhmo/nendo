# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from nendo.record import make_record
from nendo.query import Query


__all__ = [
    "make_record",
    "alias",
    "Query"
]
