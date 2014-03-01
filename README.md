Deterministic GPG brainwallet
=============================

Deterministic GPG key creation.  Idea prompted by [electrum](https://electrum.org/)
and DJB's blog [Entropy Attacks](http://blog.cr.yp.to/20140205-entropy.html).

Use case: Anyone who needs a secure yet ephemeral workstation and needs to do
some cryptography.  For example: a [TAILS](https://tails.boum.org/).  This could
also be helpful for the person with a good memory but a bad track record of losing
data.

Requirements
------------

* [GPG](http://gnupg.org)
* [Electrum](https://electrum.org) (optional)
* [MonkeySphere](http://web.monkeysphere.info/)
* [PyCrypto](https://www.dlitz.net/software/pycrypto/)

How to use
----------

    python deterministicgpg.py

Then enter Name, Email, and passphrase or Electrum seed.

Issues
------

1. Is my deterministic random number generator cryptographically secure?
   Evidence in favor: the method used is also used in the python ecdsa.util.PRNG.
2. Is PyCrypto's RSA key generation correct?

Future
------

* Electrum plugin built into GUI
* Option to generate keys off of electrum private keys (is this helpful in any way?)
* Non-RSA keys?
* Set trust on generated gpg keys
* Anything else we should deterministically generate? Bit-message IDs?
