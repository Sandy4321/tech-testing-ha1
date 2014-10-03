import unittest
import mock
from notification_pusher import *

class NotificationPusherTestCase(unittest.TestCase):
    def test_create_pidfile_example(self):
        pid = 42
        m_open = mock.mock_open()
        with mock.patch('notification_pusher.open', m_open, create=True):
            with mock.patch('os.getpid', mock.Mock(return_value=pid)):
                create_pidfile('/file/path')

        m_open.assert_called_once_with('/file/path', 'w')
        m_open().write.assert_called_once_with(str(pid))

    def test_daemonize(self):
        fork_mock = mock.Mock(return_value=0)
        with mock.patch('os.fork', fork_mock):
            with mock.patch('os.setsid', mock.Mock(), create=True):
                daemonize()
        fork_mock.assert_called_with()

    def test_parse_cmd_args(self):
        args = '-c /conf -P /pidfile -d'
        args = args.split(' ')
        parsed_args = parse_cmd_args(args)
        self.assertEqual(parsed_args.daemon, True)
        self.assertEqual(parsed_args.config, '/conf')
        self.assertEqual(parsed_args.pidfile, '/pidfile')

    def test_load_config_from_pyfile(self):
        def mocked_execfile(filepath, variables):
            variables = {
                'a': 23,
                'death': 42
            }
            pass

        with mock.patch('__builtin__.execfile', mocked_execfile):
            cfg = load_config_from_pyfile('/test')
        self.assertEqual(cfg.a, 23)