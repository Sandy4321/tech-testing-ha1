__author__ = 'gumo'
import unittest
import mock
from mock import patch, call

from tarantool_queue import tarantool_queue
from multiprocessing import Process
from random import randrange

from lib.utils import *


RANDOM_INT_OFFSET = 10000

class LibUtilsTestCase(unittest.TestCase):
    def test_create_pidfile_example(self):
        pid = randrange(RANDOM_INT_OFFSET)
        m_open = mock.mock_open()
        with mock.patch('lib.utils.open', m_open, create=True):
            with mock.patch('os.getpid', mock.Mock(return_value=pid)):
                create_pidfile('/file/path')

        m_open.assert_called_once_with('/file/path', 'w')
        m_open().write.assert_called_once_with(str(pid))

    def test_parse_cmd_args_1(self):
        cfg = '/test'
        pid = '/pid'
        args = parse_cmd_args(['-c', cfg, '-P', pid], 'test')
        self.assertTrue(args.config == cfg)
        self.assertTrue(args.pidfile == pid)
        self.assertFalse(args.daemon)


    def test_get_tube(self):
        host = 'host'
        port = randrange(RANDOM_INT_OFFSET)
        space = randrange(RANDOM_INT_OFFSET)
        name = 'name'
        with patch.object(tarantool_queue.Queue, 'tube', return_value=None) as mock_queue:
            get_tube(host, port, space, name)
        mock_queue.assert_called_once_with(name)

    def test_spawn_workers(self):
        num = randrange(RANDOM_INT_OFFSET)
        target = 'target'
        args = ['', '']
        parent_id = 1
        with patch.object(Process, 'start', return_value=None) as mock_process:
            spawn_workers(num, target, args, parent_id)
        for _ in range(0, num, 1):
            calls = []
            calls.append(call())
        mock_process.assert_has_calls(calls)
        mock_process.asert_called_with()