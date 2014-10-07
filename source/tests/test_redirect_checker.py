import unittest
import mock
from mock import patch, call, Mock



import os
import sys

import logging
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
        with patch("redirect_checker.check_network_status", Mock(return_value=True)):
            with patch("redirect_checker.active_children", Mock(return_value=[])):
                with patch("redirect_checker.spawn_workers") as mock_spawn_workers:
                    with patch('time.sleep'):
                        try:
                            main_loop(config)
                        except Exception:
                            pass
        mock_spawn_workers.assert_called_once()

    def test_main_loop_2(self):
        config = Mock()
        config.WORKER_POOL_SIZE = 0
        with patch("redirect_checker.check_network_status", Mock(return_value=True)):
            with patch("redirect_checker.active_children", Mock(return_value=[])):
                with patch("redirect_checker.spawn_workers", Mock()) as mock_spawn_workers:
                    with patch('time.sleep'):
                        try:
                            main_loop(config)
                        except Exception:
                            pass

        self.assertFalse(mock_spawn_workers.called)

    def test_main_loop_3(self):
        config = Mock()
        config.WORKER_POOL_SIZE = 5
        children = [Mock(), Mock(), Mock()]

        with patch("redirect_checker.check_network_status", Mock(return_value=False)):
            with patch("redirect_checker.active_children", Mock(return_value=children)):
                with patch('time.sleep'):
                    try:
                        main_loop(config)
                    except Exception:
                        pass
        for c in children:
            c.terminate.assert_called_once_with()


    def test_main_1(self):
        args = '1 -c /conf -d'
        args = args.split(' ')

        conf = Mock()
        conf.LOGGING = {}
        conf.EXIT_CODE = 1222
        with patch("redirect_checker.daemonize") as mock_daemonize:
            with patch("redirect_checker.load_config_from_pyfile", Mock(return_value=conf)):
                with patch("redirect_checker.main_loop") as mock_main_loop:
                    with patch("os.path.realpath"), patch("os.path.expanduser"):
                        with patch("redirect_checker.dictConfig"):
                            self.assertEqual(main(args), 1222)
        mock_main_loop.assert_called_with(conf)
        mock_daemonize.assert_called_with()

    def test_main_2(self):
        args = '1 -c /conf -P /pidfile'
        args = args.split(' ')

        conf = Mock()
        conf.LOGGING = {}
        conf.EXIT_CODE = 1222
        with patch("redirect_checker.create_pidfile") as mock_create_pidfile:
            with patch("redirect_checker.load_config_from_pyfile", Mock(return_value=conf)):
                with patch("redirect_checker.main_loop") as mock_main_loop:
                    with patch("os.path.realpath"), patch("os.path.expanduser"):
                        with patch("redirect_checker.dictConfig"):
                            self.assertEqual(main(args), 1222)
        mock_main_loop.assert_called_with(conf)
        mock_create_pidfile.assert_called_with("/pidfile")
