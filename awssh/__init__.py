#! /usr/bin/env python

# Copyright (c) 2011 SEOmoz
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''Checks for all your EC2 instances, and then edits your ssh config
file to make sure that all machines are accounted for.

It is important to note that, though it preserve the contents of the
installed ~/.ssh/config, it:

1. Does not preserve order
2. Does preserve comments
3. Does save a backup copy
4. Assumes that for a machine with keypair "production", that key
resides at ~/.ssh/production
'''

__author__     = 'Dan Lecocq'
__version__    = '0.1'
__maintainer__ = 'Dan Lecocq'
__email__      = 'dan@seomoz.org'
__status__     = 'Beta'

# Let's just make life easy on ourselves and add re
import re
import os
import logging

# Set up some logging
logger = logging.getLogger('awssh')
formatter = logging.Formatter('[%(levelname)s] => %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class SSHConfig(object):
	def __init__(self):
		self.tmp = os.path.expanduser('~/.ssh/config.tmp')
		self.bak = os.path.expanduser('~/.ssh/config.bak')
		self.orig = os.path.expanduser('~/.ssh/config')
		self.machines = {}
		self.load()

	def add(self, name, keys, comments=[]):
		existing = self.machines.get(name, {'comments': comments, 'keys': keys})
		existing['keys'].update(keys)
		existing['comments'] = comments
		self.machines[name] = existing

	def load(self):
		'''Loads the users ssh config file, preserving comments'''
		with file(self.orig, 'r') as f:
			comments = []
			host     = None
			for line in f:
				line = line.strip()
				# Skip blank lines
				if not len(line):
					continue
				elif line[0] == '#':
					# Append this to comments. We'll add them later.
					comments.append(line)
				else:
					try:
						key, value = re.split(r'\s*[\s=]\s*', line, 1)
					except:
						logger.warn('Invalid line: %s' % line)
					if key == 'Host':
						host = value
						# If it's already in there, don't overwrite it
						self.machines[value] = self.machines.get(value, {'comments': comments, 'keys': {}})
					elif not host:
						logger.warn('No Host provided before %s' % line)
						continue
					else:
						self.machines[host]['keys'][key] = {'value': value, 'comments': comments}
					comments = []

	def save(self):
		# Do NOT open the actual ~/.ssh/config file this way -- it will clobber it
		# Instead, we'll have a save command that saves this file, and moves it 
		# to replace the existing ssh config file
		with file(self.tmp, 'w+') as f:
			for k, v in self.machines.items():
				for comment in v['comments']:
					f.write('%s\n' % comment)
				f.write('Host %s\n' % k)
				for hk, hv in v['keys'].items():
					for comment in hv.get('comments', []):
						f.write('\t%s\n' % comment)
					f.write('\t%s %s\n' % (hk, hv['value']))
				f.write('\n')
		# Rename the existing ssh/config, and replace it
		os.rename(self.orig, self.bak)
		os.rename(self.tmp, self.orig)
				