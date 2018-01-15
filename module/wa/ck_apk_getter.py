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
        r_version = kwargs.get('version', getattr(resource, 'version', None))
        alt_abi = None
        if resource.owner.device.abi in ['arm64-v8','arm64']:
            alt_abi = 'armeabi'
        if resource.owner.device.abi in ['x86_64']:
            alt_abi = 'x86'
        for apk in r['dict']['apks']:
            if r_version is not None and apk['version'] != r_version:
                continue
            if resource.owner.device.abi in apk['abis']:
                return os.path.join(path,apk['apk_name'])
            if alt_abi is not None and alt_abi in apk['abis']:
                return os.path.join(path,apk['apk_name'])
        self.logger.error("Failed to find APK for {} / {} / {}".format(
                            resource.owner.package,
                            r_version,
                            resource.owner.device.abi))
        return None
