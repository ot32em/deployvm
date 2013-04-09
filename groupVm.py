import os

class GroupVm:
    def __init__(self, username, groupid, vms_parameters):
        self._username = username
        self._groupid = groupid
        self._vms_parameters = vms_parameters
        self._subids = vms_parameters.keys()

    def username(self):
        return self._username
    def groupid(self):
        return self._groupid
    def subids(self):
        return self._subids

    def vm_prototype(self, subid):
        return self._vms_parameters[subid]['prototype']
    def vm_cpu(self,subid):
        return self._vms_parameters[subid]['cpu']
    def vm_memory(self,subid):
        return self._vms_parameters[subid]['memory']
    def vm_disk(self,subid):
        return self._vms_parameters[subid]['disk']

    def vm_name(self, subid):
        return '%s-%s-%s' % (self.username(), self.groupid(), subid)

    def group_name(self):
        return '%s-%s' % (self._username, self._groupid)
    def prefix(self):
        return self.group_name() + '-'


    def vm_dir(self, deploy_prototype_fullpath, subid):
        return os.path.join( deploy_prototype_fullpath, self.username(), self.vm_name(subid))

    def unique_prototypes(self):
        prototypes = set()
        for subid in self._vms_parameters :
            prototypes.add( self.vm_prototype( subid ) )
        return list(prototypes) # set type will kick the same contents


