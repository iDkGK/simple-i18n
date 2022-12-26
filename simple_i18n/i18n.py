class I18n(object):
    def __init__(self, _OPTS=False):
        self.messageformatinstanceforlocale = {}
        self.pluralsforlocale = {}
        self.locales = {}
        self.mustacheconfig = {
            'tags': ['{{', '}}'],
            'disable': False
        }

    def configure(self, opt):
        pass

    def init(self, request, response, next):
        pass

    def __(self, phrase):
        pass

    def __mf(self, phrase):
        pass

    def __l(self, phrase):
        pass

    def __h(self, phrase):
        pass

    def __n(self, singular, plural, count):
        pass

    def setLocale(self, object, locale, skipImplicitObjects):
        pass

    def getLocale(self, request):
        pass

    def getCatalog(self, object, locale):
        pass

    def getLocales(self):
        pass

    def addLocale(self, locale):
        pass

    def removeLocale(self, locale):
        pass