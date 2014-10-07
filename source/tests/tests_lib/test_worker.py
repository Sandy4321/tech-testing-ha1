__author__ = 'gumo'

import unittest
from mock import patch, MagicMock, call

from lib.worker import *
import lib.worker

DEFAULT_URL = 'http://myurl.com:8080/folder/file.exe'


class Task:
    pass


class LibWorkerTestCase(unittest.TestCase):
    def test_get_redirect_history_from_task_1(self):
        task = Task()
        task.data = {'url': DEFAULT_URL, 'not_recheck': 'not_recheck', 'url_id': 2}
        final_data = {'url': DEFAULT_URL, 'not_recheck': 'not_recheck', 'url_id': 2,
                      'recheck': True}
        task.task_id = 1
        # with patch.object(logger, 'info', return_value=None):
        with patch.object(lib.worker, 'get_redirect_history', return_value=(['ERROR'], [], [])):
            result = get_redirect_history_from_task(task, 1)
        self.assertTrue(result == (True, final_data))

    def test_get_redirect_history_from_task_2(self):
        task = Task()
        url_id = 2
        task.data = {'url': DEFAULT_URL, 'not_recheck': 'not_recheck', 'url_id': + url_id}
        res = [[], [], []]
        final_data = {
            "url_id": url_id,
            "result": res,
            "check_type": "normal"
        }
        task.task_id = 1
        with patch.object(logger, 'info', return_value=None):
            with patch.object(lib.worker, 'get_redirect_history', return_value=res):
                result = get_redirect_history_from_task(task, 1)
        self.assertTrue(result == (False, final_data))

    def test_get_redirect_history_from_task_3(self):
        task = Task()
        url_id = 2
        suspicious = 'suspicious'
        task.data = {
            'url': DEFAULT_URL,
            'not_recheck': 'not_recheck',
            'url_id': + url_id,
            'suspicious': suspicious
        }
        res = [[], [], []]
        final_data = {
            "url_id": url_id,
            "result": res,
            "check_type": "normal",
            'suspicious': 'suspicious'
        }
        task.task_id = 1
        with patch.object(logger, 'info', return_value=None):
            with patch.object(lib.worker, 'get_redirect_history', return_value=res):
                result = get_redirect_history_from_task(task, 1)
        self.assertTrue(result == (False, final_data))

    def test_worker_1(self):
        config = MagicMock()
        tube = MagicMock()
        tube.opt = {'tube': 'tube_name'}
        tube.take = MagicMock(return_value=None)
        with patch('lib.worker.get_tube', MagicMock(return_value=tube)):
            with patch.object(logger, 'info', return_type=None) as mock_logger:
                with patch('lib.worker.os.path.exists', MagicMock(side_effect=(True, False))):
                    worker(config, 1)
        mock_logger.assert_has_calls([
            call(u'Connected to input queue server on {host}:{port} space #{space}. name={name}'.format(
                host=tube.queue.host,
                port=tube.queue.port,
                space=tube.queue.space,
                name=tube.opt['tube']
            )),
            call(u'Connected to output queue server on {host}:{port} space #{space} name={name}.'.format(
                host=tube.queue.host,
                port=tube.queue.port,
                space=tube.queue.space,
                name=tube.opt['tube']
            )),
            call('Parent is dead. exiting')
        ])

    def test_worker_2(self):
        config = MagicMock()
        tube = MagicMock()
        tube.opt = {'tube': 'tube_name'}
        task = MagicMock()
        pri = 'pri'
        task.meta = MagicMock(return_value={'pri': pri})
        task.ack = MagicMock(return_value=None)
        task.task_id = MagicMock(return_value=1)
        tube.take = MagicMock(return_value=task)
        data = []
        with patch('lib.worker.get_tube', MagicMock(return_value=tube)):
            with patch.object(logger, 'info', return_type=None):
                with patch('lib.worker.os.path.exists', MagicMock(side_effect=(True, False))):
                    with patch('lib.worker.get_redirect_history_from_task', MagicMock(return_value=(True, data))):
                        worker(config, 1)
        tube.put.assert_called_once_with(data, delay=config.RECHECK_DELAY, pri=pri)
        task.ack.assert_called_once_with()

    def test_worker_3(self):
        config = MagicMock()
        tube = MagicMock()
        tube.opt = {'tube': 'tube_name'}
        task = MagicMock()
        pri = 'pri'
        task.meta = MagicMock(return_value={'pri': pri})
        task.ack = MagicMock(return_value=None)
        task.task_id = MagicMock(return_value=1)
        tube.take = MagicMock(return_value=task)
        with patch('lib.worker.get_tube', MagicMock(return_value=tube)):
            with patch.object(logger, 'info', return_type=None) as mock_logger:
                with patch('lib.worker.os.path.exists', MagicMock(side_effect=(True, True,False))):
                    with patch('lib.worker.get_redirect_history_from_task', MagicMock(return_value=None)):
                        worker(config, 1)
        task.ack.assert_called_with()
        assert not tube.put.called

    def test_worker_4(self):
        config = MagicMock()
        tube = MagicMock()
        tube.opt = {'tube': 'tube_name'}
        task = MagicMock()
        pri = 'pri'
        task.meta = MagicMock(return_value={'pri': pri})
        task.ack = MagicMock(return_value=None)
        task.task_id = MagicMock(return_value=1)
        tube.take = MagicMock(return_value=task)
        data = []
        with patch('lib.worker.get_tube', MagicMock(return_value=tube)):
            with patch.object(logger, 'info', return_type=None):
                with patch('lib.worker.os.path.exists', MagicMock(side_effect=(True, False))):
                    with patch('lib.worker.get_redirect_history_from_task', MagicMock(return_value=(None, data))):
                        worker(config, 1)
        tube.put.assert_called_once_with(data)
        task.ack.assert_called_once_with()

    def test_worker_5(self):
        config = MagicMock()
        tube = MagicMock()
        tube.opt = {'tube': 'tube_name'}
        task = MagicMock()
        pri = 'pri'
        task.meta = MagicMock(return_value={'pri': pri})
        task.ack = MagicMock(side_effect=DatabaseError)
        task.task_id = MagicMock(return_value=1)
        tube.take = MagicMock(return_value=task)
        data = []
        with patch('lib.worker.get_tube', MagicMock(return_value=tube)):
            with patch.object(logger, 'info', return_type=None) as mock_logger:
                with patch('lib.worker.os.path.exists', MagicMock(side_effect=(True, False))):
                    with patch('lib.worker.get_redirect_history_from_task', MagicMock(return_value=(True, data))):
                        worker(config, 1)
        task.ack.assert_called_once_with()
        mock_logger.assert_has_calls([call('Task ack fail'), call('Parent is dead. exiting')])