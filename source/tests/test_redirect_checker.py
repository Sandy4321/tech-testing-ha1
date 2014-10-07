import unittest
import mock
from mock import patch, call, Mock

import logging
import os
import sys
from source.lib import utils
from logging.config import dictConfig
from multiprocessing import Process
from multiprocessing import active_children
from time import sleep

from lib.utils import (check_network_status, create_pidfile, daemonize,
                       load_config_from_pyfile, parse_cmd_args, spawn_workers)
from lib.worker import worker

from redirect_checker import (main, main_loop)

class RedirectCheckerTestCase(unittest.TestCase):

    def test_main_loop_1(self):
        config = Mock()
        config.WORKER_POOL_SIZE = 1
        with patch("lib.utils.check_network_status", Mock(return_value=True)):
            with patch("multiprocessing.active_children", Mock(return_value=[])):
                with patch("lib.utils.spawn_workers") as mock_spawn_workers:
                    with patch('time.sleep'):
                        try:
                            main_loop(config)
                        except Exception:
                            pass

        self.assertTrue(mock_spawn_workers.called)

    def test_main_loop_2(self):
        config = Mock()
        config.WORKER_POOL_SIZE = 0
        with patch("lib.utils.check_network_status", Mock(return_value=True)):
            with patch("multiprocessing.active_children", Mock(return_value=[])):
                with patch("lib.utils.spawn_workers", Mock()) as mock_spawn_workers:
                    with patch('time.sleep'):
                        try:
                            main_loop(config)
                        except Exception:
                            pass

        self.assertFalse(mock_spawn_workers.called)

    def test_main_loop_3(self):
        config = Mock()
        config.WORKER_POOL_SIZE = 5
        config.CHECK_URL = True
        config.HTTP_TIMEOUT = 1
        children = [Mock(), Mock(), Mock()]
        with patch("lib.utils.check_network_status", Mock(return_value=False)):
            with patch("multiprocessing.active_children", Mock(return_value=children)):
                with patch('time.sleep'):
                    try:
                        main_loop(config)
                    except Exception:
                        pass
        for c in children:
            c.terminate().assert_called_with()


