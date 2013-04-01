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
    return run_cmd(cmd) == 0

def download(uri, save_as):
    cmd = 'wget -N %s -O %s' % ( uri, save_as) # -N for overrite existed files
    return run_cmd(cmd) == 0

def resize_image( image_path, GB ) :
    cmd = 'resize2fs %s %sG' % (image_path, GB)
    return run_cmd( cmd ) == 0


def remove_file( file_path ):
    if os_module.path.exists( file_path):
        print("Remove file: " + file_path)
        os_module.remove( file_path )
        return True
    return False
    
def backup_file( file_path ):
    if not os_module.path.exists(file_path): 
        return False
    append_id = 1
    dest_path = ''
    while True:
        dest_path = file_path + "." + str(append_id)
        if os_module.path.exists(dest_path):
            append_id = append_id + 1
            if append_id > 10 :
                return False
            else:
                continue
            
        break
    cmd = "cp %s %s" % (file_path, dest_path)
    run_cmd(cmd)

def boot_vm( xml_path ):
    cmd = 'virsh create ' + xml_path
    run_cmd( cmd )

def addportmapping( vm_name, port ):
    cmd = 'echo mysql insert into portmapping where port=%s and vmname=%s' % (port, vm_name)
    run_cmd( cmd )

def run_cmd(cmd):
    print('[%s] prepare to run command: %s ' % (time.strftime('%H:%I:%S'), cmd) )
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
    vm_dir = get_vm_dir(username, vm_name, VM_OS_UBUNTU)
    kernel_name = "gentoo-kernel.img"
    image_name = "gentoo-prototype.img"
    xmlfile_name = vm_name + ".xml"

    if check_vm_alive( vm_name ) :
        print("Error: VM %s is runninghas been booted.")
        return False

    ''' pre booting scripts '''
    # make vm directory
    mkdir( vm_dir )

    try:
        kernel_path = prepare_kernel(vm_dir, kernel_name)
        image_path = prepare_image(vm_dir, config['disk'], image_name)

        # generate xml descriptor
        xmlfile_path = vm_dir + xmlfile_name
        mlc.make_xen_libvirt_config( xmlfile_path, vm_name, config['cpu'], config['memory'], image_path, kernel_path )

        ''' booting scripts '''
        # create vm by xml file and check alive
        boot_vm( xmlfile_path )
        check_vm(vm_name)

        # completed!
        print('VM %s is up.' % vm_name)

        ''' post booting scritpts '''
        # configure portmapping with port=22 
        addportmapping(vm_name, 22)
        return True

    except Exception as e:
        print(e)
        print("Booting Failed... prepare to clean files")
        
        clean_kernel_file( vm_dir + kernel_name)
        clean_image_file( vm_dir + image_name)
        clean_config_file( vm_dir + xmlfile_name )


''' sub functions '''
def prepare_kernel(vm_dir, kernel_name):
    ''' download kernel '''
    kernel_uri = repository_url + 'kernel/' + kernel_name
    kernel_path = vm_dir + kernel_name
    if download( kernel_uri, kernel_path ) == False :
        raise Exception("Download kernel %s failed..." % kernel_uri)

    return kernel_path

def prepare_image(vm_dir, disk_size_gb, image_name):
    ''' download image '''
    image_uri = repository_url + 'prototype/' + image_name
    image_path = vm_dir + image_name # image_name might be xxxx-prototype.img
    if download( image_uri, image_path ) == False :
        raise Exception("Download image %s failed..." % img_uri)

    ''' resize image '''
    if resize_image( image_path, disk_size_gb) == False :
        print("Resize fail... Use original size of prototype image.")
    return image_path


def clean_kernel_file( kernel_path ):
    remove_file( kernel_path )

def clean_image_file( image_path ):
    remove_file( image_path )

def clean_config_file( xml_path ):
    backup_file( xml_path )


def check_vm(vm_name):
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


if __name__ == '__main__' :
    username = 'ot32em'
#    vm_name = 'ot32em-1-1'
    config = { 'cpu':'1', 'memory':'512', 'disk':'8' }
    for i in range(1,2,1):
        create_gentoo( username, 1, i, config ) 
    
