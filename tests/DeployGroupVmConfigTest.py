__author__ = 'OT Chen'
import logging
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

    def test_download_dir(self):
        t = {
            'download_dirname': 'happy_download',
            'deploy_root': '/var/home/',
        }
        self.c.overwrite(t)
        expected = t['deploy_root'] + t['download_dirname']
        result = self.c.download_dir()
        self.assertEqual(expected, result)

    def test_getter(self):
        t = {
            'hypervisor_type': HYPERVISOR_TYPE_KVM,
            'download_method':DOWNLOAD_METHOD_BITTORRENT,
            'libvirt_connection_uri':'kvm://root@localhost',
            'log_level': logging.ERROR,
            'deploy_root': '/var/',
            'repository_url': 'http://www.google.com'
        }
        self.c.overwrite(t)
        self.assertEqual( self.c.hypervisor_type(), t['hypervisor_type'])
        self.assertEqual( self.c.download_method(), t['download_method'])
        self.assertEqual( self.c.libvirt_connection_uri(), t['libvirt_connection_uri'])
        self.assertEqual( self.c.log_level(), t['log_level'])
        self.assertEqual( self.c.deploy_dir(), t['deploy_root'])
        self.assertEqual( self.c.repository_url(), t['repository_url'])

    def test_kernel(self):
        t = {
            'use_kernel': {
                PROTOTYPE_GENTOO: KERNEL_VERSION_2_6,
                PROTOTYPE_UBUNTU_12_04: KERNEL_VERSION_3_7,
            }
        }
        self.c.overwrite(t)
        self.assertEqual(KERNEL_VERSION_2_6, self.c.kernel_version(PROTOTYPE_GENTOO))
        self.assertEqual(KERNEL_VERSION_3_7, self.c.kernel_version(PROTOTYPE_UBUNTU_12_04))

    def test_torrent_url(self):
        t = {
            'torrent_filenames': {
                PROTOTYPE_GENTOO: 'haha.torrent',
            },
            'repository_url': 'http://www.google.com',
            'repository_torrent_dirname': 'files/no1/2012/torrents',
        }
        expected = t['repository_url'] + '/' + t['repository_torrent_dirname'] + '/' + t['torrent_filenames'][PROTOTYPE_GENTOO]
        self.c.overwrite(t)
        result = self.c.torrent_url(PROTOTYPE_GENTOO)
        self.assertEqual( expected, result)




