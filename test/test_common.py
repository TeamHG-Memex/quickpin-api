# -*- coding: utf-8 -*-
"""
Authentication tests.
"""
import unittest

from getpass import getpass


class TestCommon(unittest.TestCase):
    app_url = input('App URL: ')
    username = input('Username: ')
    password = getpass()
    token_length = 56
