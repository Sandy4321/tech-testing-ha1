import unittest
import mock
from mock import patch, call

import signal
import gevent
import tarantool
import tarantool_queue
from gevent import queue as gevent_queue

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
        
        # self.assertFalse(run_application)
        # self.assertEqual(exit_code, SIGNAL_EXIT_CODE_OFFSET + signum)

    def test_install_signal_handlers(self):
        with mock.patch('gevent.signal', mock.Mock(), create=True) as signal_mock:
            install_signal_handlers()

        signal_mock.assert_any_call(signal.SIGQUIT, stop_handler, signal.SIGQUIT)
        signal_mock.assert_any_call(signal.SIGTERM, stop_handler, signal.SIGTERM)
        signal_mock.assert_any_call(signal.SIGINT, stop_handler, signal.SIGINT)
        signal_mock.assert_any_call(signal.SIGHUP, stop_handler, signal.SIGHUP)
        
    def test_notification_worker_ack(self):

        task = mock.MagicMock(name="tarantool_queue.Task")
        task.task_id = 1
        task.data = {
            "callback_url": "/testURL"
        }
        task_queue = mock.MagicMock(name="task_queue")

        with mock.patch('requests.post', mock.Mock(return_value=mock.Mock(name="response"))):
            notification_worker(task, task_queue)
        task_queue.put.assert_called_with((task, 'ack'))

    def test_notification_worker_bury(self):

        task = mock.MagicMock(name="tarantool_queue.Task")
        task.task_id = 1
        task.data = {
            "callback_url": "/testURL"
        }
        task_queue = mock.MagicMock(name="task_queue")

        with mock.patch('requests.post', mock.Mock(side_effect=requests.RequestException)):
            notification_worker(task, task_queue)
        task_queue.put.assert_called_with((task, 'bury'))
        
        

