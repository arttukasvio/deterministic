#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  Copyright 2014 Arttu Kasvio <arttu@ubuntu>
#  
# This is free and unencumbered software released into the public domain.
# See LICENSE for more info and refer to <http://unlicense.org>

# Requirements: electrum, pycrypto, monkeysphere, gpg

import os
import getpass
import hashlib
import electrum
import subprocess
from Crypto.PublicKey import RSA

class DeterministicRandom(object):
  """ Deterministic "random" generator.  May not be best method, but
        ... seems to be same basic procedure as used in python-ecdsa util.PRNG
        https://github.com/trezor/python-ecdsa/blob/master/ecdsa/util.py
        
      Somewhat inspired by: http://blog.cr.yp.to/20140205-entropy.html
      Some code from: https://github.com/dlitz/pycrypto/blob/master/lib/Crypto/Random/_UserFriendlyRNG.py
  """

  def __init__(self, seed):
    self.closed = False
    self.seed = seed
    self.iteration = 0
    self.data = ""

  def close(self):
    self.closed = True

  def flush(self):
    pass

  def read(self, N):
    """Return N bytes from the RNG."""
    if self.closed:
      raise ValueError("I/O operation on closed file")
    if not isinstance(N, (long, int)):
      raise TypeError("an integer is required")
    if N < 0:
      raise ValueError("cannot read to end of infinite stream")

    # Create the "random" data
    while len(self.data) < N:
      self.data += hashlib.sha512(self.seed + str(self.iteration)).digest()
      self.iteration += 1

    retval = self.data[:N]
    self.data = self.data[N:]
    assert len(retval) == N

    return retval

if __name__ == '__main__':
  import sys
  if(len(sys.argv) == 2 and sys.argv[1] == 'randomtest'):
    rand = DeterministicRandom("2")
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

  # Example seeds for test:
  #   action draw bit shove single however shore language visit wonderful swell pale
  #   motion shut tool sadness focus scratch wash match torture tightly situation jump
  seed = getpass.getpass(prompt="Seed: ", stream=None)
  seed = electrum.mnemonic_decode(seed.split())

  rand = DeterministicRandom(seed)

  key = RSA.generate(4096, rand.read)

  # Since we're auto-generating the key default the creation time to UNIX time 0
  os.environ['PEM2OPENPGP_TIMESTAMP'] = '0'

  #pem2openpgp "Foo Bar <fbar@linux.net>" < priv.pem | gpg --import
  pem2openpgp = subprocess.Popen(['pem2openpgp', '%s <%s>' % (name, email)],
      stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  gpg_id = pem2openpgp.communicate(key.exportKey(pkcs=1))[0]

  gpg_import = subprocess.Popen(['gpg', '--import'], stdin=subprocess.PIPE)
  gpg_import.communicate(gpg_id)

