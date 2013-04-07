DOWNLOAD_METHOD_BT = DOWNLOAD_METHOD_BITTORRENT = 0
DOWNLOAD_METHOD_UNICAST = DOWNLOAD_METHOD_UNI = 1
download_method='unicast'
hypervisor = "xen"

deploy_root="/var/www/localhost/htdocs/vm/cloud/"
deploy_user_data_dir = deploy_root + "user_data/"
download_dir = deploy_root + "tmp/download/"

repository_url="http://192.168.31.168/vm/"
repository_prototype_url = repository_url + 'prototype/'
repository_kernel_url = repository_url + 'kernel/'
repository_torrent_url = repository_url + 'torrent/'


''' vm image setting '''
prototype_filenames = { 'gentoo' : "gentoo-prototype.img",
                        'ubuntu' : "ubuntu-prototype.img",
                        'hadoop-master' : "hadoop-master-prototype.img",
                        'hadoop-slave' : "hadoop-slave-prototype.img",
                        'apache' : "apache.img" 
}

use_kernel = { 'gentoo' : '3.7',
               'ubuntu' : '3.7',
               'hadoop-master' : '3.7',
               'hadoop-slave' : '3.7',
               'apache' : '3.7',
               'ubuntu9' : '2.6'
}

''' vm kernel setting '''
kernel_filenames = { '2.6':'kernel-2.6.img',
                     '3.7':'kernel-2.7.img'}

''' prototype_uris, kernel_uris, os_types, kernel_types will be assigned at load_config '''

torrent_filenames = {'gentoo' : 'gentoo-prototype.torrent',
                     'ubuntu' : 'ubuntu-prototype.torrent',
                     'hadoop-master' : 'hadoop-master.torrent',
                     'hadoop-slave' : 'hadoop-slave.torrent',
                     'apache' : 'apache.torrent'}

