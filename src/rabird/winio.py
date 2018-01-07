import os
import sys
import ctypes
import atexit
import win32api
import win32con
import win32file
import winioctlcon
import pywintypes
import win32service
import locale
import logging
import ctypes
import struct

__author__ = """Hong-She Liang"""
__email__ = 'starofrainnight@gmail.com'
__version__ = '0.1.15'

# Define the various device type values.  Note that values used by Microsoft
# Corporation are in the range 0-32767, and 32768-65535 are reserved for use
# by customers.

FILE_DEVICE_WINIO = 0x00008010

# Macro definition for defining IOCTL and FSCTL function control codes.
# Note that function codes 0-2047 are reserved for Microsoft Corporation,
# and 2048-4095 are reserved for customers.

WINIO_IOCTL_INDEX = 0x810

# Define our own private IOCTL

IOCTL_WINIO_MAPPHYSTOLIN = winioctlcon.CTL_CODE(FILE_DEVICE_WINIO,
                                                WINIO_IOCTL_INDEX,
                                                winioctlcon.METHOD_BUFFERED,
                                                winioctlcon.FILE_ANY_ACCESS)

IOCTL_WINIO_UNMAPPHYSADDR = winioctlcon.CTL_CODE(FILE_DEVICE_WINIO,
                                                 WINIO_IOCTL_INDEX + 1,
                                                 winioctlcon.METHOD_BUFFERED,
                                                 winioctlcon.FILE_ANY_ACCESS)

IOCTL_WINIO_ENABLEDIRECTIO = winioctlcon.CTL_CODE(FILE_DEVICE_WINIO,
                                                  WINIO_IOCTL_INDEX + 2,
                                                  winioctlcon.METHOD_BUFFERED,
                                                  winioctlcon.FILE_ANY_ACCESS)

IOCTL_WINIO_DISABLEDIRECTIO = winioctlcon.CTL_CODE(FILE_DEVICE_WINIO,
                                                   WINIO_IOCTL_INDEX + 3,
                                                   winioctlcon.METHOD_BUFFERED,
                                                   winioctlcon.FILE_ANY_ACCESS)

IOCTL_WINIO_READPORT = winioctlcon.CTL_CODE(FILE_DEVICE_WINIO,
                                            WINIO_IOCTL_INDEX + 4,
                                            winioctlcon.METHOD_BUFFERED,
                                            winioctlcon.FILE_ANY_ACCESS)

IOCTL_WINIO_WRITEPORT = winioctlcon.CTL_CODE(FILE_DEVICE_WINIO,
                                             WINIO_IOCTL_INDEX + 5,
                                             winioctlcon.METHOD_BUFFERED,
                                             winioctlcon.FILE_ANY_ACCESS)


# Error Codes
EC_FILE_NOT_FOUND = 2
EC_SERVICE_FILE_NOT_FOUND = 3
EC_SERVICE_NOT_INSTALLED = 1060
EC_SERVICE_NOT_STARTED = 1062
EC_SERVICE_EXISTED = 1073


def NotInitializedError(RuntimeError):
    pass


def InvalidArgumentError(ValueError):
    pass


def DeviceIoControlError(RuntimeError):
    pass


class tagPhysStruct(ctypes.Structure):
    _fields_ = [
        ('dwPhysMemSizeInBytes', ctypes.c_ulonglong),
        ('pvPhysAddress', ctypes.c_ulonglong),
        ('PhysicalMemoryHandle', ctypes.c_ulonglong),
        ('pvPhysMemLin', ctypes.c_ulonglong),
        ('pvPhysSection', ctypes.c_ulonglong),
    ]
    _pack_ = 1


class tagPortStruct(ctypes.Structure):
    _fields_ = [
        ('wPortAddr', ctypes.c_ushort),
        ('dwPortVal', ctypes.c_ulong),
        ('bSize', ctypes.c_ubyte),
    ]
    _pack_ = 1


def _ensure_initialized(method):
    def wrapper(self, *args, **kwargs):
        if not self.dll_is_initialized:
            raise NotInitializedError()
        return method(self, *args, **kwargs)
    return wrapper


