import re
from datetime import datetime

import pyparsing as pp
from bson import ObjectId
from bson.errors import InvalidId
from dateutil import parser as date_parser

UPPER_CASE = object()
FIELD_TYPES = dict([
    ('id', ObjectId),
    ('name', str),
    ('description', str),
    ('tags', str),
    ('start_time', datetime),
    ('stop_time', datetime),
    ('heartbeat', datetime),
    ('status', UPPER_CASE),
    ('exit_code', int),
    ('storage_dir', str),
    ('exc_info.hostname', str),
    ('exc_info.work_dir', str),
    ('args', str)
])
REGEX_FIELDS = ['name', 'description', 'storage_dir', 'exc_info.work_dir']


class BadQueryError(Exception):
    """Error to indicate the given query is a bad query."""


class Query(object):
    """Base class for query objects."""

    def optimize(self):
        raise NotImplementedError()

    def mongo_filter(self):
        raise NotImplementedError()


class NullQuery(object):

    def optimize(self):
        return self

    def mongo_filter(self):
        raise RuntimeError('`NullQuery.mongo_filter()` is called. '
                           'Did you forget to call `optimize()`?')


class BadQuery(object):

    def optimize(self):
        return self

    def mongo_filter(self):
        raise RuntimeError('`BadQuery.mongo_filter()` is called. '
                           'Did you forget to call `optimize()`?')


class AllFieldQuery(Query):

    def __init__(self, phrase):
        self.phrase = phrase

    def __repr__(self):
        return repr(self.phrase)

    def __eq__(self, other):
        return isinstance(other, AllFieldQuery) and other.phrase == self.phrase

    def optimize(self):
        terms = []
        for key in FIELD_TYPES:
            t = FieldQueryTerm(key, self.phrase)
            t = t.optimize()
            if not isinstance(t, (NullQuery, BadQuery)):
                terms.append(t)
        if not terms:
            return NullQuery()
        return OrQuery(terms)

    def mongo_filter(self):
        raise RuntimeError('AllFieldQuery.mongo_filter is called. '
                           'Did you forget to call `optimize()`?')


class FieldQueryTerm(Query):

    def __init__(self, field, phrase):
        if field == 'id':
            field = '_id'
        try:
            type_ = FIELD_TYPES.get(field, None)
            if type_ is not None:
                if type_ is str:
                    phrase = str(phrase)
                elif type_ is UPPER_CASE:
                    phrase = str(phrase).upper()
                elif type_ is ObjectId:
                    phrase = ObjectId(str(phrase))
                elif type_ is int:
                    phrase = int(phrase)
                elif type_ is float:
                    phrase = float(phrase)
                elif type_ is datetime:
                    phrase = date_parser.parse(str(phrase))
        except (ValueError, TypeError, InvalidId):
            pass

        self.field = str(field)
        self.phrase = phrase
        self.bad_query = False

    def __repr__(self):
        bad_flag = ',bad' if self.bad_query else ''
        return 'FieldQuery({}:{}{})'.format(
            self.field, repr(self.phrase), bad_flag)

    def __eq__(self, other):
        return (isinstance(other, FieldQueryTerm) and
                other.field == self.field and
                other.phrase == self.phrase and
                other.bad_query == self.bad_query)

    def optimize(self):
        if self.bad_query:
            return BadQuery()
        if self.phrase is None:
            return NullQuery()
        return self

    def mongo_filter(self):
        if self.bad_query:
            raise RuntimeError('Bad query.')
        if isinstance(self.phrase, str) and self.field in REGEX_FIELDS:
            return {self.field: {
                '$regex': re.escape(self.phrase),
                '$options': 'ism',
            }}
        return {self.field: self.phrase}


class AndQuery(Query):

    def __init__(self, terms):
        self.terms = list(terms)

    def __repr__(self):
        return 'And({})'.format(','.join(map(str, self.terms)))

    def __eq__(self, other):
        return isinstance(other, AndQuery) and other.terms == self.terms

    def optimize(self):
        terms = [t.optimize() for t in self.terms]
        terms2 = []
        for t in terms:
            if isinstance(t, AndQuery):
                terms2.extend(t.terms)
            elif isinstance(t, BadQuery):
                return BadQuery()
            elif not isinstance(t, NullQuery):
                terms2.append(t)
        if not terms2:
            return NullQuery()
        if len(terms2) == 1:
            return terms2[0]
        return AndQuery(terms2)

    def mongo_filter(self):
        return {'$and': [t.mongo_filter() for t in self.terms]}


class OrQuery(Query):

    def __init__(self, terms):
        self.terms = list(terms)

    def __repr__(self):
        return 'Or({})'.format(','.join(map(str, self.terms)))

    def __eq__(self, other):
        return isinstance(other, OrQuery) and other.terms == self.terms

    def optimize(self):
        terms = [t.optimize() for t in self.terms]
        terms2 = []
        for t in terms:
            if isinstance(t, OrQuery):
                terms2.extend(t.terms)
            elif not isinstance(t, (NullQuery, BadQuery)):
                terms2.append(t)
        if not terms2:
            return NullQuery()
        if len(terms2) == 1:
            return terms2[0]
        return OrQuery(terms2)

    def mongo_filter(self):
        return {'$or': [t.mongo_filter() for t in self.terms]}


class NotQuery(Query):

    def __init__(self, term):
        self.term = term

    def __repr__(self):
        return 'Not({})'.format(self.term)

    def __eq__(self, other):
        return isinstance(other, NotQuery) and other.term == self.term

    def optimize(self):
        t = self.term.optimize()
        if isinstance(t, (BadQuery, NullQuery)):
            return NullQuery()
        if isinstance(t, NotQuery):
            return t.term
        return self

    def mongo_filter(self):
        return {'$not': self.term.mongo_filter()}


class QueryParser(object):
    unicode_printables = ''.join(
        pp.unichr(c) for c in range(65536) if not pp.unichr(c).isspace())
    singlePhrase = pp.Word(unicode_printables). \
        setParseAction(lambda s, l, t: t[0])
    quotedPhrase = pp.QuotedString('"', unquoteResults=True, escChar='\\'). \
        setParseAction(lambda s, l, t: t[0])
    phrase = (quotedPhrase | singlePhrase).setParseAction(lambda s, l, t: t[0])
    field_name = pp.Word(pp.alphanums + '._')
    field_query = (field_name + pp.Literal(':') + phrase). \
        setParseAction(lambda s, l, t: FieldQueryTerm(t[0], t[2]))
    all_field_query = pp.Group(phrase). \
        setParseAction(lambda s, l, t: AllFieldQuery(t[0][0]))

    query_string = pp.OneOrMore(field_query | all_field_query). \
        setParseAction(lambda s, l, t: AndQuery(t))


def parse_query(query_string):
    """
    Parse a query string into :class:`Query`.

    Args:
        query_string (str): The query string.

    Returns:
        Query: The parsed query object.
    """
    try:
        ret = QueryParser.query_string.parseString(query_string, parseAll=True)
        ret = ret[0]
        return ret
    except pp.ParseBaseException:
        raise BadQueryError()


def build_filter_dict_from_query_string(query_string):
    """
    Build a MongoDB filter dict from a simple string query.

    Args:
        query_string (str): The query string.

    Returns:
        dict[str, any]: The filter dict.
    """
    query = parse_query(query_string)
    query = query.optimize()
    if isinstance(query, NullQuery):
        return {}
    elif isinstance(query, BadQuery):
        raise BadQueryError()
    else:
        return query.mongo_filter()


if __name__ == '__main__':
    query = parse_query('exit_code:0')
    print(query)
    print(query.optimize())
