import json
import random
from itertools import product

inv = json.load(open("phonemic_inventory.json"))
consonants = [p for p,v in inv["phonemes"].items() if v["type"] == "consonant"]
vowels     = [p for p,v in inv["phonemes"].items() if v["type"] == "vowel"]

# full CVC pool
syllables = [o+n+c for o,n,c in product(consonants,vowels,consonants)]
random.shuffle(syllables)

# utility to pop a syllable matching predicate

def pop_syllable(predicate):
    for i,s in enumerate(syllables):
        if predicate(s):
            return syllables.pop(i)
    return None

# read lexicon
words=[]
ignored=[]
with open('lexicon.json') as f:
    for line in f:
        line=line.strip()
        if not line: continue
        if '=' in line:
            ignored.append(line)
        else:
            words.append(line)

mapping = {}
remaining_words = set(words)

# define constrained groups
groups = [
    ["black","white","red","yellow","grue"],
    ["good","bad"],
    ["old","young/new"],
    ["cold","warm","hot"],
    ["wet","dry"],
    ["big","small"],
    ["thick","thin"],
    ["long/tall","short"],
    ["sharp","dull"],
    ["light (weight)","heavy"],
    ["rotten","fresh"],
    ["male","female"],
    ["night","day"],
    ["live","die"],
    ["push","pull"],
    ["first person singular","second person singular","third person singular"],
    ["this (determiner)","that (determiner)"]
]

# assign for each group if words present
for grp in groups:
    present = [w for w in grp if w in remaining_words]
    if not present:
        continue
    if len(present) > 2:
        # choose common initial consonant
        c = random.choice(consonants)
        for w in present:
            # pick a syllable starting with c
            syl = pop_syllable(lambda s: s.startswith(c))
            if syl is None:
                syl = pop_syllable(lambda s: True)
            mapping[w] = syl
            remaining_words.remove(w)
    else:
        # pair: choose a CV then two syllables sharing it
        # pick any s, then find another with same first two chars
        if len(present) == 1:
            w = present[0]
            mapping[w] = pop_syllable(lambda s: True)
            remaining_words.remove(w)
        else:
            w1,w2 = present
            # pick a cv from pool
            syl1 = pop_syllable(lambda s: True)
            if syl1 is None:
                continue
            cv = syl1[:2]
            # find a second syllable with same cv
            syl2 = pop_syllable(lambda s: s.startswith(cv))
            if syl2 is None:
                # fallback: any other
                syl2 = pop_syllable(lambda s: True)
            mapping[w1] = syl1
            mapping[w2] = syl2
            remaining_words.remove(w1)
            remaining_words.remove(w2)

# assign remaining words randomly
for w in list(remaining_words):
    syl = pop_syllable(lambda s: True)
    if syl is None:
        break
    mapping[w] = syl
    remaining_words.remove(w)

# write outputs
with open('lexicon_mapped.json','w') as f:
    json.dump(mapping,f,indent=2)
with open('lexicon_ignored.txt','w') as f:
    f.write("\n".join(ignored))

print('Generated',len(mapping),'entries; ignored',len(ignored))
print('Remaining unassigned',len(remaining_words))
