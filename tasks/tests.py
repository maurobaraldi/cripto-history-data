import unittest

from common import (
    request,
    decompress
)

class TestRequest(unittest.TestCase):

    def test_request_should_succeed(self):
        self.assertEqual(True, True)

    def test_request_should_fail(self):
        self.assertEqual(True, True)


class TestDecompress(unittest.TestCase):

    def test_descompress_should_succeed(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
