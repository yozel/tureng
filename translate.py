import json
import hashlib
import requests
from collections import OrderedDict, Callable

class DefaultOrderedDict(OrderedDict):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
           not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                               OrderedDict.__repr__(self))
def get_result(word):
    result = dict()
    m = hashlib.md5()
    m.update("%s46E59BAC-E593-4F4F-A4DB-960857086F9C" % word)
    code = m.hexdigest()
    url = "http://ws.tureng.com/TurengSearchServiceV4.svc/Search"
    data = {"Term": word, "Code": code}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    obj = json.loads(response.text)

    exception_message = obj['ExceptionMessage']
    is_successful = obj['IsSuccessful']

    mobil_results = obj['MobileResult']
    is_found = bool(mobil_results['IsFound'])

    if is_found:
        result_group = DefaultOrderedDict(list)
        for row in mobil_results['Results']:
            result_group[row['CategoryEN']].append(row)
        result['results'] = result_group
        return result
    else:
        result['suggestions'] = mobil_results['Suggestions']
        return result

def run(word=None):
    _word = word if word else raw_input("Translate: ")

    translate_result = get_result(_word)
    if 'suggestions' in translate_result:
        current_suggestion_order = None
        while not current_suggestion_order or current_suggestion_order not in xrange(1, i + 2):
            for i, suggestion in enumerate(translate_result['suggestions']):
                print str(i + 1), "-", suggestion
            current_suggestion_order = int(raw_input("what are you looking for? (1-%s): " % str(i + 1)) or 0)

        _word = translate_result['suggestions'][int(current_suggestion_order) - 1]
        translate_result = get_result(_word)
    
    result_group = translate_result['results']

    print "******** %s ********" % _word
    print ""

    last_language = ''
    for category_en, items in result_group.iteritems():
        tmp_language = category_en[-3:-1]
        if last_language != tmp_language:
            last_language = tmp_language
            if tmp_language == 'en':
                print "English-Ingilizce"
                print "-----------------"
            else:
                print "Turkish-Turkce"
                print "-----------------"

        print "\t%s / %s" % (category_en[:-9], items[0]['CategoryTR'][:-9])
        for item in items:
            my_types = "/".join(filter(lambda x: x!=None, [item['TypeEN'], item['TypeTR']]))
            my_types = (" (%s)" % my_types) if my_types else ""
            print "\t\t%s%s" % (item['Term'], my_types)

run()