Allows you to interact with the connected / emulated device, list APKs, pull them to a directory, and decompile the code via JADX

## Requirements
You must install the following binaries for this to work: 
* [jadx](https://github.com/skylot/jadx)
* [adb](https://developer.android.com/studio)
* termcolor (a python library) - `pip install termcolor`

## Usage 
### Help 
```sh
python apk_puller.py -h
usage: apk_puller.py [-h] [-p PACKAGE] [-l] [-f FILTER] [-o OUTPUT_DIR]

Pull APK from connected Android device and decompile it.

options:
  -h, --help            show this help message and exit
  -p PACKAGE, --package PACKAGE
                        The package name of the app to pull and decompile.
  -l, --list-packages   List all installed packages on the connected device.
  -f FILTER, --filter FILTER
                        Filter string to narrow down listed packages.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory to save the extracted APK contents.
```
### Example usage
```
python3 apk_puller.py -p nord                                                                                                                                                              
Found matching packages:                                                                                                                                                                      
        > /data/app/~~EPSCYS5tnYJ9n5JVlTZ7Ug==/com.nordvpn.android-YFol8E0yb7yg3SKnX7Zi0Q==/base.apk=com.nordvpn.android                                                                      
        > /data/app/~~0xC0ehgzj_Rh-u1aSMFcIQ==/com.nordpass.android.app.password.manager-YdHLGpKHNrHuktx_Mt-TZQ==/base.apk=com.nordpass.android.app.password.manager                          
        > /data/app/~~96_wkej26xaEn8jBk4yusw==/com.nordlocker.android.encrypt.cloud-MmrnhoZxIMdOc9jYcU2KMA==/base.apk=com.nordlocker.android.encrypt.cloud                                    
Press (Y/y) and Enter to continue: y                                                                                                                                                          
/data/app/~~EPSCYS5tnYJ9n5JVlTZ7Ug==/com.nordvpn.android-YFol8E0yb7yg3SKnX7Zi0Q==/base.apk: 1 file pulled, 0 skipped. 185.1 MB/s (37924214 bytes in 0.195s)                                   
Pulled APK to mobile_dump/apk_dump/com.nordvpn.android.apk                                                                                                                                    
INFO  - loading ...                                                                                                                                                                           
INFO  - processing ...                                                                                                                                                                        
ERROR - finished with errors, count: 47                                                                                                                                                       
Decompiled APK to mobile_dump/decompiled/com.nordvpn.android/                                                                                                                                 
...
```
