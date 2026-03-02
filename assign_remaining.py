import json, random
from itertools import product

inv = json.load(open('phonemic_inventory.json'))
consonants=[p for p,v in inv['phonemes'].items() if v['type']=='consonant']
vowels=[p for p,v in inv['phonemes'].items() if v['type']=='vowel']
all_syll=[o+n+c for o,n,c in product(consonants,vowels,consonants)]

mapped = json.load(open('lexicon_mapped.json'))
used = set(mapped.values())

mp=set()
for s in used:
    for t in all_syll:
        if sum(1 for a,b in zip(s,t) if a!=b)==1:
            mp.add(t)

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

missing=[w for w in words if w not in mapped]
print('missing',len(missing))
available=[s for s in all_syll if s not in used and s not in mp]
print('available syllables',len(available))
for w in missing:
    if not available:
        break
    syl=random.choice(available)
    mapped[w]=syl
    available.remove(syl)
    for t in all_syll:
        if sum(1 for a,b in zip(syl,t) if a!=b)==1 and t in available:
            available.remove(t)

with open('lexicon_mapped.json','w') as f:
    json.dump(mapped,f,indent=2)
print('assigned',len(missing),'words')
