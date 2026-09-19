# Round 4: counting interfaces

No additional ordinary inclusion or separation was found. This pass checked the boundaries between ten counting classes and 22 randomized, proof, quantum and polynomial-hierarchy classes. The 440 directed pairs contain 55 known inclusions and 385 candidates. All labels are listed in the accompanying JSON, tied to dataset `e09e6cf8dfa1233f754dc4ecf935ea7db6831f24046cde0cbb1eebfedf4349c3`. No canonical data was edited.

The pass followed primary references through nearby classes that are absent from the roster. It concentrated on plausible sources of several missed labels; it was not an exhaustive search for every individual pair.

| Other endpoint family | Directed pairs | Known inclusions | Candidates |
|---|---:|---:|---:|
| Randomized |80|10|70|
| NP, coNP, NP∩coNP |60|8|52|
| Classical proof systems |80|8|72|
| Quantum |80|10|70|
| SBP and SZK |40|3|37|
| Polynomial hierarchy |100|16|84|

Several tempting shortcuts fail at precise boundaries:

- **SZK versus PP and smaller counting classes.** Bouland and colleagues establish an oracle separation; their ordinary PP upper bound concerns honest-verifier *perfect* zero knowledge. The distinction between perfect and statistical simulation cannot be discarded. See Corollary 5.4, Lemma 6.3 and Figure 1 of [On SZK and PP](https://eccc.weizmann.ac.il/report/2016/140/revision/2/download).
- **SZK versus SBP.** Volkovich’s Theorem 2 concerns Statistical Difference with error at most 2⁻⁽ⁿ⁺³⁾, where n is the resulting sampler’s input length. A general polarization procedure also increases the sampler size, so choosing an error parameter alone does not establish the required inequality. The theorem gives a restricted promise problem, not SZK⊆SBP. See [The Untold Story of SBP](https://eccc.weizmann.ac.il/report/2018/088/revision/1/download), Theorem 2 and Lemma 3.2.
- **SBP versus quantum proofs.** SBQP contains both SBP and QMA. That common upper bound does not order its subclasses. The explicit SBP/QMA lower bound in [Aaronson–Kothari–Kretschmer–Thaler](https://drops.dagstuhl.de/storage/00lipics/lipics-vol169-ccc2020/LIPIcs.CCC.2020.7/LIPIcs.CCC.2020.7.pdf), Corollary 20, uses an oracle.
- **Exact versus approximate counting.** [Morimae–Nishimura](https://www.rintonpress.com/xxqic16/qic-16-56/0498-0514.pdf), Theorems 3–8, place WPP below an exact-postselection class and AWPP above it. Postselection is additional computational power. Their classical lower bound begins with UP∩coUP, not NP∩coNP; WAPP is also distinct from AWPP. Exact quantum equalities retain the paper’s gate convention. Projecting the reviewed auxiliary inclusion graph back onto the roster added zero edges.
- **ZPP and NP∩coNP versus exact-counting classes.** [Spakowski–Thakur–Tripathi](https://urresearch.rochester.edu/fileDownloadForInstitutionalItem.action?itemFileId=464&itemId=374), Theorem 3.1 and Corollary 3.12, give an oracle separating ZPP from WPP. [Beigel–Buhrman–Fortnow](https://lance.fortnow.com/papers/files/newiso.pdf), Theorem 1.4 and §5, give one with P=⊕P and ZPP=EXP. Since ZPP⊆NP∩coNP relativizes, both also obstruct the corresponding relativizing inclusions of that intersection. Neither is an ordinary separation.
- **Unambiguity versus zero knowledge.** [Menda–Watrous](https://cs.uwaterloo.ca/~watrous/Papers/OraclesQSZK.pdf) construct an oracle with UP∩coUP outside QSZK. Classical Statistical Difference embeds in quantum state distinguishability, so a generic relativizing UP/coUP-to-SZK simulation would conflict with this result. Again, the ordinary pairs remain candidates.

The quantum proof survey’s PP simulation and classical-witness discussion agree with the existing MA⊆QCMA⊆QMA⊆PP chain. Its group non-membership example supplies no whole-class reverse inclusion; the efficient query bound discussed there also permits expensive computation between queries. See [Quantum Proofs](https://arxiv.org/pdf/1610.01664), §§3.2.3 and 3.4.4.

The PH/counting check retained the hypotheses on measure-based collapse results and the oracle qualifications on SPP/PH examples. In particular, neither [The Size of SPP](https://www.eecs.uwyo.edu/~jhitchco/papers/sspp.pdf), Theorem 1.3, nor [Relativized Worlds with an Infinite Hierarchy](https://lance.fortnow.com/papers/files/sppph.pdf), Theorems 4.1–4.3, supplies an unconditional ordinary inclusion. Full polynomial-time oracle access was kept separate from logarithmically many NP queries.

The JSON records hypothetical fanouts to show why these checks matter. For example, SBP⊆AWPP would resolve 9 current candidates, NP∩coNP⊆SPP 9, WPP⊆BQP 19 and coUP⊆NP 14. These are stress tests, not proposed theorems or forecasts.

I would modestly revise the previous broad old-interface omission estimate from 8% to 6%, keeping the conditional mean of 6 distinct wrong labels: an expected 0.36 instead of 0.48. This is a subjective judgment, independently supported by the other counting reviewer, and should replace that earlier row rather than be added to it. A sensitivity range of 2–15% for the event and 3–12 affected labels gives 0.06–1.8 expected labels. The evidence does not calibrate these numbers.

The limited reduction reflects specific newly checked reference chains. The 385 candidates in this slice cover only part of the earlier 526-candidate interface scope; 141 remain outside it. Papers share references, so repeated agreement is not independent evidence. A missed nonrelativizing theorem or an unfamiliar intermediate class could still change several labels. Oracle barriers alone do not certify historical openness.

This pass adds no evidence to the separate definition/application or internal-counting risk rows. It also does not extend the recent classical/time/counting allowance to all recent quantum/SZK literature; that coverage gap needs its own review and allowance. The full BGM 2002/2006 taxonomy and EATCS 2015 survey were not successfully retrieved. The JSON identifies exactly which primary passages were accessible.
