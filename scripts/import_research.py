"""Deterministically assemble the cited draft. Never certifies cutoff eligibility."""
import json
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
# Citations for class specifications. These remain prose specifications, not completed Lean definitions.
for item in catalog['classes']:
 family=item['family']
 item['definition_source_ids']=(['q-watrous08'] if family=='Quantum' else ['q-ffkl02'] if item['id'] in {'SPP','CeqP','PP','parityP','AWPP','LWPP','WPP'} else ['q-bgm03'] if item['id']=='SBP' else ['q-gsv98','q-sv03'] if item['id']=='SZK' else ['AB2007'])
defined=set(re.findall(r'\|\s+\.(\w+)\s+=>\s+some', (R/'lean/InclusionBench/Definitions.lean').read_text()))
for item in catalog['classes']:
 item['formalization_status']='operational_model_defined_equivalence_unproved' if item['id'] in defined else 'specification_only'
 item['lean_definition_file']='lean/InclusionBench/Definitions.lean' if item['id'] in defined else None
knowledge={'schema_version':1,'status':'draft; cited mathematical claims, not Lean-proved baseline facts','sources':a['sources']+b['sources'],'facts':a['facts']+b['facts'],'rules':a['rules']+b['rules'],'audit_limitations':a['cutoff_limitations']+b['notes']}
write('data/classes.json',catalog)
write('data/knowledge.json',knowledge)
