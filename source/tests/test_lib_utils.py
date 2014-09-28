__author__ = 'gumo'
import unittest
import mock

from lib.utils import (create_pidfile, parse_cmd_args, get_tube)

class LibUtilsTestCase(unittest.TestCase):
    def test_create_pidfile_example(self):
        pid = 42
        m_open = mock.mock_open()
        with mock.patch('lib.utils.open', m_open, create=True):
            with mock.patch('os.getpid', mock.Mock(return_value=pid)):
                create_pidfile('/file/path')

        m_open.assert_called_once_with('/file/path', 'w')
        m_open().write.assert_called_once_with(str(pid))

    def test_parse_cmd_args(self):
        cfg = '/test'
        pid = '/pid'
        args = parse_cmd_args(['-c', cfg, '-P', pid], 'test')
        self.assertTrue(args.config == cfg)
        self.assertTrue(args.pidfile == pid)
        self.assertFalse(args.daemon)

"""
    def test_get_tube(self):
        host = 'host'
        port = 'port'
        space = 'space'
        name = 'name'
        with mock.patch('tarantool_queue.Queue', 'tube', return_value='') as mock_queue:
            get_tube(host, port, space, name)
        mock_queue.assert_called_once_with(name)
"""

