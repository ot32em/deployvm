
# The thin-deploy daemon assumes master have made sure my machine has enough resource to deploy

# @
# @var dict:configs - a dictionary which key as subid, value as vm 
#      config of the subid.
#

import helper
import make_libvirt_config as mlc
import libvirt
import os

config = helper.load_config('deploy.cfg.py')
    
def boot_group_vms( username, groupid, subids, boot_depend, vms_parameters ):
    os_types = get_unique_os_types( vms_parameters)
    group_name = get_group_name( username, groupid )
    download_images( os_types, config['download_dir'], config['download_method'], group_name )
    # It will cost most time in download method...

    make_directories( username, groupid, subids, vms_parameters )
    copy_images( username, groupid, subids, vms_parameters )

    make_vm_config_xmls( username, groupid, subids, vms_parameters )

    # example of boot_depend
    # a = [[2,3,4],[8,9],[10,11]]
    # [8,9] will wait [2,3,4] is completed, [10,11] will wait [8,9] is completed
    # in [], the 2,3,4 will boot parallelly, 

    for i_round in boot_depend :
        for subid in i_round :
            vm_name = get_vm_name( username, groupid, subid )
            vm_dir = get_vm_dir( username, groupid, subid, vms_parameters[subid]['os_type'] )

            xml_filename = vm_name + '.xml'
            xml_fullpath = vm_dir + xml_filename
            boot_vm( xml_fullpath )

    add_sshport( username, groupid, subids )


        
def get_group_name(username, groupid):
    return '%s-%s' % (username, groupid )
def get_vm_name(username, groupid, subid):
    return '%s-%s-%s' % ( username , groupid, subid )
def get_vm_dir(username, groupid, subid, os_type ):
    vm_name = get_vm_name( username, groupid, subid)
    return config['deploy_user_data_dir'] + username + '/' + vm_name + '/'

def get_unique_os_types( vms_parameters ):
    os_types = []
    for sid in vms_parameters :
        os_type = vms_parameters[ sid ]['os_type']
        if os_type not in os_types :
            os_types.append( os_type )
    return os_types

def download_images( os_types, download_dir, method, prefix ):
    if method == 'unicast':
        for os_type in os_types:
            save_as_filename = prefix + config['prototype_filenames'][os_type] 
            save_as = config['download_dir']
            download_url = config['prototype_uris'][os_type]
            unicast_download( download_url, save_as )
    elif method == 'bt':
        for os_type in os_types:
            save_as_filename = prefix + config['prototype_filenames'][os_type] 
            save_as = config['download_dir']

            torrent_filename = prefix + config['torrent_filenames'][os_type ] 
            torrent_url = config['repository_torrent_url'] + torrent_filename
            torrent_fullpath = config['download_dir'] + torrent_filename

            bt_download( torrent_url, torrent_fullpath, save_as )
        

def unicast_download( url, save_as ):
    cmd = 'wget {url} -O {save_as_path}'.format(url=url, save_as_path=save_as )
    run_cmd( cmd )
    pass

def bt_download( torrent_url, torrent_fullpath, save_as ):
    unicast_download( torrent_url, torrent_fullpath)
    bt( torrent_fullpath, save_as)
    
    pass

def run_cmd(cmd):
    print('To run cmd: ' + cmd)
    return 0
    #return os.system(cmd)

def bt(torrent_fullpath, save_as):
    print("use %s to download file as %s" % ( torrent_fullpath, save_as))
    # use some methods
    

def make_directories( username, groupid, subids, vms_parameters ):
    for subid in subids:
        vm_name = get_vm_name( username, groupid, subid )
        os_type = vms_parameters[ subid ][ 'os_type' ]
        vm_fullpath_dir = get_vm_dir( username, groupid, subid, os_type )
        if not os.path.exists( vm_fullpath_dir ):
            os.makedirs( vm_fullpath_dir ) # recursively make intermediate directoies to contain leaf directory

def copy_images( username, groupid, subids, vms_parameters ):
    for subid in subids :
        os_type = vms_parameters[subid]['os_type']
        vm_fullpath_dir = get_vm_dir( username, groupid, subid, os_type )
        group_name = get_group_name( username, groupid )
        image_in_download_dir = config['download_dir'] + group_name + config['prototype_filenames'][os_type]
        cmd = "cp %s %s" % (image_in_download_dir, vm_fullpath_dir)
        run_cmd( cmd )


def make_vm_config_xmls( username, groupid, subids, vms_parameters ):
    hypervisor = 'xen'
    for subid in subids:
        para = vms_parameters[subid]
        os_type = para['os_type']
        vm_dir = get_vm_dir( username, groupid, subid, os_type )
        vm_name = get_vm_name( username, groupid, subid )

        xml_filename = vm_name + '.xml'
        xml_fullpath = vm_dir + xml_filename
        image_fullpath = vm_dir + config['prototype_filenames'][os_type]
        kernel_type = config['use_kernel'][os_type]
        kernel_fullpath = vm_dir + config['kernel_filenames'][kernel_type]

        if hypervisor == 'xen' :
            mlc.make_xen_libvirt_config( xml_fullpath, vm_name, para['cpu'], para['memory'], image_fullpath, kernel_fullpath )


        elif hypervisor =='kvm' : 
            pass
            # todo

def boot_vm( xml_fullpath ):
    cmd = "xl create " + xml_fullpath
    return run_cmd( cmd ) == 0

def add_sshport( username, groupid, subids ):
    vm_port = 22
    for subid in subids :
        vm_name = get_vm_name( username, groupid, subid )
        cmd = "mysql insert into port (vmport,vm_name, owner) values (%s,%s,%s)" % ( vm_port, vm_name, username )
        run_cmd( cmd )

    
if __name__ == '__main__':

    vm_para = {}
    vm_para2 = {}
    vm_para['os_type'] = 'gentoo'
    vm_para['cpu'] = '1'
    vm_para['memory'] = '1024'
    vm_para['disk'] = '8'
    vm_para2['os_type'] = 'ubuntu'
    vm_para2['cpu'] = '1'
    vm_para2['memory'] = '1024'
    vm_para2['disk'] = '8'
    vms_parameters={}
    vms_parameters[0] = vm_para
    vms_parameters[1] = vm_para.copy()
    vms_parameters[2] = vm_para2
    boot_depend = [[0,1],[2]]

    username='ot32em'
    groupid='2'
    subids = vms_parameters.keys()
    boot_group_vms( username, groupid, subids, boot_depend, vms_parameters )

