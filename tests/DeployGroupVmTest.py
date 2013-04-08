import deployGroupVm
import groupVm
from constant import *
import unittest
import os
import helper
import tempfile
import libvirt_config
import libvirt
import shutil



class DeployTest(unittest.TestCase):
    def setUp(self):
        self.dgv = deployGroupVm.DeployGroupVm()
        self.gentoo_normal_vm_para = {
            'prototype': PROTOTYPE_GENTOO,
            'cpu': '1',
            'memory': '1024',
            'disk': '8',
        }
        self.ubuntu_normal_vm_para = {
            'prototype': PROTOTYPE_UBUNTU_12_04,
            'cpu': '1',
            'memory': '1024',
            'disk': '8',
        }
        self.sample_vms_paras = {
            1: self.gentoo_normal_vm_para,
            2: self.ubuntu_normal_vm_para,
        }
        self.sample_username = 'ot32em'
        self.sample_groupid = '3'
        self.fake_prototype_filename_config = { # avoid download 3.2G image taking so long time
            'prototype_filenames': {
                PROTOTYPE_GENTOO:'100mb.img',
                PROTOTYPE_APACHE:'100mb.img',
                PROTOTYPE_UBUNTU_12_04:'100mb.img',
            }
        }
        self.sample_group_vm = groupVm.GroupVm(self.sample_username, self.sample_groupid, self.sample_vms_paras)


    def test_vm_dir(self):
        c = self.dgv.config()
        g = self.sample_group_vm
        for subid in g.subids():
            expected_vm_dir = '{userdata_dir}/{prototype}/{username}/{vm_name}'.format(
                userdata_dir = c.user_data_dir(),
                prototype = c.prototype_name(g.vm_prototype(subid)),
                username = g.username(),
                vm_name = g.vm_name(subid)
            )
            result_vm_dir = self.dgv.vm_dir(g, subid)
            self.assertEqual(expected_vm_dir, result_vm_dir)

    def test_group_vm_download_dir(self):
        c = self.dgv.config()
        g = self.sample_group_vm
        expected_dir = helper.concat_path(
            c.download_dir(),
            g.group_name()
        )
        result_dir = self.dgv.group_download_dir(g)
        self.assertEqual( expected_dir, result_dir )

    def test_download_image(self):
        c = self.dgv.config()
        g = self.sample_group_vm
        self.dgv.overwrite_config(self.fake_prototype_filename_config)
        for subid in g.subids():
            prototype = g.vm_prototype(subid)
            download_dir = self.dgv.group_download_dir(g)
            method = c.download_method()
            prototype_filename = c.prototype_filename(prototype)

            self.dgv.download_image(prototype, download_dir, method)

            expected_filepath = os.path.join(download_dir, prototype_filename)
            self.assertTrue( os.path.exists( expected_filepath ))


    def test_make_directories(self):
        self.dgv.make_directories(self.sample_group_vm)

        download_dir = self.dgv.group_download_dir(self.sample_group_vm)
        result = os.path.exists(download_dir)
        self.assertTrue(result)
        for subid in self.sample_group_vm.subids():
            vm_dir = self.dgv.vm_dir(self.sample_group_vm, subid)
            result = os.path.exists(vm_dir)
            self.assertTrue(result)

    def test_copy_images(self):
        pass

    def test_resize_images(self):
        pass

    def test_make_libvirt_xmls(self):
        pass


    def test_boot(self):
        g = self.sample_group_vm
        d = self.dgv
        d.boot(g,[1,2])

        s = libvirt.open(d.config().libvirt_connection_uri())
        names = d.libvirt_running_names()
        download_dir = d.group_download_dir(g)
        shutil.rmtree(download_dir)
        for subid in g.subids():
            name = g.vm_name(subid)
            self.assertIn(name, names)
            if name in names:
                domain = s.lookupByName(name)
                domain.destroy()
            vm_dir = d.vm_dir(g, subid)
            shutil.rmtree(vm_dir)


    def test_post_booting(self):
        pass

