import json


def root_lemma(root_key, entry):
    if isinstance(entry, dict):
        return root_key
    return entry


rules=json.load(open('derivation_rules.json'))
roots=json.load(open('roots.json'))
compound={}
with open('lexicon_ignored.txt') as f:
    for line in f:
        line=line.strip()
        if not line or '=' not in line:
            continue
        left,right=line.split('=',1)
        left=left.strip()
        parts=[p.strip() for p in right.split('+') if p.strip()]
        lemma_roots=[]
        suffix=''
        used_roots={}
        for p in parts:
            if p.startswith('-'):
                key=p[1:]
                # map common abbreviations
                if key == 'adj':
                    key = 'adjective'
                if key == 'noun':
                    key = 'noun'
                if key == 'verb':
                    key = 'verb'
                if key == 'complementizer':
                    key = 'complementizer'
                if key in rules:
                    suffix=rules[key]['suffix']
            else:
                term=p
                # direct lookup or fuzzy match
                if term in roots:
                    val=root_lemma(term, roots[term])
                    lemma_roots.append(val)
                    used_roots[term]=val
                else:
                    # attempt substring match
                    found=None
                    for rk in roots:
                        if term in rk:
                            found=rk
                            break
                    if found:
                        val=root_lemma(found, roots[found])
                        lemma_roots.append(val)
                        used_roots[found]=val
                    else:
                        print('warning missing root for',term)
        lemma="-".join(lemma_roots)+suffix
        compound[left]={'lemma':lemma,'roots':used_roots}
with open('compound_words.json','w') as out:
    json.dump(compound,out,indent=2)
print('written',len(compound))
