
# The thin-deploy daemon assumes master have made sure my machine has enough resource to deploy

# @
# @var dict:configs - a dictionary which key as subid, value as vm 
#      config of the subid.
#


def boot_group_vms( username, groupid, subids, boot_depend, configs ):
    download( os_types )

    make_dir( username, groupid, subids, os_types )
    copy( username, groupid, subids, os_types )

    make_vm_config_xml( username, groupid, subids, configs )

    # example of boot_depend
    # a = [[2,3,4],[8,9],[10,11]]
    # [8,9] will wait [2,3,4] is completed, [10,11] will wait [8,9] is completed
    # in [], the 2,3,4 will boot parallelly, 

    for i_round in boot_depend :
        wait_event = Event()
        for vm_subid in i_round :
            parallel_booting( vm_subid, wait_event )

        wait_event.block( if n > len( i_round ) )


    post_boot( )
    add_sshport( username, groupid, subids )

        





    

    

