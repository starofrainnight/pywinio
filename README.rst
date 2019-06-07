=======
pywinio
=======

.. image:: https://img.shields.io/pypi/v/pywinio.svg
    :target: https://pypi.python.org/pypi/pywinio

.. image:: https://ci.appveyor.com/api/projects/status/github/starofrainnight/pywinio?svg=true
    :target: https://ci.appveyor.com/project/starofrainnight/pywinio

A wrapper library for WinIO

Thanks for the great WinIO library which comes from Yariv Kaplan.

The WinIO library binary distribution will be accessed from winiobinary package.

This library may not work as expected after win10, because the WinIO project seems abandoned by it's original author and we have no proper rights to update it unless we write another one from ground. So this library may not works if Windows changed the API or principle which the WinIO project base on.

NOTE: This library has been renamed from 'rabird.winio' to 'pywinio' after 0.3.0 .

* License: Apache-2.0

Usage
-----

* Keyboard Emulation

 NOTICE: You must have a ps/2 keyboard connected to your PC if you test on win10 or later, otherwise this sample won't works!

::

    import pywinio
    import time
    import atexit

    # KeyBoard Commands
    # Command port
    KBC_KEY_CMD	= 0x64
    # Data port
    KBC_KEY_DATA = 0x60

    g_winio = None

    def get_winio():
    	global g_winio

    	if g_winio is None:
    		g_winio = pywinio.WinIO()
    		def __clear_winio():
    			global g_winio
    			g_winio = None
    		atexit.register(__clear_winio)

    	return g_winio

    def wait_for_buffer_empty():
    	'''
    	Wait keyboard buffer empty
    	'''

    	winio = get_winio()

    	dwRegVal = 0x02
    	while (dwRegVal & 0x02):
    		dwRegVal = winio.get_port_byte(KBC_KEY_CMD)

    def key_down(scancode):
    	winio = get_winio()

    	wait_for_buffer_empty();
    	winio.set_port_byte(KBC_KEY_CMD, 0xd2);
    	wait_for_buffer_empty();
    	winio.set_port_byte(KBC_KEY_DATA, scancode)

    def key_up(scancode):
    	winio = get_winio()

    	wait_for_buffer_empty();
    	winio.set_port_byte( KBC_KEY_CMD, 0xd2);
    	wait_for_buffer_empty();
    	winio.set_port_byte( KBC_KEY_DATA, scancode | 0x80);

    def key_press(scancode, press_time = 0.2):
    	key_down( scancode )
    	time.sleep( press_time )
    	key_up( scancode )


    # Press 'A' key
    # Scancodes references : https://www.win.tue.nl/~aeb/linux/kbd/scancodes-1.html
    key_press(0x1E)

FAQ
---------------------------

How to emulate a mouse?
==========================

This library just the API wrapper of WinIO, I give a sample about keyboard emulation just for showing the wrapper works. And WinIO is a library provied directly access I/O ports and physical memory. That's all.

I don't know the details about how the mouse works, so if you want to emulate the mouse just go by yourself.

Tips: If you are testing on Win10 or later, you MUST have a real ps/2 mouse connected (same as the situation of keyboard emulation - I guess).

If it can do sth...?
==========================

Oh, this wrapper can either if winio can. But at first, you must be familiar with the things you want to do and how the winio works.

Privilege Requirements
-----------------------

WinIo requires administrative privileges to run properly. This can be achieved by:

* Using WinIo from a service running as LocalSystem (SE_LOAD_DRIVER_NAME privilege must be explicitly enabled).
* Embedding a manifest file in the application that requests privilege elevation.
* Requiring the user to choose the "Run as Administrator" option when launching the application.

The included C# samples demonstrate using an embedded manifest file to request privilege elevation.

Driver Signing Requirements on 64-bit Systems
---------------------------------------------

64-bit versions of Windows only load device drivers that are signed by a code signing certificate issued by a public CA such as Verisign, Thawte, etc. WinIo64.sys must not be deployed on production machines unless a code signing certificate is obtained and used to sign this file. The bundled copy of WinIo64.sys is signed with a self-signed certificate and can only be used on development/test machines with Windows running in a special "test" mode. In order to use the bundled version of WinIo64.sys, you need to take the following steps:

* Open an elevated command window by right-clicking the icon and clicking "Run as Administrator".
* Type the following command to enable test-signing:

 ::

  bcdedit.exe /set TESTSIGNING ON

* Reboot the machine

For more information on Windows driver signing requirements, please refer to http://www.microsoft.com/whdc/winlogo/drvsign/kmcs_walkthrough.mspx.

Licenses
---------------------------------------------

This library was licensed under Apache-2.0 which already descripted in LICENSE

WinIO library's license descripted in LICENSE-WINIO
