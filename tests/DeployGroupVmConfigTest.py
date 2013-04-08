__author__ = 'OT Chen'
import unittest
from constant import *
import deployGroupVmConfig

class DeployGroupVmConfigTest(unittest.TestCase):
    def setUp(self):
        self.c = deployGroupVmConfig.DeployGroupVmConfig()
        test_config={}
        test_config['deploy_root']='/var/test_deploy'
        test_config['user_data_dirname']='test_user_data_dir'
        test_config['repository_url']='http://google.com/vm'
        test_config['prototype_filenames']={
            PROTOTYPE_GENTOO:'mygentoo.img',
            PROTOTYPE_UBUNTU_12_04:'myubuntu12.img',
        }
        self.c.overwrite(test_config)
        self.tc = test_config

    def test_prototype_url(self):
        gentoo_filename = self.tc['prototype_filenames'][PROTOTYPE_GENTOO]
        ubuntu_filename = self.tc['prototype_filenames'][PROTOTYPE_UBUNTU_12_04]
        expected_gentoo_url = self.tc['repository_url'] + '/prototype/' + gentoo_filename
        expected_ubuntu_url = self.tc['repository_url'] + '/prototype/' + ubuntu_filename
        self.assertEqual(expected_gentoo_url, self.c.prototype_url(PROTOTYPE_GENTOO))
        self.assertEqual(expected_ubuntu_url, self.c.prototype_url(PROTOTYPE_UBUNTU_12_04))
