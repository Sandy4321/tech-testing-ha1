__author__ = 'gumo'
import unittest
import mock
from mock import patch, call, Mock
import exceptions
from random import randrange

from lib.utils import *


class LibUtilsTestCase(unittest.TestCase):

    def test_daemonize_1(self):
        fork_mock = mock.Mock(return_value=0)
        with mock.patch('os.fork', fork_mock):
            with mock.patch('os.setsid', mock.Mock(), create=True):
                daemonize()
        fork_mock.assert_called_with()

    def test_daemonize_2(self):
        with patch.object(os, 'fork', return_value=None):
            with patch.object(os, '_exit', create=True) as mock_exit:
                daemonize()
        mock_exit.assert_called_once_with(0)

    # def test_daemonize_3(self):
    #     with patch('os.fork', Mock(side_effect=(0, 1))) as fork_mock:
    #         with mock.patch('os.setsid', mock.Mock(), create=True) as fork_setsid:
    #             daemonize()
    #     fork_mock.assert_called_with()
    #     fork_setsid.assert_called_once_with()

    def execfile_patch(self, filepath, varaibles):
        varaibles['UPPER_CASE'] = 'UPPER_CASE_VALUE'
        varaibles['lover_case'] = 'lover_case_value'
        varaibles['UPPER_lover_CaSe'] = 'UPPER_lover_CaSe'

    def test_load_config_from_pyfile(self):
        with patch('__builtin__.execfile', side_effect=self.execfile_patch):
            result = load_config_from_pyfile('filepath')
        self.assertTrue(result.UPPER_CASE == 'UPPER_CASE_VALUE')
        self.assertFalse(hasattr(result, 'lover_case'))
        self.assertFalse(hasattr(result, 'UPPER_lover_CaSe'))

    def test_create_pidfile_example(self):
        pid = 42
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

    def test_parse_cmd_args_2(self):
        args = '-c /conf -P /pidfile -d'
        args = args.split(' ')
        parsed_args = parse_cmd_args(args)
        self.assertEqual(parsed_args.daemon, True)
        self.assertEqual(parsed_args.config, '/conf')
        self.assertEqual(parsed_args.pidfile, '/pidfile')

    def test_get_tube(self):
        host = 'host'
        port = 42
        space = 322
        name = 'name'
        with patch.object(tarantool_queue.Queue, 'tube', return_value=None) as mock_queue:
            get_tube(host, port, space, name)
        mock_queue.assert_called_once_with(name)

    def test_spawn_workers(self):
        num = 42
        target = 'target'
        args = ['', '']
        parent_id = 1
        with patch.object(Process, 'start', return_value=None) as mock_process:
            spawn_workers(num, target, args, parent_id)
        calls = []
        for _ in range(0, num, 1):
            calls.append(call())
        mock_process.assert_has_calls(calls)
        mock_process.asert_called_with()

    def test_check_network_status_1(self):
        with patch('urllib2.urlopen', return_value=None):
            result = check_network_status("", 0)
        self.assertTrue(result)

    def test_check_network_status_2(self):
        with patch('urllib2.urlopen', side_effect=socket.error):
            result = check_network_status("", 0)
        self.assertFalse(result)