
# The thin-deploy daemon assumes master have made sure my machine has enough resource to deploy

# @
# @var dict:configs - a dictionary which key as subid, value as vm 
#      config of the subid.
#
import helper
import libvirt_config
import libvirt
import os
from GroupVm import GroupVm
import download
import shutil
from constant import *
import logging


class BootGroupVm(object):
    def __init__(self, config_filename):
        self.config = BootVmConfig(config_filename)
        self.setup_logger( config_filename)

    def setup_logger(self, logger_filename):
        self.logger = logging.getLogger( logger_filename)
        file_handler = logging.FileHandler( './log/' + logger_filename + '.log')
        file_handler.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler()
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def boot(self, username, groupid, vms_parameters, boot_depend):
        group_vm = GroupVm(username, groupid, vms_parameters)
        # Downloading Big Files: Prototype image, usually 500MB~3000MB via bt or unicast, then deploy to each vm folder
        # via local copying files .
        self.download_images(group_vm)
        # Setup each components for VM creation: folder, prototype image, kernel image, resize disk, and booting xml
        # config.
        self.make_directories(group_vm)
        self.copy_images(group_vm)
        self.resize_images(group_vm)
        self.make_libvirt_xmls(group_vm)
        # Booting
        # example of boot_depend
        # a = [[2,3,4],[8,9],[10,11]]
        # [8,9] will wait until 2, 3, and 4 is completed, [10,11] will stall until [8,9] is completed.
        # in [], the 2,3,4 will boot parallelly,
        for i_round in boot_depend:
            for subid in i_round:
                xml_filename = group_vm.vm_name(subid) + '.xml'
                xml_fullpath = os.path.join(self.vm_dir_fullpath(group_vm, subid),  xml_filename)
                self.boot_vm(xml_fullpath)
        # Do something after booting, it is not implemented yet.
        self.post_booting(group_vm)

    def vm_dir_fullpath(self, group_vm, subid):
        prototype = group_vm.vm_prototype(subid)
        deploy_prototype_fullpath = self.config.deploy_prototype_fullpath(prototype)
        return group_vm.vm_dir_fullpath(deploy_prototype_fullpath, subid)

    def group_vm_download_dir(self, group_vm):
        return os.path.join(self.config.download_dir(), group_vm.group_name())

    def download_images(self, group_vm):
        self.logger.debug('Start method: download_images of Group VM[%s]' % group_vm.group_name())
        method = self.config.download_method()
        unique_prototypes = group_vm.unique_prototypes()
        download_dir = self.group_vm_download_dir(group_vm)
        # download prototypes
        unique_kernel_versions = set()
        for prototype in unique_prototypes:
            self.download_image(prototype, download_dir, method)
            unique_kernel_versions.add(self.config.kernel_version(prototype))
        # download kernels
        for kernel_version in unique_kernel_versions:
            kernel_url = self.config.kernel_url_by_version(kernel_version)
            download.unicast_download(kernel_url, download_dir)

    def download_image(self, prototype, download_dir, method):
        self.logger.debug('Start method: download_image of prototype [%s], download_dir[%s], and method[%s]' % \
                          self.config.prototype_dir_name(prototype), download_dir, method)
        os.makedirs(download_dir)
        if method == DOWNLOAD_METHOD_UNICAST:
            # directly download
            url = self.config.prototype_url(prototype)
            download.unicast_download(url, download_dir)
        elif method == DOWNLOAD_METHOD_BITTORRENT:
            # get the torrent, then download via bittorrent
            torrent_url = self.config.torrent_url(prototype)
            download.unicast_download(torrent_url, download_dir)
            torrent_path = os.path.join(download_dir, self.config.torrent_filename(prototype))
            download.bt_download(torrent_path, download_dir)

    def make_directories(self, group_vm):
        self.logger.debug('Start method: make_directries of Group VM[%s]' % group_vm.group_name())
        for subid in group_vm.subids():
            vm_dir_fullpath = self.vm_dir_fullpath(group_vm, subid)
            if not os.path.exists(vm_dir_fullpath):
                os.makedirs(vm_dir_fullpath)

    def copy_images(self, group_vm):
        self.logger.debug('Start method: copy_images of Group VM[%s]' % group_vm.group_name())
        download_dir = self.group_vm_download_dir(group_vm)
        for subid in group_vm.subids():
            vm_dir_fullpath = self.vm_dir_fullpath(group_vm, subid)
            prototype = group_vm.vm_prototype(subid)
            # copy prototype image
            prototype_filename = self.config.prototype_filename(prototype)
            prototype_src_fullpath = os.path.join(download_dir, prototype_filename)
            prototype_dest_fullpath = os.path.join(vm_dir_fullpath, prototype_filename)
            shutil.copy2(prototype_src_fullpath, prototype_dest_fullpath)
            # copy kernel image
            kernel_filename = self.config.kernel_filename(prototype)
            kernel_src_fullpath = os.path.join(download_dir, kernel_filename)
            kernel_dest_fullpath = os.path.join(vm_dir_fullpath, kernel_filename)
            shutil.copy2(kernel_src_fullpath, kernel_dest_fullpath)

    def resize_images(self, group_vm):
        self.logger.debug('Start method: resize_images of Group VM[%s]' % group_vm.group_name())
        for subid in group_vm.subids():
            prototype_filename = self.config.prototype_filename(group_vm.vm_prototype(subid))
            vm_dir_fullpath = self.vm_dir_fullpath(group_vm, subid)
            new_size = group_vm.vm_disk(subid)
            prototype_fullpath = os.path.join(vm_dir_fullpath, prototype_filename)
            cmd = "resize2fs {image} {GBs}G".format(image=prototype_fullpath, GBs=new_size)
            os.system(cmd)

    def make_libvirt_xmls(self, group_vm):
        self.logger.debug('Start method: make_libvirt_xmls of Group VM[%s]' % group_vm.group_name())
        hypervisor_type = self.config.hypervisor_type()
        for subid in group_vm.subids():
            prototype = group_vm.vm_prototype(subid)
            vm_dir = self.vm_dir_fullpath(group_vm, subid)
            vm_name = group_vm.vm_name(subid)
            xml_filename = vm_name + '.xml'
            xml_fullpath = os.path.join(vm_dir, xml_filename)
            image_fullpath = os.path.join(vm_dir, self.config.prototype_filename(prototype))
            kernel_fullpath = os.path.join(vm_dir, self.config.kernel_filename(prototype))
            libvirt_config.make_libvirt_config(hypervisor_type, xml_fullpath, vm_name,
                                               group_vm.vm_cpu(subid), group_vm.vm_memory(subid),
                                               image_fullpath, kernel_fullpath)

    def boot_vm(self, xml_fullpath):
        self.logger.debug('Start method: boot_vm of xml fullpath[%s]' % xml_fullpath())
        session = libvirt.open(self.config.libvirt_connection_uri())
        with open(xml_fullpath, 'r') as f:
            xml_desc = f.read()
        domain = session.domainCreateXml(xml_desc, libvirt.VIR_DOMAIN_NONE)
        if not domain:
            self.logger.warning('Booting failed... with xml file [%s]' % xml_fullpath)
        return domain is not None

    def post_booting(self, group_vm):
        self.logger.debug('Start method: post_booting of Group VM[%s]' % group_vm.group_name())
        pass


