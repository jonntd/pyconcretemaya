#!/usr/bin/env python
#
# Copyright 2015 Falldog Hsieh <falldog7@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import atexit
import hashlib
import imp
import os
import sys
import sysconfig
from distutils.command.build import build
from distutils.command.build_ext import build_ext
from distutils.command.clean import clean
from distutils.command.install import install
from distutils.core import Command, Extension, setup
from distutils.dist import Distribution
from os.path import join

from src.config import EXE_SRC_DIR, EXT_SRC_DIR, PASSPHRASE_ENV, PY_SRC_DIR, SECRET_HEADER_PATH, SRC_DIR, TEST_DIR

version_mod = imp.load_source('version', join(PY_SRC_DIR, 'version.py'))
version = version_mod.__version__
secret_key_header_created = False

PY2 = sys.version_info.major < 3

# .rst should created by pyconcrete-admin
if os.path.exists('README.rst'):
	readme_path = 'README.rst'
else:
	readme_path = 'README.md'
with open(readme_path, 'r') as f:
	readme = f.read()

try:
	input = raw_input
except NameError:
	pass


def is_mingw():
	"""Compiler is mingw."""
	dst = Distribution()
	dst.parse_config_files()
	if 'build' not in dst.command_options:
		return False
	_build = dst.command_options['build']
	if 'compiler' not in _build:
		return False
	compiler = _build['compiler']
	if compiler[1].startswith('mingw'):
		return True
	return False


def is_msvc():
	return sys.platform == 'win32' and not is_mingw()


def is_mac():
	return sys.platform == 'darwin'


def hash_key(key):
	if PY2:
		factor = sum([ord(s) for s in key])
	else:
		factor = sum([s for s in key])
	factor %= 128
	if factor < 16:
		factor += 16

	m = hashlib.md5()
	m.update(key)
	k = m.digest()

	return k, factor


def create_secret_key_header(key, factor):
	# reference from - http://stackoverflow.com/questions/1356896/how-to-hide-a-string-in-binary-code
	# encrypt the secret key in binary code
	# avoid to easy read from HEX view
	global secret_key_header_created
	if secret_key_header_created:
		return

	key_val_lst = []
	for i, k in enumerate(key):
		n = ord(k) if PY2 else k
		key_val_lst.append("(0x%X ^ (0x%X - %d))" % (n, factor, i))
	key_val_code = ", ".join(key_val_lst)

	code = """
        #define SECRET_NUM 0x%X
        #define SECRET_KEY_LEN %d
        static const unsigned char* GetSecretKey()
        {
            unsigned int i = 0;
            static unsigned char key[] = {%s, 0/* terminal char */};
            static int is_encrypt = 1/*true*/;
            if( is_encrypt )
            {
                for(i = 0 ; i < SECRET_KEY_LEN ; ++i)
                {
                    key[i] = key[i] ^ (SECRET_NUM - i);
                }
                is_encrypt = 0/*false*/;
            }
            return key;
        }
    """ % (
		factor,
		len(key),
		key_val_code,
	)

	with open(SECRET_HEADER_PATH, 'w') as f:
		f.write(code)

	secret_key_header_created = True
	atexit.register(remove_secret_key_header)


def remove_secret_key_header():
	pass


# if os.path.exists(SECRET_HEADER_PATH):
#     os.remove(SECRET_HEADER_PATH)


class ExeDistribution(Distribution):
	exe_modules = ()

	def has_exe_modules(self):
		return self.exe_modules and len(self.exe_modules) > 0


# ================================================= command ================================================= #


class CmdBase:
	def pre_process(self):
		if secret_key_header_created:
			return

		if not self.passphrase:
			self.passphrase = os.getenv(PASSPHRASE_ENV)

		if not self.passphrase:
			self.passphrase = input(
				"please input the passphrase \nfor encrypt your python script (enter for default) : \n"
			)
			if len(self.passphrase) == 0:
				raise Exception("empty passphrase is not allow")
			else:
				passphrase2 = input("please input again to confirm\n")
				if self.passphrase != passphrase2:
					raise Exception("Passphrase is different")

		k, f = hash_key(self.passphrase.encode('utf8'))
		create_secret_key_header(k, f)

	def post_process(self):
		pass


