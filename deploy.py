
# The thin-deploy daemon assumes master have made sure my machine has enough resource to deploy

# @
# @var dict:configs - a dictionary which key as subid, value as vm 
#      config of the subid.
#
import helper
import time
import libvirt_config
import libvirt
import os
import download
import shutil
from constant import *
import logging


class BootGroupVm(object):
    def __init__(self, config_filename='deploy.cfg.py'):
        self._config = BootVmConfig(config_filename)
        self.setup_logger(config_filename)

    def overwrite_config(self, new_dictionary):
        self.config().overwrite(new_dictionary)

    def setup_logger(self, logger_filename):
        self.logger = logging.getLogger( logger_filename)
        self.logger.setLevel( self.config().log_level() )
        file_handler = logging.FileHandler('./log/' + logger_filename + '.log')
        file_handler.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler()
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def config(self):
        return self._config


    def boot(self, group_vm, boot_depend):
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
                xml_fullpath = os.path.join(self.vm_dir(group_vm, subid),  xml_filename)
                self.boot_vm(xml_fullpath)
        # Do something after booting, it is not implemented yet.
        self.post_booting(group_vm)

    def rollback(self, group_vm):
        self.logger.debug("Start to rollback.")
        failed_dirname = self.failed_log_dirname(group_vm)
        failed_dir = os.path.join( self.config().failed_log_dir(), failed_dirname)
        if not os.path.exists(failed_dir):
            os.makedirs(failed_dir)
        self.logger.debug("Failed records will be created under the folder: %s" % failed_dir )

        for subid in group_vm.subids():
            vm_dir = self.vm_dir(group_vm, subid)
            # mv libvirt config to fail_boot_log/timestamp-groupname-backup
            xml_filename = group_vm.vm_name() + '.xml'
            xml_filepath = os.path.join(vm_dir, xml_filename)
            if os.path.exists(xml_filepath):
                self.logger.debug("VM libvirt xml[%s] was found. Ready to backup it." % (xml_filename))
                shutil.move(xml_filepath, os.path.join(failed_dir, xml_filename))
                self.logger.debug("Backuped vm libvirt xml[%s] from [%s] to [%s]" % (xml_filename, vm_dir, failed_dir))
            # delete and clear directory
            if os.path.exists(vm_dir):
                self.logger.debug("VM dir[%s] was found. Ready to remove it." % vm_dir)
                shutil.rmtree(vm_dir)
                self.logger.debug("Removed vm dir[%s]." % vm_dir)

            # destroy vm
            vm_name = group_vm.vm_name(subid)
            try:
                session = libvirt.open(self.config().libvirt_connection_uri())
                d = session.lookupByName(vm_name)
                d.destroy()
                self.logger.debug("VM %s has beend destroied." % vm_name )
            except libvirt.libvirtError:
                pass

    def failed_log_dirname(self, group_vm):
        timestamp = time.strftime("%y%m%d-%H:%M:%S")
        return "%s-%s" % (timestamp, group_vm.group_name())


    def make_failed_log_dir(self, dirname):
        failed_dir = os.path.join(self.config().failed_log_dir(), dirname)
        if not os.path.exists(failed_dir):
            os.mkdir(failed_dir)
        return failed_dir

    def vm_dir(self, group_vm, subid):
        prototype = group_vm.vm_prototype(subid)
        deploy_prototype_fullpath = self.config().deploy_prototype_dir(prototype)
        return group_vm.vm_dir(deploy_prototype_fullpath, subid)

    def group_vm_download_dir(self, group_vm):
        return os.path.join(self.config().download_dir(), group_vm.group_name())

    def download_images(self, group_vm):
        self.logger.debug('Start method: download_images of Group VM[%s]' % group_vm.group_name())
        method = self.config().download_method()
        unique_prototypes = group_vm.unique_prototypes()
        download_dir = self.group_vm_download_dir(group_vm)
        # download prototypes
        unique_kernel_versions = set()
        for prototype in unique_prototypes:
            self.download_image(prototype, download_dir, method)
            unique_kernel_versions.add(self.config().kernel_version(prototype))
        # download kernels
        for kernel_version in unique_kernel_versions:
            kernel_url = self.config().kernel_url_by_version(kernel_version)
            download.unicast_download(kernel_url, download_dir)

    def download_image(self, prototype, download_dir, method):
        self.logger.debug('Start method: download_image of prototype [%s], download_dir[%s], and method[%s]' % \
                          ( self.config().prototype_name(prototype), download_dir, method) )
        if not os.path.exists( download_dir ):
            self.logger.debug("Directory[%s] does not exist, ready to mkdir it" % download_dir)
            os.makedirs(download_dir)
        if method == DOWNLOAD_METHOD_UNICAST:
            # directly download
            url = self.config().prototype_url(prototype)
            download.unicast_download(url, download_dir, debug=True)
        elif method == DOWNLOAD_METHOD_BITTORRENT:
            # get the torrent, then download via bittorrent
            torrent_url = self.config().torrent_url(prototype)
            download.unicast_download(torrent_url, download_dir, debug=True)
            torrent_path = os.path.join(download_dir, self.config().torrent_filename(prototype))
            download.bt_download(torrent_path, download_dir)

    def make_directories(self, group_vm):
        self.logger.debug('Start method: make_directries of Group VM[%s]' % group_vm.group_name())
        for subid in group_vm.subids():
            vm_dir_fullpath = self.vm_dir(group_vm, subid)
            if not os.path.exists(vm_dir_fullpath):
                os.makedirs(vm_dir_fullpath)

    def copy_images(self, group_vm):
        self.logger.debug('Start method: copy_images of Group VM[%s]' % group_vm.group_name())
        download_dir = self.group_vm_download_dir(group_vm)
        for subid in group_vm.subids():
            vm_dir_fullpath = self.vm_dir(group_vm, subid)
            prototype = group_vm.vm_prototype(subid)
            # copy prototype image
            prototype_filename = self.config().prototype_filename(prototype)
            prototype_src_fullpath = os.path.join(download_dir, prototype_filename)
            prototype_dest_fullpath = os.path.join(vm_dir_fullpath, prototype_filename)
            shutil.copy2(prototype_src_fullpath, prototype_dest_fullpath)
            # copy kernel image
            kernel_filename = self.config().kernel_filename(prototype)
            kernel_src_fullpath = os.path.join(download_dir, kernel_filename)
            kernel_dest_fullpath = os.path.join(vm_dir_fullpath, kernel_filename)
            shutil.copy2(kernel_src_fullpath, kernel_dest_fullpath)

    def resize_images(self, group_vm):
        self.logger.debug('Start method: resize_images of Group VM[%s]' % group_vm.group_name())
        for subid in group_vm.subids():
            prototype_filename = self.config().prototype_filename(group_vm.vm_prototype(subid))
            vm_dir_fullpath = self.vm_dir(group_vm, subid)
            new_size = group_vm.vm_disk(subid)
            prototype_fullpath = os.path.join(vm_dir_fullpath, prototype_filename)
            cmd = "resize2fs {image} {GBs}G".format(image=prototype_fullpath, GBs=new_size)
            os.system(cmd)

    def make_libvirt_xmls(self, group_vm):
        self.logger.debug('Start method: make_libvirt_xmls of Group VM[%s]' % group_vm.group_name())
        hypervisor_type = self.config().hypervisor_type()
        for subid in group_vm.subids():
            prototype = group_vm.vm_prototype(subid)
            vm_dir = self.vm_dir(group_vm, subid)
            vm_name = group_vm.vm_name(subid)
            xml_filename = vm_name + '.xml'
            xml_fullpath = os.path.join(vm_dir, xml_filename)
            image_fullpath = os.path.join(vm_dir, self.config().prototype_filename(prototype))
            kernel_fullpath = os.path.join(vm_dir, self.config().kernel_filename(prototype))
            libvirt_config.make_libvirt_config(hypervisor_type, xml_fullpath, vm_name,
                                               group_vm.vm_cpu(subid), group_vm.vm_memory(subid),
                                               image_fullpath, kernel_fullpath)

    def boot_vm(self, xml_fullpath):
        self.logger.debug('Start method: boot_vm of xml fullpath[%s]' % xml_fullpath)
        session = libvirt.open(self.config().libvirt_connection_uri())
        with open(xml_fullpath, 'r') as f:
            xml_desc = f.read()
        domain = session.createXML(xml_desc, libvirt.VIR_DOMAIN_NONE)
        if not domain:
            self.logger.warning('Booting failed... with xml file [%s]' % xml_fullpath)
        return domain is not None

    def post_booting(self, group_vm):
        self.logger.debug('Start method: post_booting of Group VM[%s]' % group_vm.group_name())
        pass


