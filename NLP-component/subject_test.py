import unittest


from subject import Subject


class SubjectTest(unittest.TestCase):
    def test_subject(self):
        test_subject = Subject("Math")
        print(test_subject)
        self.assertTrue(type(test_subject), Subject)


if __name__ == '__main__':
    unittest.main()
