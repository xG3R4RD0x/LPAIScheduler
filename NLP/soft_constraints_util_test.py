from typing import Any, NoReturn
import unittest
import soft_constraints_util as scu


class SoftConstraintsTest(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_extract_dates(self):
        date_list = [['July 15th', 'July 20th'], 'july 25th']
        response = scu.extract_dates(date_list)
        print("test_extract_dates")
        print(response)
        self.assertTrue(type(response), list)


if __name__ == '__main__':
    unittest.main()
