__author__ = 'gumo'
import unittest
from mock import patch, MagicMock

import lib
from lib.__init__ import *

TESTING_CLASS = lib.__init__
DEFAULT_URL = 'http://myurl.com:8080/folder/file.exe'

class LibInitTestCase(unittest.TestCase):

    def test_get_counters_1(self):
        test_res = []
        for counter_name, regex in COUNTER_TYPES:
            test_res.append(counter_name)
        with patch.object(re, 'match', return_value=True):
            self.assertTrue(get_counters("") == test_res)

    def test_get_counters_2(self):
        with patch.object(re, 'match', return_value=False):
            self.assertTrue(get_counters("") == [])

    def test_check_for_meta_1(self):
        result = check_for_meta('<meta http-equiv="refresh" content="SECONDS;NO_URL">', DEFAULT_URL)
        self.assertTrue(result is None)

    def test_check_for_meta_2(self):
        redirect_url = 'http://redirecturl.com:8080/folder/file.exe'
        result = check_for_meta('<meta http-equiv="refresh" content="SECONDS;url=' + redirect_url + '">', DEFAULT_URL)
        self.assertTrue(result == redirect_url)

    def test_check_for_meta_3(self):
        result = check_for_meta('<meta http-equiv="refresh" content="SECONDS;NO_URL;THIRD_ARG">', DEFAULT_URL)
        self.assertTrue(result is None)

    def test_check_for_meta_4(self):
        result = check_for_meta('<non_meta http-equiv="refresh" content="SECONDS;NO_URL">', DEFAULT_URL)
        self.assertTrue(result is None)

    def test_fix_market_url(self):
        self.assertTrue(fix_market_url(DEFAULT_URL) == 'http://play.google.com/store/apps/http://myurl.com:8080/folder/file.exe')
        self.assertTrue(fix_market_url('market://myurl.com:8080/folder/file.exe') == 'http://play.google.com/store/apps/myurl.com:8080/folder/file.exe')

    def test_make_pycurl_request(self):
        mock_curl = pycurl.Curl()
        mock_curl.setopt = MagicMock(return_value=None)
        mock_curl.perform = MagicMock(return_value=None)
        mock_curl.getinfo = MagicMock(return_value=DEFAULT_URL)
        with patch.object(pycurl, 'Curl', return_value=mock_curl):
            result = make_pycurl_request(DEFAULT_URL, 1)
        self.assertTrue(result == ("", DEFAULT_URL))
        mock_curl.perform.assert_called_once_with()

    def test_get_url_1(self):
        with patch.object(TESTING_CLASS, 'make_pycurl_request', side_effect=ValueError):
            result = get_url(DEFAULT_URL, 1)
        self.assertTrue(result == (DEFAULT_URL, 'ERROR', None))

    def test_get_url_2(self):
        url = 'http://odnoklassniki.ru/st.redirect'
        content = 'content'
        with patch.object(TESTING_CLASS, 'make_pycurl_request', return_value=(content, url)):
            result = get_url(url, 1)
        self.assertTrue(result == (None, None, content))

    def test_get_url_3(self):
        url = 'http://myurl.com:8080/folder/file.exe'
        new_url = 'http://mynewurl.com:8080/folder/file.exe'
        content = 'content'
        with patch.object(TESTING_CLASS, 'make_pycurl_request', return_value=(content, None)):
            with patch.object(TESTING_CLASS, 'check_for_meta', return_value=new_url):
                result = get_url(url, None)
        self.assertTrue(result == (new_url, REDIRECT_META, content))

    def test_get_url_4(self):
        url = 'http://myurl.com:8080/folder/file.exe'
        new_url = 'http://mynewurl.com:8080/folder/file.exe'
        content = 'content'
        with patch.object(TESTING_CLASS, 'make_pycurl_request', return_value=(content, new_url)):
            result = get_url(url, None)
        self.assertTrue(result == (new_url, REDIRECT_HTTP, content))

    def test_get_url_5(self):
        url = 'http://myurl.com:8080/folder/file.exe'
        market_url = 'market://myurl.com:8080/folder/file.exe'
        fixed_url = 'http://fixed.com:8080/folder/file.exe'
        content = 'content'
        with patch.object(TESTING_CLASS, 'make_pycurl_request', return_value=(content, market_url)):
            with patch.object(TESTING_CLASS, 'fix_market_url', return_value=fixed_url):
                result = get_url(url, None)
        self.assertTrue(result == (fixed_url, REDIRECT_HTTP, content))

    def test_get_url_6(self):
        url = 'http://myurl.com:8080/folder/file.exe'
        new_url = 'http://mynewurl.com:8080/folder/file.exe'
        content = 'content'
        with patch.object(TESTING_CLASS, 'make_pycurl_request', return_value=(content, None)):
            with patch.object(TESTING_CLASS, 'check_for_meta', return_value=None):
                result = get_url(url, None)
        self.assertTrue(result == (None, None, content))

    def test_redirect_history_ok(self):
        url = "http://www.odnoklassniki.ru/"
        with patch.object(TESTING_CLASS, 'prepare_url', return_value=url):
            result = get_redirect_history(url, 1)
        self.assertTrue(result == ([], [url], []))

    def test_redirect_historyl_mm(self):
        url = "http://my.mail.ru/apps/"
        with patch.object(TESTING_CLASS, 'prepare_url', return_value=url):
            result = get_redirect_history(url, 1)
        self.assertTrue(result == ([], [url], []))

    def test_redirect_history_1(self):
        url = 'http://myurl.com:8080/folder/file.exe'
        with patch.object(TESTING_CLASS, 'get_url', return_value=(None, None, None)):
            result = get_redirect_history(url, 1)
        self.assertTrue(result == ([], [url], []))

    def test_redirect_history_2(self):
        url = 'http://myurl.com:8080/folder/file.exe'
        redirect_url = "redirect.url"
        with patch.object(TESTING_CLASS, 'get_url', return_value=(redirect_url, 'ERROR', None)):
            result = get_redirect_history(url, 1)
        self.assertTrue(result == (['ERROR'], [url, "redirect.url"], []))

    def test_redirect_history_3(self):
        url = 'http://myurl.com:8080/folder/file.exe'
        max_redirects = 1
        redirect_url = "redirect.url"
        redirect_code = 'NOT_ERROR'
        with patch.object(TESTING_CLASS, 'get_url', return_value=(redirect_url, redirect_code, None)):
            result = get_redirect_history(url, 1, max_redirects)
        self.assertTrue(result == ([redirect_code], [url, redirect_url], []))

    def test_redirect_history_4(self):
        url = 'http://myurl.com:8080/folder/file.exe'
        max_redirects = 2
        redirect_url = "redirect.url"
        redirect_code = 'NOT_ERROR'
        with patch.object(TESTING_CLASS, 'get_url', return_value=(redirect_url, redirect_code, None)):
            result = get_redirect_history(url, 1, max_redirects)
        self.assertTrue(result == ([redirect_code, redirect_code], [url, redirect_url, redirect_url], []))

    def test_prepare_url_1(self):
        assert prepare_url(None) is None

    def test_prepare_url_2(self):
        url = 'http://myurl.com:8080/folder/file.exe'
        scheme = 'scheme'
        netloc = 'netloc'
        path = 'path'
        qs = 'qs'
        anchor = 'anchor'
        fragments = 'fragments'
        with patch.object(TESTING_CLASS, 'urlparse', return_value=(scheme, netloc, path, qs, anchor, fragments)):
            result = prepare_url(url)
        self.assertTrue(result == 'scheme://netloc/path;qs?anchor#fragments')

    # def test_prepare_url_3(self):
    #     url = 'http://myurl.com:8080/folder/file.exe'
    #     scheme = 'scheme'
    #     netloc = 'netloc'
    #     path = 'path'
    #     qs = 'qs'
    #     anchor = 'anchor'
    #     fragments = 'fragments'
    #     with patch.object(TESTING_CLASS, 'urlparse', return_value=(scheme, netloc, path, qs, anchor, fragments)):
    #         with patch('lib.__init__.encode', MagicMock(side_effect=UnicodeError)):
    #             result = prepare_url(url)
    #     self.assertTrue(result == 'scheme://netloc/path;qs?anchor#fragments')
