"""Deterministically assemble the cited draft. Never certifies cutoff eligibility."""
import json
import hashlib
import re
from pathlib import Path
R = Path(__file__).resolve().parents[1]
def read(p): return json.loads((R/p).read_text())
def write(p,v): (R/p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
a,b=read('research/classical.json'),read('research/quantum.json')
catalog=read('data/classes.json')
c=a['class_recommendations']
comps=[]
for name in c['complement_self']:
 comps.append({'left':name,'right':name,'source_ids':c['complement_sources'].get(name,c['complement_sources']['default'])})
for left,right in c['complement_pairs']:
 comps.append({'left':left,'right':right,'source_ids':c['complement_sources']['default']})
comps+=b['complement_pairs']
catalog['complements']=comps
# Citations for class specifications; model equivalence remains unproved.
for item in catalog['classes']:
 family=item['family']
 item['definition_source_ids']=(['q-watrous08'] if family=='Quantum' else ['q-ffkl02'] if item['id'] in {'SPP','CeqP','PP','parityP','AWPP','LWPP','WPP'} else ['q-bgm03'] if item['id']=='SBP' else ['q-gsv98','q-sv03'] if item['id']=='SZK' else ['AB2007'])
defined=set(re.findall(r'\|\s+\.(\w+)\s+=>\s+some', (R/'lean/InclusionBench/Definitions.lean').read_text()))
complete=set(re.findall(r'\|\s+\.(\w+)\s+=>', (R/'quantum/InclusionQuantum/Complete.lean').read_text()))
assert complete == {item['id'] for item in catalog['classes']}, 'Complete Lean interpretation must cover exactly the catalog'
for item in catalog['classes']:
 item['formalization_status']='operational_model_defined_equivalence_unproved'
 item['lean_definition_file']='lean/InclusionBench/Definitions.lean' if item['id'] in defined else 'quantum/InclusionQuantum/Complete.lean'
knowledge={'schema_version':1,'status':'draft; cited mathematical claims, not Lean-proved baseline facts','sources':a['sources']+b['sources'],'facts':a['facts']+b['facts'],'rules':a['rules']+b['rules'],'audit_limitations':a['cutoff_limitations']+b['notes']}
write('data/classes.json',catalog)
write('data/knowledge.json',knowledge)
paths=sorted([*R.glob('lean/InclusionBench/*.lean'), *R.glob('quantum/InclusionQuantum/*.lean'), R/'lean/lean-toolchain', R/'quantum/lake-manifest.json'])
files={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
write('data/formalization.json', {'schema_version':1, 'status':'definitions supplied; textbook equivalence and literature proof obligations remain', 'definition_count':len(complete), 'files':files, 'bundle_sha256':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',', ':')).encode()).hexdigest()})
