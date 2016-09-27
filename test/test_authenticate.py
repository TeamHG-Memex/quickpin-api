# -*- coding: utf-8 -*-
"""
Authentication tests.
"""
import unittest

from .test_common import TestCommon
from quickpin_api.qpi import QPI


class AuthenticateTest(TestCommon):
    """
    Test authentication.
    """

    def assertIsToken(self, token):
        """
        Assert that token is string of correct length.
        """
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), self.token_length)

    def test_get_token(self):
        """
        Test that a token can be obtained.
        """
        qpi = QPI(app_url=self.app_url, username=self.username,
                  password=self.password)

        self.assertIsToken(qpi.token, self.token_length)