class BuildEx(CmdBase, build):
	"""
	execute extra function before/after build.run()
	"""

	user_options = build.user_options + [('passphrase=', None, 'specify passphrase')]

	def initialize_options(self):
		build.initialize_options(self)
		self.passphrase = None

	def run(self):
		self.pre_process()
		ret = build.run(self)
		self.post_process()
		return ret


# ================================================= test command ================================================= #


class TestEx(Command):
	description = "Running all unit test for pyconcrete"
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		import unittest

		suite = unittest.TestLoader().discover(TEST_DIR)
		unittest.TextTestRunner(verbosity=2).run(suite)


# ================================================= extension ================================================= #


def get_include_dirs():
	openaes_include_dirs = [
		join(EXT_SRC_DIR),
		join(EXT_SRC_DIR, 'openaes', 'inc'),
	]
	if is_msvc() and PY2:  # Only Python 2.7 & 3.2 Need VisualStudio 2008 (without stdint.h)
		openaes_include_dirs.append(join(EXT_SRC_DIR, 'include_win'))
	return openaes_include_dirs


def get_libraries(include_python_lib=False):
	libraries = []
	# if sys.version_info.major == 3 and sys.version_info.minor >= 5 and is_msvc():
	# https://stackoverflow.com/questions/32418766/c-unresolved-external-symbol-sprintf-and-sscanf-in-visual-studio-2015
	libraries = ['legacy_stdio_definitions']

	if is_msvc():
		link_py = 'python{0}{1}'.format(sys.version_info.major, sys.version_info.minor)
	else:
		# PEP 3149 -- ABI version tagged .so files
		# link python lib may be: `-l python3.3` or `-l python3.6m`
		# reference link: https://www.python.org/dev/peps/pep-3149/
		link_py_fmt = 'python{version}{abiflags}'
		abiflags = getattr(sys, 'abiflags', '')
		link_py = link_py_fmt.format(
			version=sysconfig.get_python_version(),
			abiflags=abiflags,
		)

	if include_python_lib:
		libraries.append(link_py)

	return libraries


extra_include_dirs = []

if 'EXTRA_INCLUDE_DIRS' in os.environ:
	extra_include_dirs = os.environ['EXTRA_INCLUDE_DIRS'].split(';')
	print("EXTRA_INCLUDE_DIRS: ", extra_include_dirs)

extra_libraries = []

if 'EXTRA_LIBRARIES' in os.environ:
	extra_libraries = os.environ['EXTRA_LIBRARIES'].split(';')
	print("EXTRA_LIBRARIES: ", extra_libraries)

include_dirs = get_include_dirs() + extra_include_dirs

openaes_sources = [
	join(EXT_SRC_DIR, 'openaes', 'src', 'oaes_base64.c'),
	join(EXT_SRC_DIR, 'openaes', 'src', 'oaes_lib.c'),
]

ext_module = Extension(
	'pyconcrete._pyconcrete',
	include_dirs=include_dirs,
	libraries=get_libraries(include_python_lib=False),
	library_dirs=extra_libraries,
	sources=[
				join(EXT_SRC_DIR, 'pyconcrete.c'),
				join(EXT_SRC_DIR, 'pyconcrete_module.c'),
			]
			+ openaes_sources,
)

# ================================================= setup ================================================= #


setup(
	name='pyconcrete',
	version=version,
	description='Protect your python script, encrypt it as .pye and decrypt when import it',
	long_description=readme,
	keywords='python source encryption obfuscation',
	author='Falldog',
	author_email='falldog7@gmail.com',
	url='https://github.com/Falldog/pyconcrete',
	license="Apache License 2.0",
	ext_modules=[ext_module],
	cmdclass={
		"build": BuildEx,
	},
	scripts=[
		'pyconcrete-admin.py',
	],
	packages=[
		'pyconcrete',
	],
	package_dir={
		'': SRC_DIR,
	},
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Intended Audience :: System Administrators',
		'Topic :: Software Development :: Build Tools',
		'Topic :: Security',
		'Topic :: Security :: Cryptography',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
		'Programming Language :: Python :: 3.10',
		'Programming Language :: Python :: Implementation :: CPython',
		'License :: OSI Approved :: Apache Software License',
	],
	distclass=ExeDistribution,
)
