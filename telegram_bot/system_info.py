import platform

class BasicSystemInfo:

    def getSysInfo(self):
        sysInfo = f"{platform.machine()} - {platform.version()}"
        return sysInfo    