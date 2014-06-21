import electrum
import hashlib
import plugin
import name
import deterministicgpg

def check_mnemonic(words):
  """Input list of words, output list of bad words or empty list if no errors"""
  bad = []
  for word in words:
    if word not in electrum.mnemonic.words:
      bad.append(word)
  return bad

def get_seed(words):
  """input: List of 12 words from electrum dictionary, output: electrum decoded key"""
  return electrum.mnemonic_decode(words)

plugins = { hashlib.sha256(p.name).hexdigest(): p for p in [name.Plugin(), deterministicgpg.Plugin(),
    ]}

def get_plugins():
  return { h: plugins[h].json_dict() for h in plugins.keys() }

def get_plugin(plugid):
  if plugid in plugins:
    return plugins[plugid]
  return None
