__all__ = ['escapeRegExp', 'watchFiles', 'getArgsList', 'parseInterval', 'checkValues']


# dependencies
from itertools import chain
from math import inf, nan
from re import compile, sub
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# utils
escapeRegExp = lambda string: sub(r'[.*+?^${}()|[\]\\]', lambda substring: f'\\{substring.group(0)}', string)

watchFiles = lambda path, handler: _watch(path, handler)

getArgsList = lambda locals, keys: list(chain(*[list(value) if name == 'args' else list(value.values()) if name == 'kwargs' else [value] for name, value in {key: locals[key] for key in keys}.items()]))

parseInterval = lambda string: _entry(string)

checkValues = lambda obj, *keytypes: False not in [keytype in obj if type(keytype) is str else False not in [False if len(keytype) < 2 else keytype[0] in obj and type(obj[keytype[0]]) in keytype[1:]] if type(keytype) is list else False for keytype in keytypes]


# private variables & functions

class _EventHandler(FileSystemEventHandler):
    def __init__(self, handler) -> None:
        super().__init__()
        self.locked = False
        self.handler = handler

    def on_any_event(self, event):
        if not self.locked:
            self.locked = True
            self.handler(event)
        self.locked = False

def _watch(path, hdlr):
    handler = _EventHandler(hdlr)
    observer = Observer()
    observer.schedule(handler, path)
    observer.start()

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

