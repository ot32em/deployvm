import deploy
import GroupVm
from constant import *
import unittest
import os


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.c = deploy.BootVmConfig()
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




class DeployTest(unittest.TestCase):

    def setUp(self):
        self.b = deploy.BootGroupVm()
        test_config = {}
        test_config['prototype_filenames']= {
            PROTOTYPE_GENTOO:'100mb.img',
            PROTOTYPE_APACHE:'100mb.img',
            PROTOTYPE_UBUNTU_12_04:'100mb.img',
        }
        self.b.overwrite_config(test_config)
        vm_para = {
            'prototype': PROTOTYPE_GENTOO,
            'cpu': '1',
            'memory': '1024',
            'disk': '8',
        }
        vm_para2 = {
            'prototype': PROTOTYPE_UBUNTU_12_04,
            'cpu': '1',
            'memory': '1024',
            'disk': '8',
        }
        vms_parameters = {
            0: vm_para.copy(),
            1: vm_para.copy(),
            2: vm_para2.copy(),
        }
        self.boot_depend = [[0], [1, 2]]
        username = 'ot32em'
        groupid = '3'
        self.g = GroupVm.GroupVm(username, groupid, vms_parameters)
        self.c = self.b.config()

    def tearDown(self):
        self.b.rollback(self.g)

    def test_vm_dir(self):
        for subid in self.g.subids():
            expected_vm_dir = '{userdata_dir}/{prototype}/{username}/{vm_name}'.format(
            userdata_dir = self.c.user_data_dir(),
            prototype = self.c.prototype_name(self.g.vm_prototype(subid)),
            username = self.g.username(),
            vm_name = self.g.vm_name(subid) )
            self.assertEqual( expected_vm_dir, self.b.vm_dir(self.g, subid))

    def test_group_vm_download_dir(self):
        expected_dir = '{download_dir}/{group_name}'.format(
            download_dir = self.c.download_dir(),
            group_name = self.g.group_name()
        )
        self.assertEqual( expected_dir, self.b.group_vm_download_dir(self.g))

    def test_config_prototype_url(self):
        expected_url = 'http://140.112.31.168/vm/prototype/100mb.img'
        result_url = self.c.prototype_url(PROTOTYPE_GENTOO)
        self.assertEqual( expected_url, result_url)



    def test_download_image(self):
        pass
        for subid in self.g.subids():
            prototype = self.g.vm_prototype(subid)
            download_dir = self.b.group_vm_download_dir(self.g)
            method = self.c.download_method()
            prototype_filename = self.c.prototype_filename(prototype)
            self.b.download_image(prototype, download_dir, method)
            expected_filepath = os.path.join(download_dir, prototype_filename)
            self.assertTrue( os.path.exists( expected_filepath ))


    def test_make_directories(self):
        pass

    def test_copy_images(self):
        pass

    def test_resize_images(self):
        pass

    def test_make_libvirt_xmls(self):
        pass

    def test_boot_vm(self):
        pass

    def test_post_booting(self):
        pass
