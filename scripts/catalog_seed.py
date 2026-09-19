"""Author the class catalog. Knowledge facts are imported separately."""
import json
from pathlib import Path
R = Path(__file__).resolve().parents[1]
rows = [
('AC0','AC⁰','Circuits','Nonuniform polynomial-size, constant-depth Boolean circuits with unbounded-fan-in AND/OR and NOT gates.'),
('ACC0','ACC⁰','Circuits','Nonuniform polynomial-size, constant-depth AC⁰ circuits also allowing MOD_m gates for one fixed integer m ≥ 2; union over fixed moduli.'),
('TC0','TC⁰','Circuits','Nonuniform polynomial-size, constant-depth circuits with unbounded-fan-in majority and Boolean gates.'),
('NC1','NC¹','Circuits','Nonuniform polynomial-size Boolean circuits with bounded fan-in and O(log n) depth.'),
('L','L','Space / parallelism','Languages decided by deterministic machines using O(log n) work space and a read-only input tape.'),
('NL','NL','Space / parallelism','Languages decided by nondeterministic machines using O(log n) work space; acceptance means some computation accepts.'),
('LogCFL','LogCFL','Space / parallelism','Languages logspace many-one reducible to a context-free language.'),
('NC','uniform NC','Space / parallelism','Languages decided by logspace-uniform, polynomial-size bounded-fan-in Boolean circuit families with depth O((log n)^k) for some fixed k.'),
('SC','SC','Space / parallelism','Languages decided by one deterministic machine in polynomial time and O((log n)^k) work space simultaneously, for some fixed k.'),
('P','P','Deterministic / nondeterministic','Union over k of DTIME(n^k), under standard finite-alphabet multitape Turing-machine semantics.'),
('RP','RP','Randomness','Polynomial-time probabilistic decision algorithms with acceptance probability ≥ 1/2 on members and 0 on nonmembers.'),
('coRP','coRP','Randomness','Complements of RP languages; polynomial-time algorithms accepting members with probability 1 and nonmembers with probability ≤ 1/2.'),
('ZPP','ZPP','Randomness','Languages with zero-error randomized algorithms of expected polynomial running time; equivalently RP ∩ coRP.'),
('BPP','BPP','Randomness','Polynomial-time probabilistic algorithms accepting members with probability ≥ 2/3 and nonmembers with probability ≤ 1/3.'),
('UP','UP','Counting','Polynomial-time nondeterministic machines having at most one accepting computation per input.'),
('coUP','coUP','Counting','Complements of UP languages.'),
('NP','NP','Deterministic / nondeterministic','Languages having polynomial-length binary witnesses checked by a deterministic polynomial-time verifier.'),
('coNP','coNP','Deterministic / nondeterministic','Complements of NP languages.'),
('FewP','FewP','Counting','Languages recognized by nondeterministic polynomial-time machines having at most polynomially many accepting computations on every input.'),
('SPP','SPP','Counting','Languages whose characteristic function belongs to GapP: a polynomial-time nondeterministic machine has accepting-minus-rejecting gap 1 on members and 0 otherwise.'),
('CeqP','C₌P','Counting','Languages L for which some GapP function g satisfies x ∈ L iff g(x) = 0. GapP functions are differences of #P functions.'),
('PP','PP','Counting','Polynomial-time probabilistic algorithms whose acceptance probability is > 1/2 exactly on members; equivalently some GapP function is positive exactly on members.'),
('parityP','⊕P','Counting','Languages recognized when a nondeterministic polynomial-time machine has an odd number of accepting computations.'),
('AWPP','AWPP','Counting','For every polynomial r, there are g in GapP and a polynomial p with 0 ≤ g(x)/2^p(|x|) ≤ 1, at least 1−2^(−r(|x|)) on members and at most 2^(−r(|x|)) on nonmembers.'),
('LWPP','LWPP','Counting','There are g in GapP and an integer-valued FP function f, nonzero on unary inputs, with g(x) = f(1^|x|) for members and g(x) = 0 for nonmembers.'),
('WPP','WPP','Counting','There are g in GapP and an integer-valued FP function f, nonzero on every input, with g(x) = f(x) for members and g(x) = 0 for nonmembers.'),
('MA','MA','Proof systems','Total languages with polynomial-length classical proofs followed by a probabilistic polynomial-time verifier: some proof accepts members with probability ≥ 2/3, every proof accepts nonmembers with probability ≤ 1/3.'),
('coMA','coMA','Proof systems','Complements of total languages in MA.'),
('AM','AM','Proof systems','Total languages with a public-coin two-message protocol: Arthur sends polynomially many random bits, Merlin responds with a polynomial-length string, then a deterministic polynomial-time predicate decides; completeness ≥ 2/3, soundness ≤ 1/3.'),
('coAM','coAM','Proof systems','Complements of total languages in AM.'),
('QCMA','QCMA','Quantum','Total languages verified by polynomial-time uniform quantum circuits and polynomial-length classical witnesses, with completeness ≥ 2/3 and soundness ≤ 1/3. Fix a standard finite universal algebraic gate set.'),
('QMA','QMA','Quantum','Total languages verified by polynomial-time uniform quantum circuits and polynomial-qubit quantum witnesses, with completeness ≥ 2/3 and soundness ≤ 1/3. Fix a standard finite universal algebraic gate set.'),
('coQMA','coQMA','Quantum','Complements of total languages in QMA.'),
('BQP','BQP','Quantum','Total languages decided by polynomial-time uniform quantum circuits with error at most 1/3 on every input. Fix a standard finite universal algebraic gate set.'),
('SBP','SBP','Randomness','There are f in #P and polynomial p such that f(x) ≥ 2^p(|x|) on members and f(x) ≤ 2^(p(|x|)−1) on nonmembers; #P counts accepting computations of nondeterministic polynomial-time machines.'),
('SZK','SZK','Proof systems','Total languages with an interactive statistical zero-knowledge proof: polynomial-time verifier, completeness ≥ 2/3 and soundness ≤ 1/3, and polynomial-time simulation of every efficient cheating verifier with negligible statistical error (auxiliary input allowed).'),
('NPcapcoNP','NP ∩ coNP','Deterministic / nondeterministic','Intersection of the language classes NP and coNP.'),
('Sigma2P','Σ₂P','Polynomial hierarchy','Languages expressible by a polynomial-time predicate with a polynomial-length existential witness followed by a polynomial-length universal witness; equivalently NP^NP.'),
('Pi2P','Π₂P','Polynomial hierarchy','Complements of Σ₂P languages.'),
('Delta2P','Δ₂P','Polynomial hierarchy','P^NP: deterministic polynomial time with adaptive membership queries to an NP-complete language.'),
('Theta2P','Θ₂P','Polynomial hierarchy','P^NP[O(log n)]: deterministic polynomial time with O(log n) adaptive queries to an NP-complete language; equivalently polynomially many nonadaptive queries.'),
('PH','PH','Polynomial hierarchy','Union of Σ_kP over fixed k ≥ 0, with Σ_0P=P and Σ_(k+1)P=NP^(Σ_kP).'),
('Ppoly','P/poly','Circuits','Languages decided by deterministic polynomial-time machines with a polynomial-length advice string for each input length, with no computability requirement on advice; equivalently arbitrary polynomial-size Boolean circuit families.'),
('NPpoly','NP/poly','Circuits','Languages decided by nondeterministic polynomial-time machines with arbitrary polynomial-length advice depending only on input length.'),
('PSPACE','PSPACE','Exponential resources','Union over k of DSPACE(n^k).'),
('EXP','EXP','Exponential resources','Union over k of DTIME(2^(n^k)).'),
('NEXP','NEXP','Exponential resources','Union over k of NTIME(2^(n^k)).'),
('EXPSPACE','EXPSPACE','Exponential resources','Union over k of DSPACE(2^(n^k)).'),
('E','E','Exponential resources','Union over constants c of DTIME(2^(cn)).'),
('NE','NE','Exponential resources','Union over constants c of NTIME(2^(cn)).'),
]
nonuniform = {'AC0','ACC0','TC0','NC1','Ppoly','NPpoly'}
classes=[{'id':i,'label':l,'family':f,'definition':d,'universe':'total binary languages','uniformity':'nonuniform' if i in nonuniform else 'uniform','formalization_status':'specification_only'} for i,l,f,d in rows]
assert len(classes)==50
catalog={'schema_version':1,'conventions':{'universe':'All classes consist of total decision languages over {0,1}*. A language is a set of finite binary strings.','inclusion':'A ⊆ B is set inclusion of language classes, never a reduction between classes.','separation':'A ⊄ B means there exists a language in A outside B.','strict_inclusion':'A ⊊ B abbreviates A ⊆ B and B ⊄ A; these are two different ordered-pair claims.','nonuniformity':'AC0, ACC0, TC0, NC1, Ppoly and NPpoly allow arbitrary families/advice. They can contain undecidable languages. NC is logspace-uniform.','quantum':'Quantum and interactive classes here contain total languages. Promise-problem variants are a separate possible track.','gates':'Quantum gate-set precision and exact machine encodings must be fixed in the semantic Lean completion; these are mathematical class specifications, not completed operational formalizations.'},'classes':classes,'complements':[]}
(R/'data/classes.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n')
policy={'schema_version':1,'benchmark':'InclusionBench','version':'0.1.0-draft','cutoff':'2026-09-01','cutoff_convention':'Results publicly available before 2026-09-02 00:00:00 UTC count as pre-cutoff. Publication dates and status require human audit.','release_stage':'draft','point_unit':'One ordered class pair certified open at cutoff and newly resolved by an accepted proof, disproof, or ZFC-independence metatheorem.','official_scoring_enabled':False,'public_baseline_score':0,'baseline_meaning':'Historical pre-cutoff results earn zero by definition. Zero does not assert that no post-cutoff public result exists.','scenario_eligibility':'Absent from conservative baseline closure; unreviewed, not certified open.','independence':'Separate metatheorem establishing neither ZFC proof of inclusion nor ZFC proof of its negation, under an explicitly documented metatheory. It does not enter ordinary relation closure.','credit':'Union of resolved eligible ordered pairs per submission or system; no duplicate credit for multiple proofs or dates.','admission':'Maintainer-reviewed proof artifact and exact statement, frozen dataset hash, verified proof audit and certified per-pair eligibility are required. Current draft fails closed.'}
(R/'data/policy.json').write_text(json.dumps(policy,indent=2,ensure_ascii=False)+'\n')
(R/'data/reviews.json').write_text('[]\n')
