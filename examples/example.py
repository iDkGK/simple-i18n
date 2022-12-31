import json
from simple_i18n import I18n

i18n = I18n({
    'locales': ['en', 'ru', 'zh', 'fr', 'ko', 'de'], # setup some locales - other locales default to en silently
    'fallbacks': {'sk': 'de', 'de-*': 'de' }, # fallback from Slovak to German and from any localized German (de-at, de-li etc.) to German
    'defaultLocale': 'en', # you may alter a site wide default locale
    'retryInDefaultLocale': True, # will return translation from defaultLocale in case current locale doesn't provide it
    'cookie': 'yourcookiename', # sets a custom cookie name to parse locale settings from - defaults to None
    'header': 'accept-language', # sets a custom header name to read the language preference from - accept-language header by default
    'queryParameter': 'lang', # query parameter to switch locale (ie. /home?lang=ch) - defaults to None
    'directory': 'custom/path/to/locales/', # where to store json files - defaults to './locales' relative to modules directory
    'directoryPermissions': '755', # control mode on directory creation - defaults to NULL which defaults to umask of process user. Setting has no effect on win.
    'autoReload': True, # watch for changes in JSON files to reload locale on updates - defaults to false
    'updateFiles': False, # whether to write new locale information to disk - defaults to true
    'syncFiles': False, # sync locale information across all files - defaults to false
    'indent': '\t', # what to use as the indentation unit - defaults to '\t'
    'extension': '.json', # setting extension of json files - defaults to '.json' (you might want to set this to '.js' according to webtranslateit)
    'prefix': '', # setting prefix of json files name - default to none '' (in case you use different locale files naming scheme (webapp-en.json), rather then just en.json)
    'objectNotation': False, # enable object notation
    'logDebugFn': lambda msg: print(msg), # setting of log level DEBUG - default to logging.getLogger(__name__).debug
    'logWarnFn': lambda msg: print(msg), # setting of log level WARN - default to logging.getLogger(__name__).warning
    'logErrorFn': lambda msg: print(msg), # setting of log level ERROR - default to logging.getLogger(__name__).error
    'missingKeyFn': lambda locale, value: value, # used to alter the behaviour of missing keys
    'register': globals(), # object or [obj1, obj2] to bind the i18n api and current locale to - defaults to None
    'api': {}, # hash to specify different aliases for i18n's internal methods to apply on the request/response objects (method -> alias).
               # note that this will *not* overwrite existing properties with the same name
    'preserveLegacyCase': True, # When set to true, downcase locale when passed on queryParam; e.g. lang=en-US becomes en-us.
                                # When set to false, the queryParam value will be used as passed;
                                # e.g. lang=en-US remains en-US.
                                # defaults to true
    # 'staticCatalog': {}, # set the language catalog statically
                           # also overrides locales
    'mustacheConfig': { # use mustache with customTags (https://www.npmjs.com/package/mustache#custom-delimiters) or disable mustache entirely
        'tags': ['{{', '}}'],
        'disable': False
    },
    'parser': json # Parser can be any object that responds to .loads & .dumps
})

# try using locale 'sk', however this locale is unavailable and will fallback to 'de'
i18n.setLocale('sk')

# using i18n singleton (i18n.locale == 'de')
i18n.__('Hello') # -> Hallo
i18n.__('Hello %s', 'Marcus') # -> Hallo Marcus
i18n.__('Hello {{name}}', { 'name': 'Marcus' }) # -> Hallo Marcus

# using api bound to globals (locale == 'de')
__('Hello') # -> Hallo
__('Hello %s', 'Marcus') # -> Hallo Marcus
__('Hello {{name}}', { 'name': 'Marcus' }) # -> Hallo Marcus

# passing specific locale
i18n.__({ 'phrase': 'Hello', 'locale': 'fr' }) # -> Salut
i18n.__({ 'phrase': 'Hello %s', 'locale': 'fr' }, 'Marcus') # -> Salut Marcus
i18n.__({ 'phrase': 'Hello {{name}}', 'locale': 'fr' }, { 'name': 'Marcus' }) # -> Salut Marcus

