import plugin
import hashlib
import electrum

def pick(chars, word, i):
  filtered = [w for w in word if w in chars]
  if len(filtered) == 0:
    print '>', repr(chars), repr(word), i
    return ' '
  else:
    return filtered[i % len(filtered)]

def pick_vowel(word, i):
  return pick('aeiouy', word, i)

def pick_consonant(word, i):
  return pick('bcdfghjklmnpqrstvwxyz', word, i)


class Plugin(plugin.Plugin):
  def __init__(self):
    plugin.Plugin.__init__(self, 'Name', 'Generates a pronouncable name.')
    self.fields = []

  def doit(self, seed):
    # sha512 with electrum gives us 48 words to work with
    words = electrum.mnemonic_encode(hashlib.sha512(seed).hexdigest())   # Words used:
    len_first = 3 + int(hashlib.md5(words[0]).hexdigest()[:10], 16) % 5  #   8
    len_middle= 1 + int(hashlib.md5(words[1]).hexdigest()[:10], 16) % 8  #   9
    len_last  = 2 + int(hashlib.md5(words[2]).hexdigest()[:10], 16) % 10 #  12
    words = words[3:]                                                    # + 3
                                                                         # =32

    ret = ''
    for i, w in enumerate(words):
      if i % 2:
        ret += pick_vowel(w, i)
      else:
        ret += pick_consonant(w, i)

      name = ret.split()
      if len(name) == 1 and len(name[0]) == len_first:
        ret += ' '
      elif len(name) == 2 and len(name[1]) == len_middle:
        ret += ' '
      if len(name) == 3 and len(name[2]) == len_last:
        break
    name = ' '.join(w.capitalize() for w in ret.split())

    return plugin.Return('Your name is: %s' % name)


if __name__ == '__main__':
  import sys
  seed = 'seed'
  if len(sys.argv) == 2:
    seed = sys.argv[1]
  p = Plugin()
  for i in range(25):
    print '>', seed, i,':',
    p.doit(hashlib.sha512(seed + str(i)).hexdigest())
