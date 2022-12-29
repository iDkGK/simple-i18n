__title__ = 'simple i18n'
__description__ = 'Lightweight simple translation JavaScript module \'i18n\' in Python implementation.'
__url__ = 'https://github.com/iDkGK/simple-i18n'
__version__ = '0.1.0'
__author__ = 'iDkGK'
__author_email__ = "1444807655@qq.com"
__license__ = 'BSD'


# dependencies
import functools
import inspect
import json
import logging
import os
import pystache
import re
import shutil
import stat
from typing import Any, TypeVar
from types import FunctionType, ModuleType
from .utilities import *

# create constructor function
def I18n(_OPTS: dict[str, Any] = {}):
    MessageformatInstanceForLocale: dict = {}
    PluralsForLocale: dict = {}
    locales: dict = {}
    api = {
        '__': '__',
        '__n': '__n',
        '__l': '__l',
        '__h': '__h',
        '__mf': '__mf',
        'getLocale': 'getLocale',
        'setLocale': 'setLocale',
        'getCatalog': 'getCatalog',
        'getLocales': 'getLocales',
        'addLocale': 'addLocale',
        'removeLocale': 'removeLocale'
    }
    mustacheConfig: dict[str, list[str]|bool] = {
        'tags': ['{{', '}}'],
        'disable': False
    }
    mustacheRegex: re.Pattern|None = None
    pathsep: str = os.path.sep
    autoReload: bool = False
    cookiename: str|None = None
    languageHeaderName: str|None = None
    defaultLocale: str|None = None
    retryInDefaultLocale: bool = False
    directory: str|None = None
    directoryPermissions: int|None = None
    extension: str|None = None
    fallbacks: dict|None = None
    indent: str|None = None
    logDebugFn: FunctionType|None = None
    logErrorFn: FunctionType|None = None
    logWarnFn: FunctionType|None = None
    preserveLegacyCase: bool = True
    objectNotation: str|bool = False
    prefix: str|None = None
    queryParameter: str|None = None
    register: dict|None = None
    updateFiles: bool = True
    syncFiles: bool = False
    missingKeyFn: FunctionType|None = None
    parser: ModuleType|None = None

    # public exports
    i18n: dict = {}

    i18n['version'] = '0.1.0'

    def i18nConfigure(opt=_OPTS):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        # reset locales
        locales = {}

        # Provide custom API method aliases if desired
        # This needs to be processed before the first call to applyAPItoObject()
        if 'api' in opt and (type(opt['api']) is dict or type(opt['api']) is list):
            for method in opt['api']:
                alias = opt['api'][method]
                if method in api:
                    api[method] = alias

        # you may register i18n in global scope, up to you
        if 'register' in opt and (type(opt['register']) is dict or type(opt['register']) is list):
            register = opt['register']
            # or give an array objects to register to
            if type(opt['register']) is list:
                register = opt['register']
                for method in register:
                    applyAPItoObject(method)
            else:
                applyAPItoObject(opt['register'])

        # sets a custom cookie name to parse locale settings from
        cookiename = opt['cookie'] if 'cookie' in opt and type(opt['cookie']) is str else None

        # set the custom header name to extract the language locale
        languageHeaderName = opt['header'] if 'header' in opt and type(opt['header']) is str else 'accept-language'

        # query-string parameter to be watched - @todo: add test & doc
        queryParameter = opt['queryParameter'] if 'queryParameter' in opt and type(opt['queryParameter']) is str else None

        # where to store json files
        directory = opt['directory'] if 'directory' in opt and type(opt['directory']) is str else os.path.join(os.getcwd(), 'locales')

        # permissions when creating new directories
        directoryPermissions = int(opt['directoryPermissions'], 8) if 'directoryPermissions' in opt and type(opt['directoryPermissions']) is str else None

        # write new locale information to disk
        updateFiles = opt['updateFiles'] if 'updateFiles' in opt and type(opt['updateFiles']) is bool else True

        # sync locale information accros all files
        syncFiles = opt['syncFiles'] if 'syncFiles' in opt and type(opt['syncFiles']) is bool else False

        # what to use as the indentation unit (ex: '\t', '  ')
        indent = opt['indent'] if 'indent' in opt and type(opt['indent']) is str else '\t'

        # json files prefix
        prefix = opt['prefix'] if 'prefix' in opt and type(opt['prefix']) is str else ''

        # where to store json files
        extension = opt['extension'] if 'extension' in opt and type(opt['extension']) is str else '.json'

        # setting defaultLocale
        defaultLocale = opt['defaultLocale'] if 'defaultLocale' in opt and type(opt['defaultLocale']) is str else 'en'

        # allow to retry in default locale, useful for production
        retryInDefaultLocale = opt['retryInDefaultLocale'] if 'retryInDefaultLocale' in opt and type(opt['retryInDefaultLocale']) is bool else False

        # auto reload locale files when changed
        autoReload = opt['autoReload'] if 'autoReload' in opt and type(opt['autoReload']) is bool else False

        # enable object notation?
        objectNotation = opt['objectNotation'] if 'objectNotation' in opt else False
        if objectNotation == True:
            objectNotation = '.'

        # read language fallback map
        fallbacks = opt['fallbacks'] if 'fallbacks' in opt and (type(opt['fallbacks']) is dict or type(opt['fallbacks']) is list) else {}

        # setting custom logger functions
        logDebugFn = opt['logDebugFn'] if 'logDebugFn' in opt and type(opt['logDebugFn']) is FunctionType else logging.debug
        logWarnFn = opt['logWarnFn'] if 'logWarnFn' in opt and type(opt['logWarnFn']) is FunctionType else logging.warn
        logErrorFn = opt['logErrorFn'] if 'logErrorFn' in opt and type(opt['logErrorFn']) is FunctionType else logging.error
        preserveLegacyCase = opt['preserveLegacyCase'] if 'preserveLegacyCase' in opt and type(opt['preserveLegacyCase']) is bool else True

        # setting custom missing key function
        missingKeyFn = opt['missingKeyFn'] if 'missingKeyFn' in opt and type(opt['missingKeyFn']) is FunctionType else missingKey
        parser = opt['parser'] if 'parser' in opt and hasattr(opt['parser'], 'loads') and hasattr(opt['parser'], 'dumps') else json

        # when missing locales we try to guess that from directory
        opt['locales'] = list(opt['staticCatalog'].keys()) if 'staticCatalog' in opt else opt['locales'] if 'locales' in opt else guessLocales(directory)

        # some options should be disabled when using staticCatalog
        if 'staticCatalog' in opt:
            updateFiles = False
            autoReload = False
            syncFiles = False

        # customize mustache parsing
        if 'mustacheConfig' in opt:
            if 'tags' in opt['mustacheConfig'] and type(opt['mustacheConfig']['tags']) is list:
                mustacheConfig['tags'] = opt['mustacheConfig']['tags']
            if 'disable' in opt['mustacheConfig'] and opt['mustacheConfig']['disable'] == True:
                mustacheConfig['disable'] = True

        [start, end] = mustacheConfig['tags']
        mustacheRegex = re.compile(f'{escapeRegExp(start)}.*{escapeRegExp(end)}')

        # implicitly read all locales
        if 'locales' in opt and type(opt['locales']) is list:
            if 'staticCatalog' in opt:
                locales = opt['staticCatalog']
            else:
                for locale in opt['locales']:
                    read(locale)

            if autoReload:
                # watch changes of locale files (it's called twice because fs.watch is still unstable)
                # fs.watch(directory, (event, filename) => {
                #     const localeFromFile = guessLocaleFromFile(filename)
                #     if (localeFromFile && opt.locales.indexOf(localeFromFile) > -1) {
                #         logDebug('Auto reloading locale file '' + filename + ''.')
                #         read(localeFromFile)
                #     }
                # })
                raise NotImplementedError

    i18n['configure'] = i18nConfigure

    def i18nInit(request, response, next):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        raise NotImplementedError

    i18n['init'] = i18nInit

    def i18nTranslate(phrase=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        msg: Any = None
        argv = parseArgv(getArgsList(locals(), inspect.signature(i18nTranslate).parameters.keys()))
        namedValues = argv[0]
        arguments = argv[1]

        # called like __({phrase: 'Hello', locale: 'en'})
        if type(phrase) is dict or type(phrase) is list:
            if (
                'locale' in phrase and type(phrase['locale']) is str and
                'phrase' in phrase and type(phrase['phrase']) is str
            ):
                msg = translate(phrase['locale'], phrase['phrase'])
        # called like __('Hello')
        else:
            # get translated message with locale from scope (deprecated) or object
            msg = translate(getLocaleFromObject(i18n), phrase)

        # postprocess to get compatible to plurals
        if (type(msg) is dict or type(msg) is list) and 'one' in msg:
            msg = msg['one']

        # in case there is no 'one' but an 'other' rule
        if (type(msg) is dict or type(msg) is list) and 'other' in msg:
            msg = msg['other']

        # head over to postProcessing
        return postProcess(msg, namedValues, arguments)

    i18n['__'] = i18nTranslate

    def i18nMessageformat(phrase):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        raise NotImplementedError

    i18n['__mf'] = i18nMessageformat

    def i18nTranslationList(phrase):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        raise NotImplementedError

    i18n['__l'] = i18nTranslationList

    def i18nTranslationHash(phrase):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        raise NotImplementedError

    i18n['__h'] = i18nTranslationHash

    def i18nTranslatePlural(singular, plural, count):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        raise NotImplementedError

    i18n['__n'] = i18nTranslatePlural

    def i18nSetLocale(obj=None, locale=None, skipImplicitObjects=False):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        # when given an array of objects => setLocale on each
        if type(obj) is list and type(locale) is str:
            for i in range(len(obj), 0, -1):
                i18n['setLocale'](obj[i], locale, True)
            return i18n['getLocale'](obj[0])

        # defaults to called like i18n.setLocale(req, 'en')
        targetObject = obj
        targetLocale = locale

        # called like req.setLocale('en') or i18n.setLocale('en')
        if locale is None and type(obj) is str:
            targetObject = i18n
            targetLocale = obj

        # consider a fallback
        if targetLocale not in locales or not locales[targetLocale]:
            targetLocale = getFallback(targetLocale, fallbacks) or targetLocale

        # now set locale on object
        targetObject['locale'] = targetLocale if targetLocale in locales and locales[targetLocale] else defaultLocale

        # consider any extra registered objects
        if type(register) is dict or type(register) is list:
            if type(register) is list and not skipImplicitObjects:
                for r in register:
                    r['locale'] = targetObject['locale']
            else:
                register['locale'] = targetObject['locale']

        # consider res
        if 'res' in targetObject and targetObject['res'] and not skipImplicitObjects:
            # escape recursion
            # @see  - https://github.com/balderdashy/sails/pull/3631
            #       - https://github.com/mashpie/i18n-node/pull/218.
            if 'locals' in targetObject['res'] and targetObject['res']['locals']:
                i18n['setLocale'](targetObject['res'], targetObject['locale'], True)
                i18n['setLocale'](targetObject['res']['locals'], targetObject['locale'], True)
            else:
                i18n['setLocale'](targetObject['res'], targetObject['locale'])

        # consider locals
        if 'locals' in targetObject and targetObject['locals'] and not skipImplicitObjects:
            # escape recursion
            # @see  - https://github.com/balderdashy/sails/pull/3631
            #       - https://github.com/mashpie/i18n-node/pull/218
            if 'res' in targetObject['locals'] and targetObject['locals']['res']:
                i18n['setLocale'](targetObject['locals'], targetObject['locale'], True)
                i18n['setLocale'](targetObject['locals']['res'], targetObject['locale'], True)
            else:
                i18n['setLocale'](targetObject['locals'], targetObject['locale'])

        return i18n['getLocale'](targetObject)

    i18n['setLocale'] = i18nSetLocale

    def i18nGetLocale(request):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        # called like i18n.getLocale(req)
        if request and 'locale' in request and request['locale']:
            return request['locale']

        # called like req.getLocale()
        return i18n['locale'] or defaultLocale

    i18n['getLocale'] = i18nGetLocale

    def i18nGetCatalog(obj, locale):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        raise NotImplementedError

    i18n['getCatalog'] = i18nGetCatalog

    def i18nGetLocales():
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        raise NotImplementedError

    i18n['getLocales'] = i18nGetLocales

    def i18nAddLocale(locale):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        raise NotImplementedError

    i18n['addLocale'] = i18nAddLocale

    def i18nRemoveLocale(locale):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        raise NotImplementedError

    i18n['removeLocale'] = i18nRemoveLocale

    # ===================
    # = private methods =
    # ===================

    def postProcess(msg=None, namedValues=None, arguments=[], count=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        # test for parsable interval string
        if re.compile(r'\|').search(msg):
            msg = parsePluralInterval(msg, count)

        # replace the counter
        if type(count) is int:
            msg = msg % count

        # if the msg string contains {{Mustache}} patterns we render it as a mini template
        if not mustacheConfig['disable'] and mustacheRegex.search(msg):
            pystache.defaults.DELIMITERS = tuple(mustacheConfig['tags'])
            msg = pystache.render(msg, namedValues, partials = {})

        # if we have extra arguments with values to get replaced,
        # an additional substition injects those strings afterwards
        if re.compile('%').search(msg) and arguments and len(arguments) > 0:
            msg = msg % tuple(arguments)

        return msg

    def argsEndWithNamedObject(arguments=[], *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        return (
            len(arguments) > 1 and
            arguments[len(arguments) - 1] is not None and
            (type(arguments[len(arguments) - 1]) is dict or 
             type(arguments[len(arguments) - 1]) is list)
        )

    def parseArgv(arguments=[], *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        namedValues: Any
        returnArgs: Any

        if argsEndWithNamedObject(arguments):
            namedValues = arguments[len(arguments) - 1]
            returnArgs = arguments[1:-1]
        else:
            namedValues = {}
            returnArgs = arguments[1:] if len(arguments) >= 2 else []

        return [namedValues, returnArgs]

    def applyAPItoObject(obj=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        alreadySetted = True

        # attach to itself if not provided
        for method in api:
            alias = api[method]

            # be kind rewind, or better not touch anything already existing
            if alias not in obj or not obj[alias]:
                alreadySetted = False
                obj[alias] = i18n[method]

        # set initial locale if not set
        if 'locale' not in obj or not obj['locale']:
            obj['locale'] = defaultLocale

        # escape recursion
        if alreadySetted:
            return

        # attach to response if present (ie. in express)
        if 'res' in obj:
            applyAPItoObject(obj['res'])

        # attach to locals if present (ie. in express)
        if 'locals' in obj:
            applyAPItoObject(obj['locals'])

    def guessLocales(dir=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        entries = os.listdir(dir)
        localesFound = []

        for i in range(len(entries), 0, -1):
            if re.compile(r'^\.').match(entries[i]):
                continue
            localeFromFile = guessLocaleFromFile(entries[i])
            if localeFromFile:
                localesFound.append(localeFromFile)

        return sorted(localesFound)

    def guessLocaleFromFile(filename=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        extensionRegex = re.compile(f'{extension}$')
        prefixRegex = re.compile(f'^{prefix}')

        if not filename:
            return False
        if prefix and not prefixRegex.match(filename):
            return False
        if extension and not extensionRegex.match(filename):
            return False
        return extensionRegex.sub('', prefixRegex.sub('', filename))

    def extractQueryLanguage(queryLanguage, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        raise NotImplementedError

    def guessLanguage(request, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        raise NotImplementedError

    def getAcceptedLanguagesFromHeader(header, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        raise NotImplementedError

    def getLocaleFromObject(obj=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        locale = None
        if 'scope' in obj:
            locale = obj['scope']['locale']
        if 'locale' in obj:
            locale = obj['locale']
        return locale

    def parsePluralInterval(phrase, count, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        returnPhrase = phrase
        phrases = re.split(r'\|', phrase)
        intervalRuleExists = False

        # some() breaks on 1st true
        def test(p):
            # access variables from upper function
            nonlocal returnPhrase, intervalRuleExists
            
            matches = re.match(r'^\s*([()[\]]+[\d,]+[()[\]]+)?\s*(.*)$', p)

            # not the same as in combined condition
            if matches and matches.group(1):
                intervalRuleExists = True
                if matchInterval(count, matches.group(1)) == True:
                    returnPhrase = matches.group(2)
                    return True
            else:
                # this is a other or catch all case, this only is taken into account if there is actually another rule
                if intervalRuleExists:
                    returnPhrase = p
            return False
        for p in phrases:
            if test(p):
                break
        return returnPhrase

    def matchInterval(number, interval, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        interval = parseInterval(interval)
        if interval and type(number) is int:
            if interval['from']['value'] == number:
                return interval['from']['included']
            if interval['to']['value'] == number:
                return interval['to']['included']

            return (
                min(interval['from']['value'], number) == interval['from']['value'] and
                max(interval['to']['value'], number) == interval['to']['value']
            )
        return False

    def translate(locale=None, singular=None, plural=None, skipSyncToAllFiles=False, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        # add same key to all translations
        if not skipSyncToAllFiles and syncFiles:
            syncToAllFiles(singular, plural)

        if locale is None:
            logWarn(f'WARN: No locale found - check the context of the call to __(). Using {defaultLocale} as current locale')
            locale = defaultLocale

        # try to get a fallback
        if locale not in locales or not locales[locale]:
            locale = getFallback(locale, fallbacks) or locale

        # attempt to read when defined as valid locale
        if locale not in locales or not locales[locale]:
            read(locale)

        # fallback to default when missed
        if locale not in locales or not locales[locale]:
            logWarn(f'WARN: Locale  {locale} couldn\'t be read - check the context of the call to $__. Using {defaultLocale} (default) as current locale')

            locale = defaultLocale
            read(locale)

        # dotnotaction add on, @todo: factor out
        defaultSingular = singular
        defaultPlural = plural
        if objectNotation:
            indexOfColon = singular.index(':')
            # We compare against 0 instead of -1 because
            # we don't really expect the string to start with ':'.
            if indexOfColon > 0:
                defaultSingular = singular[indexOfColon+1]
                singular = singular[0:indexOfColon]
            if plural and type(plural) is not int:
                indexOfColon = plural.index(':')
                if indexOfColon > 0:
                    defaultPlural = plural[indexOfColon+1]
                    plural = plural[0:indexOfColon]

        accessor = localeAccessor(locale, singular)
        mutator = localeMutator(locale, singular)

        if plural:
            if accessor() is None:
                # when retryInDefaultLocale is true - try to set default value from defaultLocale
                if retryInDefaultLocale and locale != defaultLocale:
                    logDebug(f'Missing {singular} in {locale} retrying in {defaultLocale}')
                    mutator(translate(defaultLocale, singular, plural, True))
                else:
                    mutator({
                        'one': defaultSingular or singular,
                        'other': defaultPlural or plural
                    })
                write(locale)

        if accessor() is None:
            # when retryInDefaultLocale is true - try to set default value from defaultLocale
                if retryInDefaultLocale and locale != defaultLocale:
                    logDebug(f'Missing {singular} in {locale} retrying in {defaultLocale}')
                    mutator(translate(defaultLocale, singular, plural, True))
                else:
                    mutator(defaultSingular or singular)
                write(locale)

        return accessor()

    def syncToAllFiles(singular=None, plural=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        for l in locales:
            translate(l, singular, plural, True)

    def localeAccessor(locale=None, singular=None, allowDelayedTraversal=True, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        # Bail out on non-existent locales to defend against internal errors.
        if locale not in locales or not locales[locale]:
            return localeAccessor

        # Handle object lookup notation
        indexOfDot = objectNotation and singular.rindex(objectNotation)
        if objectNotation and indexOfDot > 0 and indexOfDot < len(singular) - 1:
            # If delayed traversal wasn't specifically forbidden, it is allowed.
            # The accessor we're trying to find and which we want to return.
            accessor = None
            # An accessor that returns null.
            nullAccessor = lambda *args, **kwargs: None
            # Do we need to re-traverse the tree upon invocation of the accessor?
            reTraverse = False
            # Split the provided term and run the callback for each subterm.
            def reducer(obj, index):
                # access variables from upper function
                nonlocal accessor

                # Make the accessor return null.
                accessor = nullAccessor
                # If our current target object (in the locale tree) doesn't exist or
                # it doesn't have the next subterm as a member...
                if obj is None or (index in obj and obj[index]):
                    # ...remember that we need retraversal (because we didn't find our target).
                    reTraverse = allowDelayedTraversal
                    # Return null to avoid deeper iterations.
                    return None
                # We can traverse deeper, so we generate an accessor for this current level.
                accessor = lambda *args, **kwargs: obj[index]
                # Return a reference to the next deeper level in the locale tree.
                return obj[index]
            functools.reduce(reducer, singular.split(objectNotation), locales[locale])
            # Return the requested accessor.
            # If we need to re-traverse (because we didn't find our target term)
            # traverse again and return the new result (but don't allow further iterations)
            # or return the previously found accessor if it was already valid.
            return lambda *args, **kwargs: localeAccessor(locale, singular, False)() if reTraverse else accessor()
        else:
            # No object notation, just return an accessor that performs array lookup.
            return lambda *args, **kwargs: locales[locale][singular] if singular in locales[locale] else None

    def localeMutator(locale=None, singular=None, allowBranching=False, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        # Bail out on non-existent locales to defend against internal errors.
        if locale not in locales or not locales[locale]:
            return localeMutator

        # Handle object lookup notation
        indexOfDot = objectNotation and singular.rindex(objectNotation)
        if objectNotation and indexOfDot > 0 and indexOfDot < len(singular) - 1:
            # If branching wasn't specifically allowed, disable it.
            # This will become the function we want to return.
            accessor = None
            # An accessor that takes one argument and returns null.
            nullAccessor = lambda *args, **kwargs: None
            # Fix object path.
            fixObject = lambda  *args, **kwargs: {}
            # Are we going to need to re-traverse the tree when the mutator is invoked?
            reTraverse = False
            # Split the provided term and run the callback for each subterm.
            def reducer(obj, index):
                # access variables from upper function
                nonlocal accessor, fixObject

                # Make the mutator do nothing.
                accessor = nullAccessor
                # If our current target object (in the locale tree) doesn't exist or
                # it doesn't have the next subterm as a member...
                if obj is None or index not in obj:
                    # ...check if we're allowed to create new branches.
                    if allowBranching:
                        # Fix `object` if `object` is not Object.
                        if obj is None or (type(obj) is not dict and type(obj) is not list):
                            obj = fixObject()
                        # If we are allowed to, create a new object along the path.
                        obj[index] = {}
                    else:
                        # If we aren't allowed, remember that we need to re-traverse later on and...
                        reTraverse = True
                        # ...return null to make the next iteration bail our early on.
                        return None
                # Generate a mutator for the current level.
                def accessor(value):
                    obj[index] = value
                    return value
                # Generate a fixer for the current level.
                def fixObject(*args, **kwargs):
                    obj[index] = {}
                    return obj[index]

                # Return a reference to the next deeper level in the locale tree.
                return obj[index]
            functools.reduce(reducer, singular.split(objectNotation), locales[locale])
            # Return the final mutator.
            def returnAbove(value):
                # If we need to re-traverse the tree
                # invoke the search again, but allow branching
                # this time (because here the mutator is being invoked)
                # otherwise, just change the value directly.
                value = missingKeyFn(locale, value)
                return localeMutator(locale, singular, True)(value) if reTraverse else accessor(value)
            return returnAbove
        else:
            # No object notation, just return a mutator that performs array lookup and changes the value.
            def returnBelow(value):
                value = missingKeyFn(locale, value)
                locales[locale][singular] = value
                return value
            return returnBelow

    def read(locale=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        localeFile = {}
        file = getStorageFilePath(locale)
        with open(file, 'r', encoding='utf-8') as localeFile:
            content = localeFile.read()
            try:
                # parsing filecontents to locales[locale]
                locales[locale] = parser.loads(content) # type: ignore
            except Exception as parseError:
                logError(f'unable to parse locales from file (maybe {file} is empty or invalid json?): ', parseError)
        try:
            logDebug(f'read {file} for locale: {locale}')
        except Exception as readError:
            # unable to read, so intialize that file
            # locales[locale] are already set in memory, so no extra read required
            # or locales[locale] are empty, which initializes an empty locale.json file
            # since the current invalid locale could exist, we should back it up
            if os.path.exists(file):
                logDebug(f'backing up invalid locale {locale} to {file}.invalid')
                os.rename(file, f'{file}.invalid')

            logDebug(f'initializing {file}')
            write(locale)

    def write(locale=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        stats: Any = None
        target: Any = None
        tmp: Any = None

        # don't write new locale information to disk if updateFiles isn't true
        if not updateFiles:
            return

        # creating directory if necessary
        try:
            stats = os.lstat(directory)
        except Exception as e:
            logDebug(f'creating locales dir in: {directory}')
            try:
                if type(directoryPermissions) is int:
                    os.makedirs(directory, mode=directoryPermissions)
                else:
                    os.makedirs(directory)
            except Exception as e:
                # in case of parallel tasks utilizing in same dir
                if isinstance(e, FileExistsError):
                    raise e

        # first time init has an empty file
        if locale not in locales or not locales[locale]:
            locales[locale] = {}

        # writing to tmp and rename on success
        try:
            target = getStorageFilePath(locale)
            tmp = f'{target}.tmp'
            with open(tmp, 'w', encoding='utf-8') as file:
                file.write(parser.dumps(locales[locale], ensure_ascii=False, indent=indent)) # type: ignore
            stats = os.stat(tmp)
            if stats.st_file_attributes == stat.FILE_ATTRIBUTE_ARCHIVE:
                shutil.move(tmp, target)
            else:
                logError(f'unable to write locales to file (either {tmp} or {target} are not writeable?): ')
        except Exception as e:
            logError(f'unexpected error writing files (either {tmp} or {target} are not writeable?): ', e)    

    def getStorageFilePath(locale=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        # changed API to use .json as default, #16
        ext = extension or '.json'
        filepath = os.path.normpath(f'{directory}{pathsep}{prefix}{locale}{ext}')
        filepathJS = os.path.normpath(f'{directory}{pathsep}{prefix}{locale}.js')

        # use .js as fallback if already existing
        try:
            if os.stat(filepathJS):
                logDebug(f'using existing file {filepathJS}')
                extension = '.js'
                return filepathJS
        except Exception as e:
            logDebug(f'will use {filepath}')
        return filepath

    def getFallback(targetLocale=None, fbs=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        fallbacks = fbs or {}
        if targetLocale in fallbacks:
            return fallbacks[targetLocale]
        fallBackLocale = None
        for key in fallbacks:
            if re.match(r'^'+key.replace('*', '.*')+r'$', str(targetLocale)):
                fallBackLocale = fallbacks[key]
                break
        return fallBackLocale

    def logDebug(msg=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        logDebugFn(msg)

    def logWarn(msg=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        logWarnFn(msg)

    def logError(msg=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        logErrorFn(msg)

    def missingKey(locale=None, value=None, *args, **kwargs):
        # access variables from upper function
        nonlocal i18n, MessageformatInstanceForLocale, PluralsForLocale, locales, api, mustacheConfig, mustacheRegex, pathsep, autoReload, cookiename, languageHeaderName, defaultLocale, retryInDefaultLocale, directory, directoryPermissions, extension, fallbacks, indent, logDebugFn, logErrorFn, logWarnFn, preserveLegacyCase, objectNotation, prefix, queryParameter, register, updateFiles, syncFiles, missingKeyFn, parser

        return value

    # implicitly configure when created with given options
    # 
    # i18n = I18n({
    #   'locales': ['en', 'fr']
    # })
    if _OPTS:
        i18n['configure'](_OPTS)

    class I18n(object):
        def __init__(self):
            self.__dict__ = i18n

        @staticmethod
        def configure(opt=_OPTS):
            pass

        @staticmethod
        def init(request, response, next):
            pass

        @staticmethod
        def __(phrase=None, *args, **kwargs):
            pass

        @staticmethod
        def __n(phrase):
            pass

        @staticmethod
        def __l(phrase):
            pass

        @staticmethod
        def __h(phrase):
            pass

        @staticmethod
        def __mf(singular, plural, count):
            pass

        @staticmethod
        def getLocale(obj=None, locale=None, skipImplicitObjects=False):
            pass

        @staticmethod
        def setLocale(request):
            pass

        @staticmethod
        def getCatalog(obj, locale):
            pass

        @staticmethod
        def getLocales():
            pass

        @staticmethod
        def addLocale(locale):
            pass

        @staticmethod
        def removeLocale(locale):
            pass

    return I18n()