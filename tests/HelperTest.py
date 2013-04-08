__author__ = 'OT Chen'
import unittest
import helper
import tempfile
import os

class HelperTest(unittest.TestCase):
    def test_load_variables(self):
        tmpdir_path = tempfile.mktemp()
        filepath = os.path.join( tmpdir_path, 'test_load_variables.py')
        lines = []
        lines.append('a=1')
        lines.append('b="string"')
        lines.append('c=[1,2,3,4]')
        lines.append('d={"key":"value"}')
        with open(filepath,'w') as f:
            f.writelines(lines)
        expected_variable = {
            'a':1,
            'b':"string",
            'c':[1,2,3,4],
            'd':{'key':'value'},
        }
        result_variable = helper.load_variables(filepath)
        self.assertEqual( expected_variable, result_variable)

    def test_prepend(self):
        # dictionary test
        fruits = {
            0: 'apple',
            1: 'banana',
            2: 'cranberry',
        }
        prefix = 'sweet_'
        expected_fruits = {
            0: 'sweet_apple',
            1: 'sweet_banana',
            2: 'sweet_cranberry',
        }
        result_fruits = helper.prepend(prefix, fruits)
        self.assertEqual(expected_fruits, result_fruits)

        # exception case
        self.assertRaises(TypeError, helper.prepend, 'string')
        self.assertRaises(TypeError, helper.prepend, 3.14)

    def test_concat_path(self):
        # case 1: first arg with tailing slash
        root = '/var/lib/run/'
        filename = 'sshd'
        expected_path = root + filename
        result_path = helper.concat_path(root, filename)
        self.assertEqual(expected_path, result_path)

        # case 2: first arg without tailing slash
        root = '/var/lib/run'
        filename = 'sshd'
        expected_path = root + '/' + filename
        result_path = helper.concat_path(root, filename)
        self.assertEqual(expected_path, result_path)

        # case 3: three args
        url = 'http://blog.wretch.cc'
        user = 'tonystark'
        thread = 'I\'m_Iron_Man.'
        expected_url = url + '/' + user + '/' + thread
        result_url = helper.concat_path(url, user,thread)
        self.assertEqual( expected_url, result_url)

        # case 4: multiple cases
        d1 = '/usr/'
        d2 = 'local'
        d3 = 'etc/'
        d4 = 'vim'
        d5 = 'colorschema/'
        d6 = 'jellybeans.vim'
        expected_path = d1 + d2 + '/' + d3 + d4 + '/' + d5 + d6
        result_path = helper.concat_path(d1,d2,d3,d4,d5,d6)
        self.assertEqual(expected_path, result_path)

        # case 5: bad arguments occurs Attribute Error
        self.assertRaises(AttributeError, helper.concat_path, '/var') # only 1 argument
        self.assertRaises(AttributeError, helper.concat_path, '/var','/log') # second argument with leading slash





