import unittest
import mock
from Queue import Queue
from notification_pusher import *

class NotificationPusherTestCase(unittest.TestCase):

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

    def test_done_with_processed_tasks(self):
        test1_passed = False
        class test1:
            task_id = 4
            def test1_method(self):
                test1_passed = True

        queue = Queue()
        t = test1()
        queue.put_nowait((t, 'test1_method'))
        done_with_processed_tasks(queue)
        self.assertTrue(test1_passed)
