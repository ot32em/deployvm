import deploy
import GroupVm
from constant import *
import unittest

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
        b = self.bgv
        c = self.bgv.config
        g = self.group_vm
        for subid in self.group_vm.subids():
            expected_vm_dir = '{userdata_dir}/{prototype}/{username}/{vm_name}'.format(
            userdata_dir = c.user_data_dir(),
            prototype = c.prototype_filename(g.vm_prototype(subid)),
            username = g.username(),
            vm_name = g.vm_name(subid) );
            self.assertEqual( expected_vm_dir, b.vm_dir(g.groupid()) )

    def test_group_vm_download_dir(self):
        expected_dir = '{download_dir}/{group_name}'.format(
            download_dir = self.c.download_dir(),
            group_name = self.g.group_name()
        )
        self.assertEqual( expected_dir, self.b.group_vm_download_dir(self.g))

    def test_download_image(self):
        self.assertFalse()

    def test_make_directories(self):
        self.assertFalse()

    def test_copy_images(self):
        self.assertFalse()


    def test_resize_images(self):
        self.assertFalse()

    def test_make_libvirt_xmls(self):
        self.assertFalse()

    def test_boot_vm(self):
        self.assertFalse()

    def test_post_booting(self):
        self.assertFalse()