class BootVmConfig:
    def __init__(self, config_filename):
        config = helper.load_variables(config_filename)
        self.config_filename = config_filename
        self.config_variable = config

        self._hypervisor_type = config['hypervisor_type']
        self._libvirt_connection_uri = config['libvirt_connection_uri']
        self._download_method = config['download_method']

        self._deploy_root = config['deploy_root']
        self._user_data_dir = config['deploy_user_data_dir']
        self._download_dir = config['download_dir']
        self._repository_url = config['repository_url']

        self._use_kernel_map = config['use_kernel']
        self._prototype_dir_names = config['prototype_dir_names']

        self.RESOURCE_PROTOTYPE = 0
        self.RESOURCE_KERNEL = 1
        self.RESOURCE_TORRENT = 2
        self._resource_directory_urls = {
            self.RESOURCE_PROTOTYPE: config['repository_url'] + config['repository_prototype_dirname'],
            self.RESOURCE_KERNEL:  config['repository_url'] + config['repository_kernel_dirname'],
            self.RESOURCE_TORRENT: config['repository_url'] + config['repository_torrent_dirname'],
        }

        self._resource_filenames = {
            self.RESOURCE_PROTOTYPE: config['prototype_filenames'],
            self.RESOURCE_KERNEL: config['kernel_filenames'],
            self.RESOURCE_TORRENT: config['torrent_filenames'],
        }

    def download_dir(self):
        return self._download_dir

    def download_method(self):
        return self._download_method

    def hypervisor_type(self):
        return self._hypervisor_type

    def libvirt_connection_uri(self):
        return self._libvirt_connection_uri

    def prototype_dir_name(self, prototype):
        return self._prototype_dir_names[prototype]

    def deploy_prototype_fullpath(self, prototype):
        return os.path.join(self._user_data_dir, self.prototype_dir_name(prototype))

    def resource_filename(self, resource_type, resource_name):
        return self._resource_filenames[resource_type][resource_name]

    def prototype_filename(self, prototype):
        return self.resource_filename(self.RESOURCE_PROTOTYPE, prototype)

    def prototype_url(self, prototype):
        return self._resource_directory_urls[self.RESOURCE_PROTOTYPE] + self.prototype_filename(prototype)

    def torrent_filename(self, prototype):
        return self._resource_filenames[self.RESOURCE_TORRENT][prototype]

    def torrent_url(self, prototype):
        return self._resource_directory_urls[self.RESOURCE_TORRENT] + self.torrent_filename(prototype)

    def kernel_filename(self, prototype):
        kernel_version = self._use_kernel_map[prototype]
        return self._kernel_filename_by_version(kernel_version)

    def kernel_url(self, prototype):
        kernel_version = self.kernel_version(prototype)
        return self._kernel_filename_by_version(kernel_version)

    def _kernel_filename_by_version(self, kernel_version):
        return self.resource_filename(self.RESOURCE_KERNEL, kernel_version)

    def kernel_url_by_version(self, kernel_version):
        return self._resource_directory_urls[self.RESOURCE_KERNEL] + self.kernel_filename(kernel_version)

    def kernel_version(self, prototype):
        return self._use_kernel_map[prototype]

if __name__ == '__main__':
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
    boot_depend = [[0], [1, 2]]
    username = 'ot32em'
    groupid = '3'

    bgv = BootGroupVm('deploy.cfg.py')
    bgv.boot(username, groupid, vms_parameters, boot_depend)
