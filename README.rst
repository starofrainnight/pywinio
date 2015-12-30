rabird.winio
-----------------

A wrapper library for winio .

Thanks for the great WinIO library which comes from Yariv Kaplan.

The WinIO library binary distribution will download from http://www.internals.com/ during setup.

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

bcdedit.exe /set TESTSIGNING ON
 
* Reboot the machine 
 
For more information on Windows driver signing requirements, please refer to http://www.microsoft.com/whdc/winlogo/drvsign/kmcs_walkthrough.mspx.

Licenses
===============

This library used MIT license which already descripted in LICENSE.txt

WinIO library's license descripted in LICENSE-WINIO.txt 