class WinIO(object):
    # Rewrote __new__ for Singleton design.

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(WinIO, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        self.dll_is_initialized = False
        self.hSCManager = win32service.OpenSCManager(
            None, None, win32service.SC_MANAGER_ALL_ACCESS)
        self.hDriver = None
        self.__is_need_uninstall_driver = True
        self.__initialize()

    def __stop_driver(self):
        hService = None
        ServiceStatus = None

        hService = win32service.OpenService(
            self.hSCManager, 'WINIO', win32service.SERVICE_ALL_ACCESS)
        try:
            ServiceStatus = win32service.ControlService(
                hService, win32service.SERVICE_CONTROL_STOP)
        except pywintypes.error as e:
            if e.winerror == EC_SERVICE_NOT_STARTED:
                return
            else:
                raise e

    @_ensure_initialized
    def __get_port_value(self, wPortAddr, bSize):
        if bSize not in [1, 2, 4]:
            raise InvalidArgumentError(
                'Argument "bSize" only accept 1, 2, 4. Current value : %s!' % (str(bSize)))

        # If this is a 64 bit OS, we must use the driver to access I/O ports even
        # if the application is 32 bit
        if self.__is_64bit_os():
            PortStruct = tagPortStruct()
            PortStruct.bSize = bSize
            PortStruct.wPortAddr = wPortAddr

            return struct.unpack('@L',
                                 win32file.DeviceIoControl(
                                     self.hDriver,
                                     IOCTL_WINIO_READPORT,
                                     memoryview(PortStruct),
                                     4))[0]
        else:
            if bSize == 1:
                return ctypes.c_ubyte(ctypes.cdll.msvcrt._inp(ctypes.c_ushort(wPortAddr))).value
            elif bSize == 2:
                return ctypes.c_ushort(ctypes.cdll.msvcrt._inpw(ctypes.c_ushort(wPortAddr))).value
            elif bSize == 4:
                return ctypes.c_ulong(ctypes.cdll.msvcrt._inpd(ctypes.c_ushort(wPortAddr))).value

    def get_port_byte(self, wPortAddr):
        return self.__get_port_value(wPortAddr, 1)

    def get_port_word(self, wPortAddr):
        return self.__get_port_value(wPortAddr, 2)

    def get_port_dword(self, wPortAddr):
        return self.__get_port_value(wPortAddr, 4)

    @_ensure_initialized
    def __set_port_value(self, wPortAddr, dwPortVal, bSize):
        # If this is a 64 bit OS, we must use the driver to access I/O ports even
        # if the application is 32 bit
        if self.__is_64bit_os():
            PortStruct = tagPortStruct()
            PortStruct.bSize = bSize
            PortStruct.dwPortVal = dwPortVal
            PortStruct.wPortAddr = wPortAddr

            win32file.DeviceIoControl(
                self.hDriver,
                IOCTL_WINIO_WRITEPORT,
                memoryview(PortStruct),
                4)
        else:
            if bSize == 1:
                ctypes.cdll.msvcrt._outp(ctypes.c_ushort(
                    wPortAddr), ctypes.c_int(dwPortVal))
            elif bSize == 2:
                ctypes.cdll.msvcrt._outpw(ctypes.c_ushort(
                    wPortAddr), ctypes.c_ushort(dwPortVal))
            elif bSize == 4:
                ctypes.cdll.msvcrt._outpd(ctypes.c_ushort(
                    wPortAddr), ctypes.c_ulong(dwPortVal))

    def set_port_byte(self, wPortAddr, dwPortVal):
        return self.__set_port_value(wPortAddr, dwPortVal, 1)

    def set_port_word(self, wPortAddr, dwPortVal):
        return self.__set_port_value(wPortAddr, dwPortVal, 2)

    def set_port_dword(self, wPortAddr, dwPortVal):
        return self.__set_port_value(wPortAddr, dwPortVal, 4)

    @_ensure_initialized
    def map_phys_to_lin(self, PhysStruct):
        if (not win32file.DeviceIoControl(
                self.hDriver,
                IOCTL_WINIO_MAPPHYSTOLIN,
                memoryview(PhysStruct),
                memoryview(PhysStruct))):
            raise DeviceIoControlError("Failed on IOCTL_WINIO_MAPPHYSTOLIN")

        return PhysStruct.pvPhysMemLin

    @_ensure_initialized
    def unmap_physical_memory(self, PhysStruct):
        if (not win32file.DeviceIoControl(
                self.hDriver,
                IOCTL_WINIO_UNMAPPHYSADDR,
                memoryview(PhysStruct),
                None)):
            raise DeviceIoControlError("Failed on IOCTL_WINIO_UNMAPPHYSADDR")

    @_ensure_initialized
    def get_phys_long(self, pbPhysAddr):
        PhysStruct = tagPhysStruct()
        PhysStruct.pvPhysAddress = pbPhysAddr
        PhysStruct.dwPhysMemSizeInBytes = 4

        pdwLinAddr = self.map_phys_to_lin(PhysStruct)
        dwLinAddrRaw = bytes(
            (ctypes.c_char * 4).from_address(pdwLinAddr.value))
        dwPhysVal = struct.unpack('@L', dwLinAddrRaw)

        self.unmap_physical_memory(PhysStruct)

        return dwPhysVal

    @_ensure_initialized
    def set_phys_long(self, pbPhysAddr, dwPhysVal):
        PhysStruct = tagPhysStruct()
        PhysStruct.pvPhysAddress = pbPhysAddr
        PhysStruct.dwPhysMemSizeInBytes = 4

        pdwLinAddr = self.map_phys_to_lin(PhysStruct)
        if (pdwLinAddr == 0):
            raise ValueError("Linear address invalid!")

        data = ctypes.cast(
            ctypes.c_void_p(pdwLinAddr.value),
            ctypes.POINTER(ctypes.c_ulong))
        data.contents.value = dwPhysVal

        self.unmap_physical_memory(PhysStruct)

    def uninstall_driver(self):
        hService = None
        pServiceConfig = None
        dwBytesNeeded = 0
        cbBufSize = 0

        try:
            self.__stop_driver()

            hService = win32service.OpenService(
                self.hSCManager, 'WINIO', win32service.SERVICE_ALL_ACCESS)

            # If QueryServiceConfig() can not return a correct config, it will
            # throw exception!
            pServiceConfig = win32service.QueryServiceConfig(hService)

            # If service is set to load automatically, don't delete it!
            # dwStartType
            if (pServiceConfig[1] == win32service.SERVICE_DEMAND_START):
                win32service.DeleteService(hService)

        except pywintypes.error as e:
            if e.winerror == EC_SERVICE_NOT_INSTALLED:
                return

            raise

    def install_driver(self, pszWinIoDriverPath, IsDemandLoaded):
        hService = None

        # Remove any previous instance of the driver
        self.uninstall_driver()

        # Install the driver
        if (IsDemandLoaded == True):
            demand_flags = win32service.SERVICE_DEMAND_START
        else:
            demand_flags = win32service.SERVICE_SYSTEM_START

        try:
            hService = win32service.CreateService(self.hSCManager,
                                                  "WINIO",
                                                  "WINIO",
                                                  win32service.SERVICE_ALL_ACCESS,
                                                  win32service.SERVICE_KERNEL_DRIVER,
                                                  demand_flags,
                                                  win32service.SERVICE_ERROR_NORMAL,
                                                  pszWinIoDriverPath,
                                                  None,
                                                  0,
                                                  None,
                                                  None,
                                                  None)
        except pywintypes.error as e:
            if e.winerror == EC_SERVICE_EXISTED:  # Service existed!
                return True

            raise

    def __start_driver(self):
        hService = None
        bResult = True

        hService = win32service.OpenService(
            self.hSCManager, "WINIO", win32service.SERVICE_ALL_ACCESS)
        win32service.StartService(hService, None)

    def __is_64bit_os(self):
        if 'PROCESSOR_ARCHITEW6432' in os.environ:
            if os.environ['PROCESSOR_ARCHITEW6432'] == 'AMD64':
                return True

        if "64" in os.environ["PROCESSOR_ARCHITECTURE"]:
            return True

        return False

    def __get_driver_file_path(self):
        # Find the data directory
        while True:
            # If we installed by pip, the data directory will be ../../../data
            pywinio_module_dir = os.path.join(
                os.path.dirname(__file__), '../../..', 'data')
            if os.path.exists(os.path.join(pywinio_module_dir, "WinIo32.sys")):
                break

            # If we installed by easy_install, the data directory will be
            # ../data
            pywinio_module_dir = os.path.join(
                os.path.dirname(__file__), '..', 'data')
            if os.path.exists(os.path.join(pywinio_module_dir, "WinIo32.sys")):
                break

            break

        if self.__is_64bit_os():
            result = os.path.join(pywinio_module_dir, 'WinIo64.sys')
        else:
            result = os.path.join(pywinio_module_dir, 'WinIo32.sys')

        result = os.path.normpath(os.path.realpath(result))

        return result

    def __initialize(self):
        # Try to open the winio device.
        hDriver = None
        try:
            hDriver = win32file.CreateFile(r"\\.\WINIO",
                                           win32con.GENERIC_READ | win32con.GENERIC_WRITE,
                                           0,
                                           None,
                                           win32con.OPEN_EXISTING,
                                           win32con.FILE_ATTRIBUTE_NORMAL,
                                           None)

            # Driver already installed in system as service by user, we must
            # not uninstall it.
            self.__is_need_uninstall_driver = False
        except pywintypes.error as e:
            if e.winerror != EC_FILE_NOT_FOUND:
                raise e

        # If the driver is not running, install it
        if hDriver is None:
            self.install_driver(self.__get_driver_file_path(), True)
            self.__start_driver()

            hDriver = win32file.CreateFile(r"\\.\WINIO",
                                           win32con.GENERIC_READ | win32con.GENERIC_WRITE,
                                           win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                                           None,
                                           win32con.OPEN_EXISTING,
                                           win32con.FILE_ATTRIBUTE_NORMAL,
                                           None)

        # Enable I/O port access for this process if running on a 32 bit OS
        if not self.__is_64bit_os():
            win32file.DeviceIoControl(
                hDriver, IOCTL_WINIO_ENABLEDIRECTIO, None, 4)

        self.hDriver = hDriver
        self.dll_is_initialized = True

    def __finalize(self):
        if self.hDriver is not None:
            # Disable I/O port access if running on a 32 bit OS
            if not self.__is_64bit_os():
                win32file.DeviceIoControl(
                    self.hDriver, IOCTL_WINIO_DISABLEDIRECTIO, None, 4)

            self.hDriver = None

        if self.__is_need_uninstall_driver:
            self.uninstall_driver()

        dll_is_initialized = False

    def __del__(self):
        if self.dll_is_initialized:
            self.__finalize()
