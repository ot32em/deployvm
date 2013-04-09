__author__ = 'OT Chen'
import helper
import os

class DeployGroupVmConfig:
    def __init__(self, config_filename='deploy.cfg.py'):
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
