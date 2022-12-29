__all__ = ['escapeRegExp', 'getArgsList', 'parseInterval']

# dependencies
from itertools import chain
from math import inf, nan
from re import compile, sub

# utils
escapeRegExp = lambda string: sub(r'[.*+?^${}()|[\]\\]', lambda substring: f'\\{substring.group(0)}', string)

getArgsList = lambda locals, keys: list(chain(*[list(value) if name == 'args' else list(value.values()) if name == 'kwargs' else [value] for name, value in {key: locals[key] for key in keys}.items()]))

parseInterval = lambda string: _entry(string)

_patternParts = {
    'value': '[-+]?(?:Infinity|[[0-9]*\\.?\\d*(?:[eE][-+]?\\d+)?)',
    'leftBrace': '[\\(\\]\\[]',
    'delimeter': ',',
    'rightBrace': '[\\)\\]\\[]',
}

_PATTERN = compile('(' + _patternParts['leftBrace'] + ')' +
    '(' + _patternParts['value'] + ')?' +
    '(' + _patternParts['delimeter'] + ')?' +
    '(' + _patternParts['value'] + ')?' +
    '(' + _patternParts['rightBrace'] + ')'
)

def _execPattern(string):
    match = _PATTERN.findall(string)
    if not match:
        return None
    match = [match[i] if i <= len(match) else None for i in range(6)]
    _ = match[0]
    leftBrace = match[1]
    fromValue = match[2]
    delimeter = match[3]
    toValue = match[4]
    rightBrace = match[5]
    return {
        'leftBrace': leftBrace,
        'fromValue': fromValue,
        'delimeter': delimeter,
        'toValue': toValue,
        'rightBrace': rightBrace
    }

def _parse(string):
    match = _execPattern(string)
    if not match:
        return None
    return {
        'from': {
            'value': +match['fromValue'] if match['fromValue'] is not None else +inf,
            'included': match['leftBrace'] == '['
        },
        'to': {
            'value': +match['toValue'] if match['toValue'] is not None else +inf if match['delimeter'] else match['fromValue'] if match['fromValue'] is not None else nan,
            'included': match['rightBrace'] == ']'
        }
    }

def _check(interval):
    if interval['from']['value'] == interval['to']['value']:
        return interval['from']['included'] and interval['to']['included']
    return min(interval['from']['value'], interval['to']['value']) == interval['from']['value']

def _entry(string):
    intv = _parse(string)
    if not intv and not _check(intv):
        return None
    return intv

