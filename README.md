pyconcrete maya
==============

Protect your python script, encrypt .pyc to .pye and decrypt when import it

--------------


Protect python script work flow
--------------
* your_script.py `import pyconcrete`
* pyconcrete will hook import module
* when your script do `import MODULE`, pyconcrete import hook will try to find `MODULE.pye` first
  and then decrypt `MODULE.pye` via `_pyconcrete.pyd` and execute decrypted data (as .pyc content)
* encrypt & decrypt secret key record in `_pyconcrete.pyd` (like DLL or SO)
  the secret key would be hide in binary code, can't see it directly in HEX view


Encryption
--------------
* only support AES 128 bit now
* encrypt & decrypt by library OpenAES


Installation
--------------
  * need to input your passphrase create secret key for encrypt python script.
  * same passphrase will generate the same secret key
  * installation will add `pyconcrete.pth` into your `site-packages` for execute `sitecustomize.py` under pyconcrete which will automatic import pyconcrete

Build
--------------
```
Visual Studio 2010 (VS10): SET VS90COMNTOOLS=%VS100COMNTOOLS%
Visual Studio 2012 (VS11): SET VS90COMNTOOLS=%VS110COMNTOOLS%
Visual Studio 2013 (VS12): SET VS90COMNTOOLS=%VS120COMNTOOLS%
Visual Studio 2015 (VS14): SET VS90COMNTOOLS=%VS140COMNTOOLS%
set VS90COMNTOOLS=%VS140COMNTOOLS%



# Maya2023
set PYCONCRETE_PASSPHRASE='1111"
set EXTRA_INCLUDE_DIRS=C:/Program Files/Autodesk/Maya2023/include/Python39/Python
set EXTRA_LIBRARIES=C:/Program Files/Autodesk/Maya2023/lib
"C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe" setup.py build 

# Maya2022 py2
set PYCONCRETE_PASSPHRASE='1111"
set EXTRA_INCLUDE_DIRS=C:/Program Files/Autodesk/Maya2022/include/Python27/Python
set EXTRA_LIBRARIES=C:/Program Files/Autodesk/Maya2022/lib
"C:\Program Files\Autodesk\Maya2022\bin\mayapy2.exe" setup.py build 

# Maya2022 py3
set PYCONCRETE_PASSPHRASE='1111"
set EXTRA_INCLUDE_DIRS=C:/Program Files/Autodesk/Maya2022/include/Python37/Python
set EXTRA_LIBRARIES=C:/Program Files/Autodesk/Maya2022/lib
"C:\Program Files\Autodesk\Maya2022\bin\mayapy.exe" setup.py build 

# Maya2019 py2
set PYCONCRETE_PASSPHRASE='1111"
set EXTRA_INCLUDE_DIRS=C:/Program Files/Autodesk/Maya2019/include/python2.7
set EXTRA_LIBRARIES=C:/Program Files/Autodesk/Maya2019/lib
"C:\Program Files\Autodesk\Maya2019\bin\mayapy.exe" setup.py build 




import pyconcrete
import py_compile
py_file = r"C:\Users\Admin\Documents\maya\2022\scripts\pytest.py"

pyc_file = py_file + 'c'
pye_file = py_file + 'e'
pyc_exists = exists(pyc_file)
py_compile.compile(py_file, cfile=pyc_file)
pyconcrete.encrypt_file(pyc_file, pye_file)

```


Usage
--------------

### Full encrypted
* convert all of your `.py` to `*.pye`
```sh
$ pyconcrete-admin.py compile --source=<your py script>  --pye
$ pyconcrete-admin.py compile --source=<your py module dir> --pye
```

* remove `*.py` `*.pyc` or copy `*.pye` to other folder
* *main*.py encrypted as *main*.pye, it can't be executed by normal `python`.
You must use `pyconcrete` to process the *main*.pye script.
`pyconcrete`(*exe*) will be installed in your system path (ex: /usr/local/bin)

```sh
pyconcrete main.pye
src/*.pye  # your libs
```


### Partial encrypted (pyconcrete as lib)
* download pyconcrete source and install by setup.py
```sh
$ python setup.py install \
  --install-lib=<your project path> \
  --install-scripts=<where you want to execute pyconcrete-admin.py and pyconcrete(exe)>
```

* import pyconcrete in your main script
  * recommendation project layout
```sh
main.py       # import pyconcrete and your lib
pyconcrete/*  # put pyconcrete lib in project root, keep it as original files
src/*.pye     # your libs
```


Test
--------------
* test in local
```sh
$ ./pyconcrete-admin.py test
```


