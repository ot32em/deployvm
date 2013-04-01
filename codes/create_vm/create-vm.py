import libvirt
import os as os_module
import sys
import make_libvirt_config as mlc
import time


''' 
    basic systom attributes 
        name
            > username as un
            > group number as gn
            > subid number as sn
            > fullname: $un-$gn-$sn
        os type
            > ubuntu
            > gentoo
        cpu amount
            > 1-4
        memory size
            > 256-1024
        disk size
            > 4G-16GB
    
    name as first parameter
    os type as second parameter
    cpu, memory, and diks combined in third parameter as config
            
'''

''' constants  init '''
VM_OS_UBUNTU=1
VM_OS_GENTOO=2
VM_OS_WEB=3
VM_OS_HADOOP=4
VM_OS_DEFAULT=VM_OS_UBUNTU

''' root path '''
repository_url='http://localhost/vm/'
cloud_dir='/root/vm/cloud/userdata/'

''' meta info '''
os_names = { VM_OS_GENTOO:'gentoo', VM_OS_UBUNTU:'ubuntu', VM_OS_WEB:'web', VM_OS_HADOOP:'hadoop' }
os_dirs = dict()
for os in os_names :
    os_dirs[os] = cloud_dir + os_names[os] + '/'
# example: os_dirs['gentoo'] = /root/vm/cloud/userdata/gentoo/


''' tool functions '''
def get_vm_name( username, gn, sn ):
    return '%s-%i-%i' % (username, gn, sn)

def get_vm_dir(username, vmname, os):
    return os_dirs[os] + username + '/' + vmname + '/'
#example: vm_dir('ot32em-2-3', VM_OS_UBUNTU) will return
#           return '/root/vm/cloud/userdata/ubuntu/ot32em-2-3/'


''' command functions '''

def mkdir(dirname):
    cmd='mkdir -p ' + dirname
    run_cmd( cmd )

def download(uri, save_as):
    cmd = 'wget %s -O %s' % ( uri, save_as)
    run_cmd(cmd)

def resize_image( image_path, GB ) :
    cmd = 'resize2fs %s %sG' % (image_path, GB)
    run_cmd( cmd )

def boot_vm( xml_path ):
    cmd = 'virsh create ' + xml_path
    run_cmd( cmd )

def addportmapping( vm_name, port ):
    cmd = 'echo mysql insert into portmapping where port=%s and vmname=%s' % (port, vm_name)
    run_cmd( cmd )

def run_cmd(cmd):
    print('run command: ' + cmd)
    return os_module.system(cmd)


''' vm function '''
def check_vm_alive(vm_name):
    con = libvirt.open('xen:///')
    isActive = False

    # check booted?
    try:
        domain = con.lookupByName(vm_name)
        isActive = domain.isActive()
    except libvirt.libvirtError as e:
        if e.get_error_code == libvirt.VIR_ERR_NO_DOMAIN :
            return false
    return isActive

def check_vm_touchable(vm_name):
    cmd = "ping -c 2 " + vm_name
    return run_cmd( cmd )



''' main function ''' 

def create_gentoo(username, gn, sn, config):

    vm_name = get_vm_name( username, gn, sn)

    if check_vm_alive( vm_name ) :
        raise SystemExit('VM %s has been created!!' % vm_name)

    vm_dir = get_vm_dir(username, vm_name, VM_OS_UBUNTU)

    # make vm directory
    mkdir( vm_dir )

    # deploy a image
    ''' download kernel '''
    kernel_uri = repository_url + 'kernel/gentoo-kernel-domu.img'
    kernel_path = vm_dir + 'gentoo-kernel-domu.img'
    download( kernel_uri, kernel_path )

    ''' download image '''
    image_uri = repository_url + 'prototype/gentoo-prototype.img'
    image_path = vm_dir + 'gentoo.img'
    download(image_uri, image_path)

    ''' resize image '''
    numGBs = config['disk']
    resize_image( image_path, numGBs)

    # generate xml descriptor
    xml_path = vm_dir + vm_name + '.xml'
    mlc.make_xen_libvirt_config( xml_path, vm_name, config['cpu'], config['memory'], image_path, kernel_path )

    # create vm by xml file
    boot_vm( xml_path )
    
    # check vm whether boot successfully or not
    times = 3
    while True:
        alive = check_vm_alive( vm_name )
        if alive:
            break
        else:
            print('VM %s does not respond. wait %i seconds for another ping(%s trial left).' % (vm_name, 5, times))
            for i in xrange(5):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)
            times = times-1

        if times <= 0 :
            raise SystemExit('VM booting failed...')

    print('VM %s is up.' % vm_name)

    # configure portmapping with port=22 
    addportmapping(vm_name, 22)


if __name__ == '__main__' :
    username = 'ot32em'
#    vm_name = 'ot32em-1-1'
    config = { 'cpu':'1', 'memory':'512', 'disk':'8' }
    for i in range(1,4,1):
        create_gentoo( username, 1, i, config ) 
    
