from constant import *
download_method = DOWNLOAD_METHOD_UNICAST
hypervisor_type = HYPERVISOR_TYPE_XEN
libvirt_connection_uri = 'xen:///'

deploy_root="/var/www/localhost/htdocs/vm/cloud/"
deploy_user_data_dir = deploy_root + "user_data/"
download_dir = deploy_root + "tmp/download/"

repository_url="http://192.168.31.168/vm/"
repository_prototype_dirname = 'prototype/'
repository_kernel_dirname = 'kernel/'
repository_torrent_dirname = 'torrent/'


''' vm image setting '''
prototype_filenames = {
    PROTOTYPE_GENTOO: 'gentoo-prototype.img',
    PROTOTYPE_UBUNTU_12_04 : "ubuntu-prototype.img",
    PROTOTYPE_HADOOP_MASTER : "hadoop-master-prototype.img",
    PROTOTYPE_HADOOP_SLAVE : "hadoop-slave-prototype.img",
    PROTOTYPE_APACHE : "apache.img",
    PROTOTYPE_UBUNTU_9_04 : 'N/A',
}

prototype_dir_names = {
    PROTOTYPE_GENTOO: 'gentoo',
    PROTOTYPE_UBUNTU_12_04 : 'ubuntu',
    PROTOTYPE_HADOOP_MASTER : 'hadoop',
    PROTOTYPE_HADOOP_SLAVE : 'hadoop',
    PROTOTYPE_APACHE : "apache",
    PROTOTYPE_UBUNTU_9_04 : 'ubuntu',
}

use_kernel = {
    PROTOTYPE_GENTOO: KERNEL_VERSION_3_7,
    PROTOTYPE_UBUNTU_12_04 : KERNEL_VERSION_3_7,
    PROTOTYPE_HADOOP_MASTER : KERNEL_VERSION_3_7,
    PROTOTYPE_HADOOP_SLAVE : KERNEL_VERSION_3_7,
    PROTOTYPE_APACHE : KERNEL_VERSION_3_7,
    PROTOTYPE_UBUNTU_9_04 :KERNEL_VERSION_2_6,
}

''' vm kernel setting '''
kernel_filenames = {
    KERNEL_VERSION_2_6 : 'kernel-2.6.img',
    KERNEL_VERSION_3_7 : 'kernel-2.7.img',
}

''' prototype_uris, kernel_uris, os_types, kernel_types will be assigned at load_config '''

torrent_filenames = {
    PROTOTYPE_GENTOO : 'gentoo-prototype.torrent',
    PROTOTYPE_UBUNTU_12_04 : 'ubuntu-prototype.torrent',
    PROTOTYPE_HADOOP_MASTER : 'hadoop-master.torrent',
    PROTOTYPE_HADOOP_SLAVE : 'hadoop-slave.torrent',
    PROTOTYPE_APACHE : 'apache.torrent',
}