class BootVmConfig:
    def __init__(self, config_filename):
        self.config_filename = config_filename
        self.config_dictionary = helper.load_variables(config_filename)
        self.load_dictionary()

    def overwrite(self, new_dictionary):
        self.config_dictionary.update(new_dictionary)
        self.reload_dictionary()

    def reload_dictionary(self): # a alias method
        self.load_dictionary()

    def load_dictionary(self):
        config = self.config_dictionary
        self._log_level = config['log_level']
        self._hypervisor_type = config['hypervisor_type']
        self._libvirt_connection_uri = config['libvirt_connection_uri']
        self._download_method = config['download_method']

        self._deploy_root = config['deploy_root']
        self._user_data_dirname = config['user_data_dirname']
        self._failed_log_dirname = config['failed_log_dirname']
        self._download_dirname = config['download_dirname']

        self._repository_url = config['repository_url']

        self._use_kernel_map = config['use_kernel']
        self._prototype_names = config['prototype_names']

        self.RESOURCE_PROTOTYPE = 0
        self.RESOURCE_KERNEL = 1
        self.RESOURCE_TORRENT = 2

        self._repository_dirnames = {
            self.RESOURCE_PROTOTYPE: config['repository_prototype_dirname'],
            self.RESOURCE_KERNEL: config['repository_kernel_dirname'],
            self.RESOURCE_TORRENT: config['repository_torrent_dirname'],
        }

        self._resource_filenames = {
            self.RESOURCE_PROTOTYPE: config['prototype_filenames'],
            self.RESOURCE_KERNEL: config['kernel_filenames'],
            self.RESOURCE_TORRENT: config['torrent_filenames'],
        }

    # Meta Data
    def log_level(self):
        return self._log_level
    def download_method(self):
        return self._download_method
    def hypervisor_type(self):
        return self._hypervisor_type
    def libvirt_connection_uri(self):
        return self._libvirt_connection_uri

    # Normal Map
    def prototype_name(self, prototype):
        return self._prototype_names[prototype]
    def kernel_version(self, prototype):
        return self._use_kernel_map[prototype]

    # General Direcotry
    def deploy_dir(self):
        return self._deploy_root
    def user_data_dir(self):
        return os.path.join(self.deploy_dir(), self._user_data_dirname)
    def download_dir(self):
        return os.path.join(self.deploy_dir(), self._download_dirname)
    def failed_log_dir(self):
        return os.path.join(self.deploy_dir(), self._failed_log_dirname)
    def deploy_prototype_dir(self, prototype):
        return os.path.join(self.user_data_dir(), self.prototype_name(prototype))

    # Resource Filename Getter
    def resource_filename(self, resource_type, resource_key):
        return self._resource_filenames[resource_type][resource_key]
    def prototype_filename(self, prototype):
        return self.resource_filename(self.RESOURCE_PROTOTYPE, prototype)
    def torrent_filename(self, prototype):
        return self.resource_filename(self.RESOURCE_TORRENT, prototype)
    def kernel_filename_by_version(self, kernel_version):
        return self.resource_filename(self.RESOURCE_KERNEL, kernel_version)
    def kernel_filename(self, prototype):
        kernel_version = self.kernel_version(prototype)
        return self.kernel_filename_by_version(kernel_version)

    # Resource URL Getter
    def repository_url(self):
        return self._repository_url
    def repository_dir(self, resource_type):
        return helper.concat_path(self.repository_url(), self._repository_dirnames[resource_type])
    def prototype_url(self, prototype):
        return helper.concat_path(self.repository_dir(self.RESOURCE_PROTOTYPE), self.prototype_filename(prototype))
    def torrent_url(self, prototype):
        return helper.concat_path(self.repository_dir(self.RESOURCE_TORRENT), self.torrent_filename(prototype))
    def kernel_url(self, prototype):
        return helper.concat_path(self.repository_dir(self.RESOURCE_KERNEL), self.kernel_filename(prototype))
    def kernel_url_by_version(self, kernel_version):
        return helper.concat_path(self.repository_dir(self.RESOURCE_KERNEL), self.kernel_filename_by_version(kernel_version))
