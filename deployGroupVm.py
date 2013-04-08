
# The thin-deploy daemon assumes master have made sure my machine has enough resource to deploy

# @
# @var dict:configs - a dictionary which key as subid, value as vm 
#      config of the subid.
#
# system modules
import time
import libvirt
import os
import shutil
import logging
# custom modules
import helper
from constant import *
import download
import libvirt_config
from deployGroupVmConfig import DeployGroupVmConfig


class DeployGroupVm(object):
    '''
    @type self._config DeployGroupVmConfig
    @type self.logger logger.Logger
    '''

    def __init__(self, config_filename='deploy.cfg.py'):
        self._config = DeployGroupVmConfig(config_filename)
        self.setup_logger(config_filename)

    def overwrite_config(self, new_dictionary):
        self.config().overwrite(new_dictionary)

    def setup_logger(self, logger_filename):
        self.logger = logging.getLogger( logger_filename)
        self.logger.setLevel( self.config().log_level() )
        file_handler = logging.FileHandler('./log/' + logger_filename + '.log')
        file_handler.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.ERROR)
#        self.logger.addHandler(file_handler)
#        self.logger.addHandler(stream_handler)

    def config(self):
        return self._config


    def boot(self, group_vm, boot_depend):
        '''
        @ type group_vm GroupVM
        @ type boot_depend list
        '''

        # make vm directory, download dir for group
        self.make_directories(group_vm)
        # Downloading Big Files: Prototype image, usually 500MB~3000MB via bt or unicast, then deploy to each vm folder
        # via local copying files .
        self.download_images(group_vm)
        # Setup each components for VM creation: folder, prototype image, kernel image, resize disk, and booting xml
        # config.
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

    def failed_rollback(self, group_vm):
        self.rollback(group_vm, True)

    def rollback(self, group_vm, backup=False):
        #self.logger.info("Start to rollback group_vm: [%s]" % group_vm.group_name())
        if backup:
            failed_dirname = self.failed_log_dirname(group_vm)
            failed_dir = os.path.join( self.config().failed_log_dir(), failed_dirname)
            if not os.path.exists(failed_dir):
                os.makedirs(failed_dir)
            self.logger.debug("Failed records will be created under the folder: %s" % failed_dir )

        running_names = self.libvirt_running_names()
        for subid in group_vm.subids():
            vm_dir = self.vm_dir(group_vm, subid)
            if backup:
                # mv libvirt config to fail_boot_log/timestamp-groupname-backup
                xml_filename = group_vm.vm_name(subid) + '.xml'
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
            if vm_name in running_names:
                try:
                    session = libvirt.open(self.config().libvirt_connection_uri())
                    d = session.lookupByName(vm_name)
                    d.destroy()
                    self.logger.debug("VM %s has beend destroied." % vm_name )
                except libvirt.libvirtError:
                    pass

    def libvirt_running_names(self):
        names = []
        s = libvirt.open(self.config().libvirt_connection_uri())
        for vid in s.listDomainsID():
            v = s.lookupByID(vid)
            names.append(v.name())
        return names

    def failed_log_dirname(self, group_vm):
        timestamp = time.strftime("%y%m%d-%H:%M:%S")
        return "%s-%s" % (timestamp, group_vm.group_name())

    def make_failed_log_dir(self, dirname):
        failed_dir = os.path.join(self.config().failed_log_dir(), dirname)
        if not os.path.exists(failed_dir):
            os.mkdir(failed_dir)
        return failed_dir

    def vm_dir(self, group_vm, subid):
        '''
        @type group_vm GroupVm
        @type subid int
        '''
        prototype = group_vm.vm_prototype(subid)
        deploy_prototype_fullpath = self.config().deploy_prototype_dir(prototype)
        return group_vm.vm_dir(deploy_prototype_fullpath, subid)

    def group_download_dir(self, group_vm):
        return os.path.join(self.config().download_dir(), group_vm.group_name())

    def download_images(self, group_vm):
        self.logger.debug('Start method: download_images of Group VM[%s]' % group_vm.group_name())
        method = self.config().download_method()
        unique_prototypes = group_vm.unique_prototypes()
        download_dir = self.group_download_dir(group_vm)
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
        download_dir = self.group_download_dir(group_vm)
        helper.mkdir_p(download_dir)
        for subid in group_vm.subids():
            self.make_vm_directory(group_vm, subid)

    def make_vm_directory(self, group_vm, subid):
        vm_dir = self.vm_dir(group_vm, subid)
        helper.mkdir_p(vm_dir)

    def copy_images(self, group_vm):
        self.logger.debug('Start method: copy_images of Group VM[%s]' % group_vm.group_name())
        for subid in group_vm.subids():
            self.copy_vm_image(group_vm, subid)

    def copy_vm_image(self, group_vm, subid):
        download_dir = self.group_download_dir(group_vm)
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
            cmd = "e2fsck -f " + prototype_fullpath
            os.system(cmd)
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


