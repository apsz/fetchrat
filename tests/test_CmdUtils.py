#!/usr/bin/python3


import unittest
import unittest.mock
import CmdUtils


class TestCmdUtils(unittest.TestCase):

    def setUp(self):
        self.all_defaults = ('string')
        self.all_defaults_no_message = (None)
        self.valid_given = ('string', map(str, list(range(10))))
        self.default_given = ('string', '10')
        self.min_max_given = ('string', 10, 20)

    # get_str
    @unittest.mock.patch('CmdUtils.get_input', return_value='test_string')
    def test_str_defaults_normal_msg(self, input):
        self.assertEquals(CmdUtils.get_str(msg=self.all_defaults[0]), 'test_string')

    @unittest.mock.patch('CmdUtils.get_input', return_value='test_string')
    def test_str_defaults_no_msg(self, input):
        with self.assertRaises(TypeError):
            self.assertEquals(CmdUtils.get_str(msg=self.all_defaults_no_message[0]),
                              'test_string')

    @unittest.mock.patch('CmdUtils.get_input', return_value='6')
    def test_str_valid_range(self, input):
        self.assertEquals(CmdUtils.get_str(msg=self.valid_given[0],
                                           valid=self.valid_given[1]), '6')

    @unittest.mock.patch('CmdUtils.get_input', return_value='')
    def test_str_default_given(self, input):
        self.assertEquals(CmdUtils.get_str(msg=self.default_given[0],
                                           default=self.default_given[1]), '10')

    @unittest.mock.patch('CmdUtils.get_input', return_value='test_string')
    def test_str_min_max_given(self, input):
        self.assertEquals(CmdUtils.get_str(msg=self.min_max_given[0],
                                           min_len=self.min_max_given[1],
                                           max_len=self.min_max_given[2]), 'test_string')

    # get_int
    @unittest.mock.patch('CmdUtils.get_input', return_value=0)
    def test_int_defaults_normal_msg(self, input):
        self.assertEquals(CmdUtils.get_int(msg=self.all_defaults[0]), 0)

    @unittest.mock.patch('CmdUtils.get_input', return_value=0)
    def test_int_defaults_no_msg(self, input):
        with self.assertRaises(TypeError):
            self.assertEquals(CmdUtils.get_int(msg=self.all_defaults_no_message[0]),
                              'test_string')

    @unittest.mock.patch('CmdUtils.get_input', return_value='')
    def test_int_valid_range(self, input):
        self.assertEquals(CmdUtils.get_int(msg=self.default_given[0],
                                           default=int(self.default_given[1])), 10)

    @unittest.mock.patch('CmdUtils.get_input', return_value='')
    def test_int_default_given(self, input):
        self.assertEquals(CmdUtils.get_int(msg=self.default_given[0],
                                           default=self.default_given[1]), '10')

    @unittest.mock.patch('CmdUtils.get_input', return_value=12)
    def test_int_min_max_given(self, input):
        self.assertEquals(CmdUtils.get_int(msg=self.min_max_given[0],
                                           min_val=self.min_max_given[1],
                                           max_val=self.min_max_given[2]), 12)


if __name__ == '__main__':
    unittest.main()