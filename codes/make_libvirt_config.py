from xml.etree.ElementTree import Element, ElementTree, SubElement, dump, tostring



def make_xen_domain_node(vm_name, vm_cpu, vm_memory, vm_image_fullpath, vm_kernel_fullpath):
    domain = Element('domain', { 'type':'xen'})

    name = SubElement( domain, 'name')
    name.text = vm_name
    memory = SubElement( domain, 'memory', { 'unit':'MiB'} )
    memory.text = vm_memory
    vcpu = SubElement( domain, 'vcpu', {'placement':'static'} )
    vcpu.text=vm_cpu


    os = make_os_node(vm_kernel_fullpath, vm_name) 
    domain.append(os)

    clock = SubElement(domain, 'clock', {'offset':'utc', 'adjustment':'reset' } )
    on_poweroff = SubElement(domain, 'on_poweroff')
    on_poweroff.text='destroy'
    on_reboot = SubElement(domain, 'on_reboot')
    on_reboot.text='restart'
    on_crash = SubElement(domain, 'on_crash')
    on_crash.text='restart'

    domain.append(make_devices_node(vm_image_fullpath))
    return domain

def make_os_node(vm_kernel_fullpath, vm_name):
    os = Element('os')
    type = SubElement(os, 'type', { 'arch':'x86_64', 'machine':'xenpv' } )
    type.text = 'linux'
    kernel = SubElement(os, 'kernel')
    kernel.text= vm_kernel_fullpath
    cmdline = SubElement(os, 'cmdline')
    cmdline.text='root=/dev/xvda1 ro console=hvc0 xencons=tty ip=::::%s::dhcp' % vm_name

    return os

def make_devices_node(vm_image_fullpath):
    devices = Element('devices')
    devices.append( make_disk_node(vm_image_fullpath) )
    devices.append( make_if_node() )
    devices.append( make_console_node() )
    return devices

def make_disk_node(vm_image_fullpath):
    disk = Element('disk', { 'type':'file', 'device':'disk'} )
    driver = SubElement( disk, 'driver', {'name':'tap2'} )
    source = SubElement( disk, 'source', {'file':vm_image_fullpath } )
    target = SubElement( disk, 'target', {'dev':'xvda1', 'bus':'xen'} )

    return disk

def make_if_node():
    interface = Element('interface', { 'type':'bridge' } )
    source = SubElement( interface, 'source', { 'bridge':'virbr0' } )

    return interface

def make_console_node():
    console = Element('console', {'type':'pty'} )
    target = SubElement( console, 'target', {'type':'xen', 'port':'0' } )

    return console


''' xml pretty print tool '''
def indent(elem, level=0):
    i= "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i+ " "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent( elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else :
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail=i

def make_xen_libvirt_config(xml_fullpath, vm_name, vm_cpu, vm_memory, vm_image_fullpath, vm_kernel_fullpath):
    domain = make_xen_domain_node(vm_name, vm_cpu, vm_memory, vm_image_fullpath, vm_kernel_fullpath)
    indent(domain)
    tree = ElementTree( domain )
    tree.write(xml_fullpath)
