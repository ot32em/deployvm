
step1: listen a username + group set vm , create vm order


step2: setup the files of group of vms 
    
    1. download via unicast or btitorrent to download the image in this machine.

    2. copy image to each vm directory

        2.2.1 make directory if not exists

step3: booting vm with order if specificed
    
    1. setup libvirt config file coording vm's congiguration about OStype, cpu amount, memory size, disk size

    2. schedule the booting seqence accoring its booting order

        example: some slave vm need depend on master to get some setup information  when they are booting.


    == question: how to determine a vm is booting complete or not
        
        a. use event sync, 
            let the booting thread trigger the complete event when it booted the vm booted.
            pros: quick, easy
            cons: not sure the touchable
        b. use ping to ping each port
            pros: slow, not elegant
            cons: sure the touchable
        c. inject some rc.local code in each vm image
            pros: quick, sure the touchable
            cons: it's diffulte to mofity the rc.local codes..

    3.3 checking all the vm booted succesfully and reboot again...

step4: report booting status to Database

step5: boot fail handling
    
    clean all


