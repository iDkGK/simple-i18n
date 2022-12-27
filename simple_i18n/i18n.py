__author__ = 'Created by iDkGK <1444807655@qq.com> on 2022-12-27'
__link__ = 'https://github.com/iDkGK/simple-i18n'
__license__ = 'https://www.freebsd.org/copyright/freebsd-license/'
__version__ = '0.1.0'

# dependencies
import os
import re
from typing import (
    Any,
    overload
)
from types import FunctionType

# utils
escapeRegExp = lambda string: re.sub(r'[.*+?^${}()|[\]\\]', lambda substring: '\\{}'.format(substring.group(0)), string)

# create constructor function
def I18n(_OPTS=False):
    MessageformatInstanceForLocale = {}
    PluralsForLocale = {}
    locales = {}
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
    mustacheConfig = {
        'tags': ['{{', '}}'],
        'disable': False
    }
    mustacheRegex: Any
    pathsep = os.path.sep
    autoReload: Any
    cookiename: Any
    languageHeaderName: Any
    defaultLocale: Any
    retryInDefaultLocale: Any
    directory: Any
    directoryPermissions: Any
    extension: Any
    fallbacks: Any
    indent: Any
    logDebugFn: Any
    logErrorFn: Any
    logWarnFn: Any
    preserveLegacyCase: Any
    objectNotation: Any
    prefix: Any
    queryParameter: Any
    register: Any
    updateFiles: Any
    syncFiles: Any
    missingKeyFn: Any
    parser: Any

    # public exports
    class I18n(object):
        pass
    i18n = I18n()

    i18n.version = '0.1.0'

    def i18nConfigure(opt):
        # access variables from upper function
        nonlocal locales, api, register, cookiename, languageHeaderName, queryParameter, directory, directoryPermissions, updateFiles, syncFiles, indent, prefix, extension, defaultLocale, retryInDefaultLocale, autoReload, objectNotation, fallbacks, logDebugFn, logWarnFn, logErrorFn, preserveLegacyCase, missingKeyFn, parser

        # reset locales
        locales = {}

        # Provide custom API method aliases if desired
        # This needs to be processed before the first call to applyAPItoObject()
        if 'api' in opt and type(opt['api']) is dict:
            for method in opt['api']:
                alias = opt[api][method]
                if method in api:
                    api[method] = alias

        # you may register i18n in global scope, up to you
        if 'register' in opt and type(opt['register']) is dict:
            register = opt['register']
            # or give an array objects to register to
            if type(opt['register']) is list:
                register = opt['register']
                register = [applyAPItoObject(method) for method in register]
            else:
                applyAPItoObject(opt['register'])

        # sets a custom cookie name to parse locale settings from
        cookiename = opt['cookie'] if 'cookie' in opt and type(opt['cookie']) is str else None

        #set the custom header name to extract the language locale
        languageHeaderName = opt['header'] if 'header' in opt and type(opt['header']) is str else 'accept-language'

        #query-string parameter to be watched - @todo: add test & doc
        queryParameter = opt['queryParameter'] if 'queryParameter' in opt and type(opt['queryParameter']) is str else None

        #where to store json files
        directory = opt['directory'] if 'directory' in opt and type(opt['directory']) is str else os.path.join(os.getcwd(), 'locales')

        #permissions when creating new directories
        directoryPermissions = int(opt['directoryPermissions'], 8) if 'directoryPermissions' in opt and type(opt['directoryPermissions']) is str else None

        #write new locale information to disk
        updateFiles = opt['updateFiles'] if 'updateFiles' in opt and type(opt['updateFiles']) is bool else True

        #sync locale information accros all files
        syncFiles = opt['syncFiles'] if 'syncFiles' in opt and type(opt['syncFiles']) is bool else False

        #what to use as the indentation unit (ex: "\t", "  ")
        indent = opt['indent'] if 'indent' in opt and type(opt['indent']) is str else '\t'

        #json files prefix
        prefix = opt['prefix'] if 'prefix' in opt and type(opt['prefix']) is str else ''

        #where to store json files
        extension = opt['extension'] if 'extension' in opt and type(opt['extension']) is str else '.json'

        #setting defaultLocale
        defaultLocale = opt['defaultLocale'] if 'defaultLocale' in opt and type(opt['defaultLocale']) is str else 'en'

        #allow to retry in default locale, useful for production
        retryInDefaultLocale = opt['retryInDefaultLocale'] if 'retryInDefaultLocale' in opt and type(opt['retryInDefaultLocale']) is bool else False

        #auto reload locale files when changed
        autoReload = opt['autoReload'] if 'autoReload' in opt and type(opt['autoReload']) is bool else False

        #enable object notation?
        objectNotation = opt['objectNotation'] if 'objectNotation' in opt else False
        if objectNotation == True:
            objectNotation = '.'

        #read language fallback map
        fallbacks = opt['fallbacks'] if 'fallbacks' in opt and type(opt['fallbacks']) is dict else {}

        #setting custom logger functions
        logDebugFn = opt['logDebugFn'] if 'logDebugFn' in opt and type(opt['logDebugFn']) is FunctionType else None
        logWarnFn = opt['logWarnFn'] if 'logWarnFn' in opt and type(opt['logWarnFn']) is FunctionType else None
        logErrorFn = opt['logErrorFn'] if 'logErrorFn' in opt and type(opt['logErrorFn']) is FunctionType else None
        preserveLegacyCase = opt['preserveLegacyCase'] if 'preserveLegacyCase' in opt and type(opt['preserveLegacyCase']) is bool else True

        #setting custom missing key function
        missingKeyFn = opt['missingKeyFn'] if 'missingKeyFn' in opt and type(opt['missingKeyFn']) is FunctionType else missingKeyFn
        parser = opt['cookie'] if 'cookie' in opt and type(opt['cookie']) is str else None

        #when missing locales we try to guess that from directory


        #some options should be disabled when using staticCatalog


        #customize mustache parsing


        #implicitly read all locales


    i18n.configure = i18nConfigure

    # ===================
    # = private methods =
    # ===================

    def postProcess(msg, namedValues, args, count):
        pass

    def argsEndWithNamedObject(args):
        pass

    def parseArgv(args):
        pass

    def applyAPItoObject(object):
        pass

    def guessLocales(directory):
        pass

    def guessLocaleFromFile(filename):
        pass

    def extractQueryLanguage(queryLanguage):
        pass

    def guessLanguage(request):
        pass

    def getAcceptedLanguagesFromHeader(header):
        pass

    def getLocaleFromObject(obj):
        pass

    def parsePluralInterval(phrase, count):
        pass

    def matchInterval(number, interval):
        pass

    def translate(locale, singular, plural, skipSyncToAllFiles):
        pass

    def syncToAllFiles(singular, plural):
        pass

    def localeAccessor(locale, singular, allowDelayedTraversal):
        pass

    def localeMutator(locale, singular, allowBranching):
        pass

    def read(locale):
        pass

    def write(locale):
        pass

    def getStorageFilePath(locale):
        pass

    def getFallback(targetLocale, fallbacks):
        pass

    def logDebug(msg):
        pass

    def logWarn(msg):
        pass

    def logError(msg):
        pass

    def missingKey(locale, value):
        pass

    if _OPTS:
        i18n.configure(_OPTS)

    return i18n