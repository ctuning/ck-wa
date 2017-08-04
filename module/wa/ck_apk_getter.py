from wlauto import ResourceGetter
import ck.kernel as ck
import os.path

class CkApkGetter(ResourceGetter):

    name = 'ck_apk_getter'
    resource_type = 'apk'

    def get(self, resource, **kwargs):
        # Return path to the APK for Workload resource.owner.name
        if (resource.uiauto):
            return None
        # Remember if debugging/changing to use self.logger.debug as below
        # self.logger.debug(dir(resource.owner))
        r = ck.access({'module_uoa':'apk',
                       'action':'load',
                       'data_uoa':resource.owner.package})
        path = r['path']
        for apk in r['dict']['apks']:
            if apk['version'] == resource.owner.version:
                if resource.owner.device.abi in apk['abis']:             
                    return os.path.join(path,apk['apk_name'])        
        self.logger.error("Failed to find APK for {} / {} / {}".format(
                            resource.owner.package,
                            resource.owner.version,
                            resource.owner.device.abi))
        return None
