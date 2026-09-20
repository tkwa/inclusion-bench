"""Describe a frozen roster; these measurements are not importance weights."""
from collections import Counter
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from inclusion_bench.benchmark import Benchmark,canonical_hash
b=Benchmark(); matrix=b.matrix(); family={c['id']:c['family'] for c in b.classes}
profiles=[]
for c in b.classes:
 rows=[p for p in matrix['pairs'] if p['left']==c['id']]
 cols=[p for p in matrix['pairs'] if p['right']==c['id']]
 profiles.append({'class_id':c['id'],'family':c['family'],
  'row_status_counts':dict(Counter(p['status'] for p in rows)),
  'column_status_counts':dict(Counter(p['status'] for p in cols)),
  'open_pairs':[{'left':p['left'],'right':p['right']} for p in rows+cols if p['status']=='unreviewed']})
result={'schema_version':1,'dataset_sha256':b.digest,'classes_sha256':canonical_hash(b.catalog),
 'knowledge_sha256':canonical_hash(b.knowledge),'version':b.policy['version'],
 'scope':'Descriptive profile of current mathematical classifications. Open-pair counts are neither research-importance measures nor estimates of tractability.',
 'class_count':len(b.ids),'family_class_counts':dict(Counter(family.values())),
 'open_pair_count':len(b.unresolved),
 'open_endpoint_family_counts':dict(Counter(family[c] for a,z in b.unresolved for c in (a,z))),
 'open_family_pairs':[{'left_family':a,'right_family':z,'ordered_pairs':n} for (a,z),n in sorted(Counter((family[a],family[z]) for a,z in b.unresolved).items())],
 'complement_pairs':b.catalog['complements'],'classes':profiles}
path=Path(__file__).with_name('baseline-roster-profile.json')
path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'written':str(path.relative_to(ROOT)),'classes':len(profiles),'open_pairs':len(b.unresolved)}))
