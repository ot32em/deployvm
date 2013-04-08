import deploy

from constant import *
def setup():
    bgv = deploy.BootGroupVm()
    test_config = {}
    test_config['prototype_filenames']= {
        PROTOTYPE_GENTOO:'100mb.img',
        PROTOTYPE_APACHE:'100mb.img',
        PROTOTYPE_UBUNTU_12_04:'100mb.img',
    }
    bgv.overwrite_config(test_config)


def test_vm_dir():
    assert False

def test_make_failed_log_dir():
    assert False

def test_group_vm_download_dir():
    assert False

def test_download_image():
    assert False

def test_make_directories():
    assert False

def test_copy_images():
    assert False


def test_resize_images():
    assert False

def test_make_libvirt_xmls():
    assert False

def test_boot_vm():
    assert False

def test_post_booting():
    assert False
