import os.path
import hashlib

import electrum

import bottle
from bottle import Bottle, run, static_file, request

import deterministic

app = Bottle()
STATIC_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

@app.route('/')
def index():
  print STATIC_ROOT
  return static_file('index.html', root=STATIC_ROOT)

@app.route('/plugins')
def list_plugins():
  return deterministic.get_plugins()

@app.route('/plugins/<plugid>')
def run_plugin(plugid):
  plugin = deterministic.get_plugin(plugid)
  seed = request.query.seed
  provided = request.query.provided
  print 'SEED:', seed, 'PROVIDED:', provided

  for need in plugin.needs:
    if need not in provided:
      print 'Plugin', plugid, '('+plugin.name+')', 'needs', need
      return {}

  ret = plugin.doit(seed, provided=provided)
  if ret is None:
    return {'result': 'None'}

  return {'result': ret.string, 'provides': ret.provides}

@app.route('/mnemonic')
def electrum_autocomplete():
  if len(request.query.words.strip()) == 0:
    return { 'error': 'Enter 12 word electrum style mnemonic', 'percent': 0 }

  words = request.query.words.split()
  if len(words) > 12: # more than 12 words
    return { 'error': 'Enter only 12 words' }

  bad = deterministic.check_mnemonic(words)

  if not bad:
    if len(words) == 12:
      seed = deterministic.get_seed(words)
      return { 'seed': seed, 'percent': 100 }
    else: # incomplete, last word not started, nothing bad
      return { 'percent': int( 100 * len(words) / 12.0 ) }
  elif len(bad) == 1 and bad[0] == words[-1]: # last word incomplete
    matches = [ m for m in electrum.mnemonic.words if m.startswith(words[-1]) ]
    return { 'matches': matches, 'percent': int( 100 * len(words) / 12.0 ) }
  else: # bad
    return { 'error': 'Invalid words: ' + ', '.join(bad) }

bottle.debug(True)
run(app, host='localhost', reloader=True)
