rabird.winio
========================

A wrapper library for winio .

Thanks for the great WinIO library which comes from Yariv Kaplan.

The WinIO library binary distribution will download from http://www.internals.com/ during setup.

Usage
========================

* Keyboard Emulation

::
  
    import rabird.winio
    import time
    import atexit
    
    # KeyBoard Commands
    # Command port
    KBC_KEY_CMD	= 0x64
    # Data port
    KBC_KEY_DATA = 0x60
    
    __winio = None
    
    def __get_winio():
    	global __winio
    	
    	if __winio is None:
    		__winio = rabird.winio.WinIO()
    		def __clear_winio():
    			global __winio
    			__winio = None
    		atexit.register(__clear_winio)
    		
    	return __winio	
    
    def wait_for_buffer_empty():
    	'''
    	Wait keyboard buffer empty
    	'''
    	
    	winio = __get_winio()
    	
    	dwRegVal = 0x02
    	while (dwRegVal & 0x02):
    		dwRegVal = winio.get_port_byte(KBC_KEY_CMD)
    		
    def key_down(scancode):
    	winio = __get_winio()
    	
    	wait_for_buffer_empty();
    	winio.set_port_byte(KBC_KEY_CMD, 0xd2);
    	wait_for_buffer_empty();
    	winio.set_port_byte(KBC_KEY_DATA, scancode)
    
    def key_up(scancode):
    	winio = __get_winio()
    	
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


Privilege Requirements
========================
 
WinIo requires administrative privileges to run properly. This can be achieved by:
 
* Using WinIo from a service running as LocalSystem (SE_LOAD_DRIVER_NAME privilege must be explicitly enabled). 
* Embedding a manifest file in the application that requests privilege elevation. 
* Requiring the user to choose the "Run as Administrator" option when launching the application.
 
The included C# samples demonstrate using an embedded manifest file to request privilege elevation. 
 
Driver Signing Requirements on 64-bit Systems
=================================================

64-bit versions of Windows only load device drivers that are signed by a code signing certificate issued by a public CA such as Verisign, Thawte, etc. WinIo64.sys must not be deployed on production machines unless a code signing certificate is obtained and used to sign this file. The bundled copy of WinIo64.sys is signed with a self-signed certificate and can only be used on development/test machines with Windows running in a special "test" mode. In order to use the bundled version of WinIo64.sys, you need to take the following steps:
 
* Open an elevated command window by right-clicking the icon and clicking "Run as Administrator". 
* Type the following command to enable test-signing:

 ::
 
  bcdedit.exe /set TESTSIGNING ON
 
* Reboot the machine 
 
For more information on Windows driver signing requirements, please refer to http://www.microsoft.com/whdc/winlogo/drvsign/kmcs_walkthrough.mspx.

Licenses
===============

This library used MIT license which already descripted in LICENSE.txt

WinIO library's license descripted in LICENSE-WINIO.txt 
