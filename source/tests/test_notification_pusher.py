import unittest
import mock
from Queue import Queue
from notification_pusher import *

class NotificationPusherTestCase(unittest.TestCase):

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
        # self.assertTrue(test1_passed)
        pass