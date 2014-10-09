import unittest
import mock
from mock import patch, call, Mock, MagicMock

import signal
import gevent
import tarantool
import tarantool_queue
from gevent import queue as gevent_queue

import notification_pusher
from notification_pusher import *



class NotificationPusherTestCase(unittest.TestCase):

    def test_done_with_processed_tasks(self):
        class test:
            task_id = 123456
            def test_method(self):
                pass

        queue = gevent_queue.Queue()
        t = test()
        queue.put_nowait((t, 'test_method'))
        with patch.object(t, 'test_method', return_value=None) as meth_mock:
            done_with_processed_tasks(queue)
        meth_mock.assert_called_with()

    def test_stop_handler(self):
        global run_application
        global exit_code
        run_application = True
        exit_code = 0
        signum = 34

        stop_handler(signum)
        
        self.assertFalse(notification_pusher.run_application)
        self.assertEqual(notification_pusher.exit_code, SIGNAL_EXIT_CODE_OFFSET + signum)

    def test_install_signal_handlers(self):
        with patch('gevent.signal', mock.Mock(), create=True) as signal_mock:
            install_signal_handlers()

        signal_mock.assert_any_call(signal.SIGQUIT, stop_handler, signal.SIGQUIT)
        signal_mock.assert_any_call(signal.SIGTERM, stop_handler, signal.SIGTERM)
        signal_mock.assert_any_call(signal.SIGINT, stop_handler, signal.SIGINT)
        signal_mock.assert_any_call(signal.SIGHUP, stop_handler, signal.SIGHUP)
        
    def test_notification_worker_ack(self):

        task = MagicMock(name="tarantool_queue.Task")
        task.task_id = 1
        task.data = {
            "callback_url": "/testURL"
        }
        task_queue = MagicMock(name="task_queue")

        with patch('requests.post', Mock(return_value=Mock(name="response"))):
            notification_worker(task, task_queue)
        task_queue.put.assert_called_with((task, 'ack'))

    def test_notification_worker_bury(self):

        task = MagicMock(name="tarantool_queue.Task")
        task.task_id = 1
        task.data = {
            "callback_url": "/testURL"
        }
        task_queue = MagicMock(name="task_queue")

        with patch('requests.post', Mock(side_effect=requests.RequestException)):
            notification_worker(task, task_queue)
        task_queue.put.assert_called_with((task, 'bury'))
        
    def test_main_1(self):
        args = '1 -c /conf -d'
        args = args.split(' ')

        notification_pusher.run_application = False
        notification_pusher.exit_code = 1111

        conf = Mock()
        conf.LOGGING = {}
        with patch("notification_pusher.daemonize") as mock_daemonize:
            with patch("notification_pusher.load_config_from_pyfile", Mock(return_value=conf)):
                with patch("os.path.realpath"), patch("os.path.expanduser"):
                    with patch("notification_pusher.dictConfig"):
                        self.assertEqual(main(args), 1111)

        mock_daemonize.assert_called_with()

    def test_main_2(self):
        args = '1 -c /conf -P /pidfile'
        args = args.split(' ')

        notification_pusher.run_application = False
        notification_pusher.exit_code = 1111

        conf = Mock()
        conf.LOGGING = {}
        with patch("notification_pusher.create_pidfile") as mock_create_pidfile:
            with patch("notification_pusher.load_config_from_pyfile", Mock(return_value=conf)):
                with patch("os.path.realpath"), patch("os.path.expanduser"):
                    with patch("notification_pusher.dictConfig"):
                        self.assertEqual(main(args), 1111)

        mock_create_pidfile.assert_called_with('/pidfile')

    @patch('notification_pusher.patch_all', Mock())
    def test_main_3(self):
        def main_loop_mocked(conf):
            notification_pusher.run_application = False

        args = '1 -c /conf'
        args = args.split(' ')

        notification_pusher.run_application = True
        notification_pusher.exit_code = 1111

        conf = Mock()
        conf.LOGGING = {}

        with patch("notification_pusher.load_config_from_pyfile", Mock(return_value=conf)):
            with patch("notification_pusher.main_loop", Mock(side_effect=main_loop_mocked)) as mock_main_loop:
                with patch("os.path.realpath"), patch("os.path.expanduser"):
                    with patch("notification_pusher.dictConfig"):
                        self.assertEqual(main(args), 1111)

        mock_main_loop.assert_called_with(conf)

    @patch('notification_pusher.patch_all', Mock())
    def test_main_4(self):
        def main_loop_mocked(conf):
            notification_pusher.run_application = False
            raise Exception()

        args = '1 -c /conf'
        args = args.split(' ')

        notification_pusher.run_application = True
        notification_pusher.exit_code = 1111

        conf = Mock()
        conf.LOGGING = {}
        conf.SLEEP_ON_FAIL = 1

        with patch("notification_pusher.load_config_from_pyfile", Mock(return_value=conf)):
            with patch("notification_pusher.main_loop", Mock(side_effect=main_loop_mocked)) as mock_main_loop:
                with patch("os.path.realpath"), patch("os.path.expanduser"):
                    with patch("notification_pusher.dictConfig"):
                        with patch("notification_pusher.sleep") as mock_sleep:
                            self.assertEqual(main(args), 1111)

        mock_main_loop.assert_called_with(conf)
        mock_sleep.assert_called_with(conf.SLEEP_ON_FAIL)

    def test_main_loop_1(self):
        mock_queue = Mock()
        mock_worker_pool = Mock()
        # mock_tube_queue = Mock()
        # mock_queue.tube = mock_tube_queue

        config = Mock()
        config.WORKER_POOL_SIZE = 1
        config.QUEUE_TUBE = "TUBE"

        notification_pusher.run_application = False

        with patch('notification_pusher.tarantool_queue.Queue', Mock(return_value=mock_queue)):
            with patch('notification_pusher.Pool', Mock(return_value=mock_worker_pool)) as mock_Pool:
                main_loop(config)

        mock_Pool.assert_called_with(config.WORKER_POOL_SIZE)
        mock_queue.tube.assert_called(config.QUEUE_TUBE)

    def test_main_loop_2(self):
        def sleep_mocked(time):
            notification_pusher.run_application = False

        mock_task = Mock()
        mock_task.task_id.return_value = 1

        mock_queue = Mock()
        mock_tube = Mock()
        mock_queue.tube.return_value = mock_tube
        mock_tube.take.return_value = mock_task

        mock_worker_pool = Mock()
        mock_worker_pool.free_count.return_value = 3

        mock_worker = Mock()

        config = Mock()
        config.WORKER_POOL_SIZE = 1
        config.QUEUE_TUBE = "TUBE"

        notification_pusher.run_application = True

        with patch('notification_pusher.tarantool_queue.Queue', Mock(return_value=mock_queue)):
            with patch('notification_pusher.Pool', Mock(return_value=mock_worker_pool)) as mock_Pool:
                with patch('notification_pusher.Greenlet', Mock(return_value=mock_worker)):
                    with patch('notification_pusher.done_with_processed_tasks') as mock_done_with_processed_tasks:
                        with patch('notification_pusher.sleep', Mock(side_effect=sleep_mocked)):
                            main_loop(config)

        self.assertTrue(mock_done_with_processed_tasks.called)
        mock_worker.start.has_calls([call(), call(), call()])