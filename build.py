# coding: utf-8
import types
import json
import os
import subprocess
import sys
import zipfile
import marshal
import imp
import time
import struct
import shutil

from datetime import datetime
from xml.etree import ElementTree
from xml.dom import minidom


def buildFlashFD(path):
	path = str(os.path.abspath(path))
	if os.path.isfile(path):
		try:
			fdbuild = os.environ.get('FDBUILD')
			flexsdk = os.environ.get('FLEXSDK')
			if fdbuild and os.path.exists(fdbuild) and flexsdk and os.path.exists(flexsdk):
				args = [fdbuild, '-compiler:' + flexsdk, path]
				subprocess.check_output(args,
										shell=True,
										universal_newlines=True,
										stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError as error:
			print path
			print error.output.strip()

		name, _ = os.path.splitext(os.path.basename(path))
		swf = os.path.join(os.path.dirname(path), 'bin', os.path.basename(name) + '.swf')

		if os.path.isfile(swf):
			with open(swf, 'rb') as f:
				return f.read()
		else:
			print swf, 'not found'
	else:
		print path, 'not found'

def buildPython(path, filename):
	def read(self, path, filename):
		with open(path, 'r') as f:
			try:
				timestamp = long(os.fstat(f.fileno()).st_mtime)
			except AttributeError:
				timestamp = long(time.time())
			return f.read(), struct.pack('L', timestamp)

	def repack(code, co_filename, co_name):
		co_consts = []
		for const in code.co_consts:
			if isinstance(const, types.CodeType):
				const = repack(const, co_filename, const.co_name)
			co_consts.append(const)

		code = types.CodeType(
			code.co_argcount,
			code.co_nlocals,
			code.co_stacksize,
			code.co_flags,
			code.co_code,
			tuple(co_consts),
			code.co_names,
			code.co_varnames,
			co_filename,
			co_name,
			code.co_firstlineno,
			code.co_lnotab,
			code.co_freevars,
			code.co_cellvars
		)

		return code

	if filename.startswith('/'):
		filename = filename[1:]

	with open(path, 'rb') as f:
		try:
			timestamp = long(os.fstat(f.fileno()).st_mtime)
		except AttributeError:
			timestamp = long(time.time())

		basename = os.path.basename(path)
		code = compile(f.read(), filename, 'exec')
		code = repack(code, filename, basename)
		return imp.get_magic() + struct.pack('L', timestamp) + marshal.dumps(code)


def createMeta(**meta):
	metaET = ElementTree.Element('root')
	for key, value in meta.iteritems():
		ElementTree.SubElement(metaET, key).text = value
	metaStr = ElementTree.tostring(metaET)
	metaDom = minidom.parseString(metaStr)
	metaData = metaDom.toprettyxml(encoding='utf-8').split('\n')[1:]
	return '\n'.join(metaData)


def write(package, path, data):
	print 'Write', path, len(data)
	now = tuple(datetime.now().timetuple())[:6]
	path = path.replace('\\', '/')

	dirname = os.path.dirname(path)
	while dirname:
		if dirname + '/' not in package.namelist():
			package.writestr(zipfile.ZipInfo(dirname + '/', now), '')
		dirname = os.path.dirname(dirname)

	if data:
		info = zipfile.ZipInfo(path, now)
		info.external_attr = 33206 << 16 # -rw-rw-rw-
		package.writestr(info, data)

with open('./build.json', 'r') as fh:
	CONFIG = json.loads(fh.read())

if CONFIG.get('append_version', True):
	packageName = '%s_%s.wotmod' % (CONFIG['meta']['id'], CONFIG['meta']['version'])
else:
	packageName = '%s.wotmod' % CONFIG['meta']['id']

if os.path.exists('bin'):
	shutil.rmtree('bin')

if not os.path.exists('bin'):
	os.makedirs('bin')

with zipfile.ZipFile('bin/' + packageName, 'w') as package:
	write(package, 'meta.xml', createMeta(**CONFIG['meta']))

	sources = os.path.abspath('./sources')

	for dirName, _, files in os.walk(sources):
		for filename in files:
			path = os.path.join(dirName, filename)
			name = path.replace(sources, '').replace('\\', '/')
			dst = 'res' + name
			
			fname, fext = os.path.splitext(dst)
			if fext == '.py':
				write(package, fname + '.pyc', buildPython(path, name))
			elif fext == '.po':
				import polib
				write(package, fname + '.mo', polib.pofile(path).to_binary())
			else:
				with open(path, 'rb') as f:
					write(package, dst, f.read())

	for source, dst in CONFIG.get('flash_fdbs', {}).items():
		write(package, dst, buildFlashFD(source))

	for path, dst in CONFIG.get('copy', {}).items():
		with open(path, 'rb') as f:
			write(package, dst, f.read())
