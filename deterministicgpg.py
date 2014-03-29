#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  Copyright 2014 Arttu Kasvio <arttu@ubuntu>
#  
# This is free and unencumbered software released into the public domain.
# See LICENSE for more info and refer to <http://unlicense.org>

# Requirements: pycrypto, monkeysphere, gpg

import os
import drbg
import getpass
import hashlib
import electrum
import subprocess
import xml.sax.saxutils
from Crypto.PublicKey import RSA

import plugin

def create_gpg_key(user_id, seed):
  
  rand = drbg.HMAC_DRBG(seed)

  key = RSA.generate(4096, rand.read)

  # Since we're auto-generating the key default the creation time to UNIX time 0
  os.environ['PEM2OPENPGP_TIMESTAMP'] = '0'

  #pem2openpgp "Foo Bar <fbar@linux.net>" < priv.pem | gpg --import
  pem2openpgp = subprocess.Popen(['pem2openpgp', user_id],
      stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  gpg_id = pem2openpgp.communicate(key.exportKey(pkcs=1))[0]

  gpg_import = subprocess.Popen(['gpg', '--import'], stdin=subprocess.PIPE)
  gpg_import.communicate(gpg_id)

class Plugin(plugin.Plugin):
  def __init__(self):
    plugin.Plugin.__init__(self, 'GPG private/public keys',
        'Generates a 4096 bit RSA private/public key using a deterministic random number generator seeded from your electrum passphrase.')
    self.name = plugin.StringField('name', 'Name:', 'Typically "First Last"')
    self.email = plugin.StringField('email', 'Email:', 'name@server.domain\n<i>(name will be automatically prepended)</i>')
    self.fields = [self.name, self.email]

  def doit(self, seed):
    key_id = '%s <%s>' % (self.name.value, self.email.value)
    create_gpg_key(key_id, seed)
    ret = plugin.Return(('GPG key for %s created.  You now need to set the trust level for it in the '
        'gpg keychain.  You can do this in <a href="seahorse">seahorse</a> or the <a href="gpg">gpg commandline</a>.'
        ) % xml.sax.saxutils.escape(key_id))
    ret['seahorse'] = plugin.RetExecLink('seahorse')
    ret['gpg'] = plugin.RetExecLink("gpg --edit-key '%s'" % key_id, terminal=True)
    return ret

	
if __name__ == '__main__':
  import sys
  if(len(sys.argv) == 2 and sys.argv[1] == 'randomtest'):
    rand = drbg.HMAC_DRBG("2")
    xpm = open('rand.xpm', 'w')
    xpm.write('! XPM2\n')
    xpm.write('1024 1024 2 1\n')
    xpm.write('a c #FFFFFF\n')
    xpm.write('b c #000000\n')
    for i in range(1024):
      for j in range(1024/8): # 8 bits/byte
        byte = ord(rand.read(1))
        for k in range(8):
          if (byte >> k) & 1:
            xpm.write('a')
          else:
            xpm.write('b')
      xpm.write('\n')
    xpm.close()
    sys.exit(0)
          
  # get name/email for GPG id
  name = raw_input('Name: ')
  email= raw_input('Email: ')
  user_id = '%s <%s>' % (name, email)

  # Example electrum seeds for test:
  #   action draw bit shove single however shore language visit wonderful swell pale
  #   motion shut tool sadness focus scratch wash match torture tightly situation jump
  seed = getpass.getpass(prompt="Passphrase or Electrum seed: ", stream=None)
  if len(seed.split()) == 12:
    try:
      import electrum
      seed = electrum.mnemonic_decode(seed.split())
    except ImportError:
      print 'Could not import electrum to parse 12 word electrum seed.'
      print "Install electrum or use a passphrase that isn't 12 words long."
      print
      raise
  #else we treat whatever was typed as a passphrase
        
  create_gpg_key(user_id, seed)

