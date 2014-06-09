# -*- coding: utf-8 -*-
"""
format-sql

Copyright (c) 2014, Friedrich Paetzke (paetzke@fastmail.fm)
All rights reserved.

"""
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

import pytest
from format_sql.tokenizer import normalize_sql, Token, tokenize, Type


def assert_tokens(sql, expected_tokens):
    tokens = tokenize(sql)
    for token, expected_token in zip_longest(tokens, expected_tokens):
        assert token.value == expected_token.value
        assert token._type == expected_token._type


def _test(data):
    assert_tokens(data.sql, data.tokens)


def test_tokenize_select_from(select_from):
    _test(select_from)


def test_tokenize_select_with_group_and_having(select_with_group_and_having):
    _test(select_with_group_and_having)


def test_tokenize_select_with_limit(select_with_limit):
    _test(select_with_limit)


def test_tokenize_select_with_limit_and_offset(select_with_limit_and_offset):
    _test(select_with_limit_and_offset)


def test_tokenize_select_with_complex_filter(select_with_complex_filter):
    _test(select_with_complex_filter)


def test_tokenize_select_with_sub_select_in_filter(select_with_sub_select_in_filter):
    _test(select_with_sub_select_in_filter)


def test_tokenize_select_with_complex_having(select_with_complex_having):
    _test(select_with_complex_having)


def test_tokenize_select_with_where_filters(select_with_where_filters):
    _test(select_with_where_filters)


def test_tokenize_select_with_join(select_with_join):
    _test(select_with_join)


def test_tokenize_select_with_join_and_on(select_with_join_and_on):
    _test(select_with_join_and_on)


def test_tokenize_select_with_multiple_columns(select_with_multiple_columns):
    _test(select_with_multiple_columns)


def test_tokenize_select_with_not_in_compare(select_with_not_in_compare):
    _test(select_with_not_in_compare)


def test_tokenize_select_with_filter_in_list(select_with_filter_in_list):
    _test(select_with_filter_in_list)


def test_tokenize_select_with_multiple_joins(select_with_multiple_joins):
    _test(select_with_multiple_joins)


def test_tokenize_select_in_from(select_in_from):
    _test(select_in_from)


def test_tokenize_select_in_from_and_join(select_in_from_and_join):
    _test(select_in_from_and_join)


def test_tokenize_select_with_single_order_value(select_with_single_order_value):
    _test(select_with_single_order_value)


def test_tokenize_select_with_order_values(select_with_order_values):
    _test(select_with_order_values)


@pytest.mark.parametrize('sql, expected_token', [
    ('SELECT', Token(Type.SELECT, 'SELECT')),
    ('SELECT DISTINCT', Token(Type.SELECT, 'SELECT DISTINCT')),
    ('SELECT SQL_NO_CACHE', Token(Type.SELECT, 'SELECT SQL_NO_CACHE')),
])
def test_handle_select(sql, expected_token):
    assert_tokens(sql, [expected_token])


@pytest.mark.parametrize('sql, expected_token', [
    ('INNER JOIN', Token(Type.JOIN, 'INNER JOIN')),
    ('JOIN', Token(Type.JOIN, 'JOIN')),
    ('LEFT JOIN', Token(Type.JOIN, 'LEFT JOIN')),
    ('LEFT OUTER JOIN', Token(Type.JOIN, 'LEFT OUTER JOIN')),
    ('RIGHT JOIN', Token(Type.JOIN, 'RIGHT JOIN')),
    ('RIGHT OUTER JOIN', Token(Type.JOIN, 'RIGHT OUTER JOIN')),
    ('FULL OUTER JOIN', Token(Type.JOIN, 'FULL OUTER JOIN')),
])
def test_handle_join(sql, expected_token):
    assert_tokens(sql, [expected_token])


@pytest.mark.parametrize('sql, expected_token', [
    ('=', Token(Type.COMPARE, '=')),
    ('<', Token(Type.COMPARE, '<')),
    ('!=', Token(Type.COMPARE, '!=')),
    ('<>', Token(Type.COMPARE, '<>')),
    ('>', Token(Type.COMPARE, '>')),
    ('LIKE', Token(Type.COMPARE, 'LIKE')),
    ('LIKE BINARY', Token(Type.COMPARE, 'LIKE BINARY')),
])
def test_handle_compare(sql, expected_token):
    assert_tokens(sql, [expected_token])


@pytest.mark.parametrize('sql, expected_token', [
    ('my_table AS t1', Token(Type.STR, 'my_table AS t1')),
    ('q.`cnd`', Token(Type.STR, 'q.`cnd`')),
    ('gt.fu_d', Token(Type.STR, 'gt.fu_d')),
    ('q.`cnd` AS e2', Token(Type.STR, 'q.`cnd` AS e2')),
    ('count(1)', Token(Type.STR, 'count(1)')),
    ('count(1) AS cnt', Token(Type.STR, 'count(1) AS cnt')),
    ('count(`s`.`dd`) AS cnt', Token(Type.STR, 'count(`s`.`dd`) AS cnt')),
    ('%(some_thing)s', Token(Type.STR, '%(some_thing)s')),
    ('%%(some_thing_2)s', Token(Type.STR, '%%(some_thing_2)s')),
    ('s.id ASC', Token(Type.STR, 's.id ASC')),
    ('d.d DESC', Token(Type.STR, 'd.d DESC')),
    ('COUNT(*)', Token(Type.STR, 'COUNT(*)')),
    ('COUNT(*) AS cnt', Token(Type.STR, 'COUNT(*) AS cnt')),
    ("'value is here'", Token(Type.STR, "'value is here'")),
    ('INTERVAL', Token(Type.STR, 'INTERVAL')),
    ('ANDOR', Token(Type.STR, 'ANDOR')),
    ('FROMME', Token(Type.STR, 'FROMME')),
    ('ORDER BY', Token(Type.ORDER, 'ORDER BY'))
])
def test_handle_str(sql, expected_token):
    assert_tokens(sql, [expected_token])


@pytest.mark.parametrize('sql, expected_sql, expected_has_semicolon', [
    ('Select * FROM my_table', 'SELECT * FROM my_table', False),
    ('left join', 'LEFT JOIN', False),
    ('x in ("78", "d")', 'x IN ("78", "d")', False),
    ('Select * FROM my_table;', 'SELECT * FROM my_table', True),
])
def test_normalize_sql(sql, expected_sql, expected_has_semicolon):
    normalized, has_semicolon = normalize_sql(sql)
    assert normalized == expected_sql
    assert has_semicolon == expected_has_semicolon
