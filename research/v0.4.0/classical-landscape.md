# Classical landscape for the provisional v0.4.0 roster

**Add BPL, UL, and ∃R to the shortlist first.** They introduce major questions about space derandomization, isolation, and real feasibility that the current decision-language roster does not represent faithfully. PL, symmetric alternation S₂P, and an explicitly uniform NC¹ are my next choices. This is a domain assessment for comparison with the counting, quantum, and proof-system reviews; it is not a proposed final allocation of all 50 slots.

This review uses the September 1, 2026 cutoff and the v0.3.1 snapshot at commit `5e4addcddd40f1a75a02b83dc26aaee2ac54b1cd`, dataset digest `6cf78ea6cf5edd43e5c327a90ba54765871cfd552800637cbecfbc646eef7742`. The [companion JSON](classical-landscape.json) records 32 sources, 19 candidate classes or alternatives, reproducible baseline counts, and six competing replacement packages. The reviewer is AI-assisted; these priorities are judgments, not a community survey or a calibrated forecast of the next 50 breakthroughs.

**What the present roster already does well.** Keep the main questions P versus NP, NP versus coNP, P versus BPP, L versus NL, NC versus P, and NP versus PSPACE prominent. They are the basic separations emphasized in broad complexity surveys. Circuit endpoints ACC⁰, TC⁰, nonuniform NC¹, and P/poly also serve different scientific purposes: modular gates, threshold gates, formula size, and general circuit size. A large number of known relations around them is not a reason to remove their outstanding lower-bound questions. [Allender–Loui–Regan, p30](https://www.cs.rutgers.edu/~allender/papers/ALR12.pdf); [Rossman, introduction](https://eccc.weizmann.ac.il/report/2024/107/download/).

The existing SC, LogCFL, NC, and NL endpoints give subpolynomial-space and parallel computation more structure than a single L–P comparison. In particular, directed reachability in polynomial time and polylogarithmic space is a substantive question. The 2025 connectivity/random-walk work explicitly uses the difficulty of improving those resources. Its per-input “one of two algorithms succeeds” theorem must not be recorded as a whole-class inclusion. [Doron–Pyne–Tell–Williams, abstract and Theorem1](https://eccc.weizmann.ac.il/report/2025/077/).

**The strongest additions.**

| Candidate | Question it would expose | Why this merits a slot |
|---|---|---|
| BPL | L = BPL; BPL ⊆ NL | Space-efficient randomized computation is a separate derandomization frontier from BPP. |
| UL | NL = UL; L = UL | Uniformly making directed reachability unambiguous is not represented by polynomial-time UP. |
| ∃R | ∃R = NP; ∃R ⊆ PH; ∃R = PSPACE | Real feasibility connects a large collection of discrete geometry, game-theory, and algebra problems. |

For BPL, use total languages recognized with bounded error by a randomized logarithmic-space machine that halts on every random tape. Hoza’s survey makes L = BPL its central problem and also discusses the weaker L = RL question. Adding BPL does not automatically represent every partial one-sided derandomization advance. [Hoza, §1 and §6](https://eccc.weizmann.ac.il/report/2022/121/download).

UL means at most one accepting computation on every input. The equality NL/poly = UL/poly is established; the uniform equality is not. Recent primary work continues to develop uniform isolation and hardness-to-randomness approaches, so this choice is not based only on an old class diagram. [Reinhardt–Allender, introduction and Corollary2.3](https://people.cs.rutgers.edu/~allender/papers/nlul.pdf); [Pyne–Tell, §3.4.3](https://eccc.weizmann.ac.il/report/2026/045/download/).

∃R fits the current type: it is the polynomial-time many-one closure of a **finite binary-encoded decision problem**, the existential theory of the reals. Use formulas with explicitly encoded integer or rational coefficients. Arbitrary real inputs to a BSS machine would be a different object. The 2024 compendium gives NP ⊆ ∃R ⊆ PSPACE, explains the open relationship with PH, and documents the breadth of complete problems. [Schaefer–Cardinal–Miltzow, §1.1–1.2](https://arxiv.org/html/2407.18006v1#S1.SS1).

**The next slots involve real tradeoffs.**

| Candidate | Scientific contribution | Reservation |
|---|---|---|
| PL | Logspace counting and integer linear algebra; comparisons with NL, BPL, and LogCFL | Choose it deliberately over C=L or ⊕L; they are different classes. |
| S₂P | Symmetric alternation and a strengthened Karp–Lipton collapse target | Some advances would already have consequences in the existing PH rows. |
| DLOGTIME-uniform NC¹ | The exact uniform parallelism–logspace boundary | Retain the current nonuniform NC¹ separately for formula lower bounds. |
| DP | Boolean hierarchy and exact optimization | DP = coDP needs a complement endpoint or an explicit complement question. |
| EXP^NP | A general-circuit lower-bound target above NEXP | A higher class is scientifically useful only if its specific frontier is selected deliberately. |

PL has a direct counting-machine definition; C=L tests whether a GapL function is zero, and has integer-matrix singularity as a natural complete problem. This avoids trying to insert the determinant **function** into a language-class matrix. The logspace-counting literature develops these distinctions and asks about their position relative to other parallel classes. My preference is one representative initially, PL, with C=L and ⊕L as alternatives for a more linear-algebra-focused roster. [Allender–Ogihara, §3–5 and §8](https://www.numdam.org/item/ITA_1996__30_1_1_0.pdf).

S₂P sits between Δ₂P and Σ₂P ∩ Π₂P, contains MA, and is contained in ZPP^NP. It represents a familiar structural refinement of the current PH/proof-system part of the roster. It is self-complementary, so it buys a new proof-system dimension without requiring a second mirror slot. [Russell–Sundaram](https://doi.org/10.1007/s000370050007); [Cai](https://doi.org/10.1016/j.jcss.2003.07.015).

Uniformity should be explicit in names and questions. Proving L has uniform NC¹ circuits would also prove the currently scored inclusion L ⊆ nonuniform NC¹. A separation from **uniform** NC¹ alone need not prove a nonuniform formula lower bound. Replacing the existing class would therefore change the question, while adding a separate uniform node would expand it. DLOGTIME uniformity is a standard appropriate convention for such small circuits; do not choose a weaker generator simply because a transducer interface is already implemented. [Barrington–Immerman–Straubing](https://www.sciencedirect.com/science/article/pii/002200009090022D).

DP is not NP ∩ coNP. It consists of languages formed by intersecting an NP language with a possibly different coNP language, and includes both NP and coNP. The Boolean hierarchy has natural complete problems and collapse implications for PH. But one DP row does not capture the entire hierarchy. If slots are scarce, BPL and UL fill more distinct gaps than a solitary DP row. [Riege–Rothe, Definition4 and Theorem5](https://www.jucs.org/jucs_12_5/completenes_in_the_boolean/jucs_12_05_0551_0578_rothe.pdf); [Kadin](https://epubs.siam.org/doi/10.1137/0217080).

For a circuit-focused alternative, EXP^NP versus P/poly is more useful than adding another class whose general-circuit separation is already known. The analogous nondeterministic-circuit frontier can require a second exponential alternation. These distinctions appear explicitly in the hardness/derandomization literature, along with essential promise, advice, and infinitely-often qualifiers. They should not be collapsed into “exponential time.” [Aydınlıoğlu–van Melkebeek, Theorem1 and its following discussion](https://pages.cs.wisc.edu/~dieter/Papers/r-nlb-eccc.pdf).

Other defensible choices include comparator class CC, catalytic logspace CL, and a precisely specified randomized parallel class. CC has natural stable-marriage and lexicographic matching complete problems, with a distinct relationship to NC. CL represents a different workspace resource and has substantial recent progress, but CL and CNL are already equal and should not consume separate slots. RNC requires an explicit one-sided versus bounded-error convention. I rank these below BPL, UL, and ∃R, without making a claim about which problems are easiest. [Cook–Filmus–Lê, Corollary6.17 and §7](https://www.cs.utoronto.ca/~sacook/homepage/lfmmToct.pdf); [Koucký–Mertz–Pyne–Sami, Theorem1](https://eccc.weizmann.ac.il/report/2025/019/download); [David–Papakonstantinou–Sidiropoulos](https://eccc.weizmann.ac.il/report/2009/039/).

**Where slots can come from.** An active roster of 40–50 classes can coexist with additional unscored nodes used for definitions, citations, and implication paths. That gives AC⁰ a natural home: it has **zero unresolved incident ordered pairs** in the present 50-class snapshot. Demoting it preserves every present scored question while keeping an important historical reference class.

EXPSPACE is not redundant. Its two unresolved incident pairs are EXPSPACE ⊆ EXP and EXPSPACE ⊆ NEXP. Both express genuine time–space gaps. Demoting it is a choice to broaden the roster at the expense of those questions, not a mathematical simplification. Its noninclusions in NP/poly and P/poly are already present and follow from the reviewed exponential-space circuit diagonalization. [Current derivation](../classical-notes.md).

Complement satellites such as coUP, coMA, and coAM are plausible sources of slots, but they are not aliases. If only one is demoted, many questions retain a simultaneous-complement mirror elsewhere. Some interfaces lose their last direct representative. The counting reviewer should decide which of FewP, LWPP, and WPP remain essential before reallocating those slots; their raw number of unknown comparisons is not evidence of equal scientific value.

| Current roster measurement | Count | Interpretation |
|---|---:|---|
| Unresolved ordered pairs | 1,378 | Frozen candidate questions, not 1,378 independent conjectures |
| Orbits under the encoded simultaneous-complement map | 1,065 | 313 orbits have two members; other logical dependencies remain |
| Known nonuniform-to-recursive separations | 264 of 413 | Mostly an advice/uncomputability distinction, not 264 different frontier successes |
| Common unresolved outbound targets for E and EXP | 38 | Corresponding inclusions are equivalent under the existing regular-padding rules |
| Common unresolved outbound targets for NE and NEXP | 28 | The same qualification applies |

These figures describe the existing graph; they do not measure importance or justify changing the requested one-point scoring rule. In particular, E and NE have other incoming comparisons and genuine linear-exponential questions. Their roles are not exhausted by padding. If finite-model theory receives special emphasis, coNE would represent Asser’s spectrum complement problem directly: the primary characterization is Spec = NE, **not** NEXP. A negative answer already implies NP ≠ coNP; a positive answer is an additional target. [Durand–Jones–Makowsky–More, Theorem5.5, Corollary5.6, and §5.5](https://arxiv.org/pdf/0907.5495).

Here are competing **50-class** packages, keeping additions from other agents open for the next comparison:

| Package | Demote to background | Add | Old candidate pairs no longer between two active endpoints / complement orbits without a retained representative |
|---|---|---|---:|
| Minimum, preserving resource gaps | AC0, coUP, coMA | BPL, UL, ∃R | 128 / 25 |
| Minimum, preserving proof complements | AC0, EXPSPACE, coUP | BPL, UL, ∃R | 64 / 12 |
| More classical breadth | AC0, coUP, coMA, FewP, LWPP, WPP | BPL, UL, ∃R, PL, S₂P, uniform NC¹ | 316 / 193 |
| More circuit emphasis | Same six demotions | Replace S₂P above with EXP^NP | 316 / 193 |

The loss columns consider current pairs only. They do not count new questions, and “no retained complement representative” does not mean no remaining implication can receive credit. The broader packages require cross-review of counting and proof-system value; they are alternatives for eliciting priorities, not claims of optimal selection. BQL and the quantum-proof candidates should compete for these same marginal slots rather than being appended after a complete classical allocation.

**The requested demotion tradeoffs.** I would keep NP ∩ coNP and NP/poly in a conservative total-language roster. The first asks about the whole region with efficiently checkable certificates on both sides. A containment such as NP ∩ coNP ⊆ BQP need not give NP ⊆ BQP. Parity and mean-payoff games provide natural members, but are not known to be complete for the entire class; solving one of them does not automatically resolve its row. [Jurdziński, Theorem8](https://www.dcs.warwick.ac.uk/~mju/Papers/Jur98-IPL.pdf).

NP/poly has an additional motivation beyond circuit-diagram completeness. The hypothesis coNP ⊆ NP/poly is equivalent by complementation to NP ⊆ coNP/poly, the central exceptional case in instance-compression and kernelization lower bounds. Removing NP/poly loses that direct target, as well as positive nondeterministic-circuit containments for quantum and counting classes. Conversely, every current unresolved C ⊆ NP/poly also has unresolved C ⊆ P/poly, so a new lower bound against NP/poly would still imply a scored deterministic-circuit lower bound. This asymmetry favors retaining the node if positive structural discoveries count as much as separations. [Fortnow–Santhanam, Theorem1.2 and §4](https://lance.fortnow.com/papers/files/compress.pdf); [Yap, abstract](https://www.sciencedirect.com/science/article/pii/0304397583900208).

coRP is a more plausible demotion. With RP, ZPP, and BPP retained, full derandomization, elimination of the opposite error type, and many complement mirrors remain represented. It still loses direct asymmetric targets, including coRP ⊆ NE. This argument says nothing about complete coverage of particular polynomial-identity-testing algorithms: a member of coRP is not automatically coRP-complete.

E and NE deserve separate decisions. E's outgoing polynomially padded questions substantially overlap EXP's, but its incoming questions require time 2^O(n), not arbitrary exponential time. E is also the natural source of the quantitative circuit hardness used for derandomization. Keeping it as a background node preserves that vocabulary; removing its scored row does not claim the quantitative distinction is unimportant. The Impagliazzo–Wigderson hypothesis requires exponential circuit size, which is stronger than E ⊄ P/poly. NE has the same padding issue but also its connection to finite spectra and several incoming questions that lose their last ordinary scored consequence when it alone is removed. [Impagliazzo–Wigderson, abstract and §1](https://www.math.ias.edu/~avi/PUBLICATIONS/MYPAPERS/IW97/proc.pdf); [Durand et al., Theorem5.5](https://arxiv.org/pdf/0907.5495).

**Allocate the PH slots deliberately.** I would retain NP, coNP, Σ₂P, Δ₂P, and PH, and preferably Θ₂P. Σ₂P represents alternation and natural minimization problems; Δ₂P represents adaptive NP-oracle computation; PH supplies the whole-hierarchy comparison needed for quantum, counting, and real feasibility. Θ₂P represents polynomially many parallel NP questions, so Δ₂P ⊆ Θ₂P asks whether adaptivity can be removed. Natural exact-ranking problems support its scientific identity. [Schaefer–Umans, §1–3](https://ovid.cs.depaul.edu/documents/phcom.pdf); [Hemaspaandra–Hemaspaandra–Rothe, Theorems3.1 and3.8](https://www.ccc.cs.uni-duesseldorf.de/~rothe/PDF/JACM-carroll-44-6-pp806-825.pdf).

If one more PH slot must be reassigned, I would consider Π₂P before Θ₂P. Π₂P is not an alias of Σ₂P. However, Σ₂P = Π₂P also collapses PH to Σ₂P, while their inequality separates Σ₂P from the self-complementary Δ₂P; those broad breakthroughs retain scored consequences. Adding S₂P instead buys a new symmetric-verification target. Keeping all current PH-related nodes and adding S₂P would allocate eight of fifty slots to NP, coNP, Σ₂P, Π₂P, Δ₂P, Θ₂P, PH, and S₂P. That may be defensible, but should compete openly with missing space and algebraic directions.

I tested the ordinary implication library to distinguish direct endpoint loss from loss of all current credit. For each unresolved pair touching a proposed demotion, I separately assumed inclusion and noninclusion, computed closure, and checked for any other old candidate resolved between retained nodes:

| Node demoted alone | Ordinary assumptions tested | Assumptions with no other old scored consequence |
|---|---:|---:|
| coRP | 110 | 1 |
| NP ∩ coNP | 116 | 8 |
| NP/poly | 58 | 20 |
| E | 144 | 0 |
| NE | 114 | 4 |
| Θ₂P | 128 | 0 |
| Π₂P | 124 | 0 |

For example, Δ₂P ⊆ Θ₂P still implies Δ₂P ⊆ PP and NEXP ⊄ Δ₂P after Θ₂P is demoted. This is a property of the encoded theory, **not** a proof of complete redundancy or equal scientific coverage. It tests single demotions, excludes independence, and must be rerun for simultaneous cuts and new endpoints. In particular, independence of a background pair does not propagate as an ordinary inclusion or separation.

**A full conservative 50-node comparison.** Combining the domain reviews yields the following defensible starting point, called **A** in the JSON. It demotes AC0, coUP, coMA, coAM, coQMA, FewP, LWPP, and WPP to background, and adds BPL, UL, ∃R, P^PP, CH, QMA(2), StoqMA, and QSZK. The grouping is only for readability; classes can participate in several scientific fields.

| Group | Scored endpoints | Count |
|---|---|---:|
| Circuits and advice | ACC0, TC0, nonuniform NC1, P/poly, NP/poly | 5 |
| Space and parallelism | L, UL, NL, BPL, LogCFL, NC, SC, PSPACE, EXPSPACE | 9 |
| Time, nondeterminism, and real feasibility | P, NP, coNP, NP ∩ coNP, ∃R, E, NE, EXP, NEXP | 9 |
| Randomness and classical proofs | RP, coRP, ZPP, BPP, MA, AM, SBP, SZK | 8 |
| Counting and unambiguity | UP, SPP, C=P, PP, ⊕P, AWPP, P^PP, CH | 8 |
| Quantum computation and proofs | BQP, QCMA, QMA, QMA(2), StoqMA, QSZK | 6 |
| Higher polynomial hierarchy | Σ₂P, Π₂P, Δ₂P, Θ₂P, PH | 5 |

This is a proposal for review, not a claim of optimal balance. The strongest counterarguments are the loss of fine positive collapses such as FewP = UP and LWPP = WPP, the changed complement weighting, and the continued absence of PL and BQL. The quantum entries must be explicitly total-language restrictions; their promise versions do not have identical coverage. The [counting review](counting-and-scope-landscape.md) and [quantum review](quantum-randomness-landscape.md) give the cross-domain source evidence and alternatives.

My broader-coverage comparison **B** replaces A's coRP and E with **PL and BQL**, leaving both demoted nodes available to the inference engine. It retains Θ₂P, NE, NP ∩ coNP, NP/poly, and the two EXPSPACE gaps. This gains logspace counting and quantum space at the expense of direct linear-exponential deterministic comparisons and one-sided complement weighting. A removes 437 old candidate ordered pairs from the active matrix; B removes 537. Those are weighting counts, not counts of scientific questions lost, and they omit all newly introduced pairs. An intermediate nine-change proposal can make either swap alone. A separate alternative replaces Π₂P with S₂P. None of these choices is based on which theorem seems easier to formalize or prove.

**A necessary coverage limit.** The primary July 2026 revision of *Bipartite Matching is in NC* gives a deterministic parallel algorithm, including the stated weighted/search extensions; an independent July paper simplifies its detection criterion. This is an excellent historical stress test. An individual-problem algorithm does not by itself collapse RNC to NC or P to NC, so it can remain unscored in any roster of broad classes. It is also already before the cutoff and must not appear on the future-open list. [Chatterjee et al., Theorem1.1](https://eccc.weizmann.ac.il/report/2026/100/revision/2/download/); [Kopparty–Saraf](https://arxiv.org/abs/2607.15554).

Likewise, a super-quadratic lower bound for depth-two threshold circuits need not separate the union TC⁰ from another broad class. Near-maximum bounds for S₂E, AMEXP with subexponential advice, and E with a promise-MA oracle and one advice bit are distinct results with distinct qualifiers. Adding their names cannot make later quantitative improvements score when the ordinary polynomial-size separation was already known. [Chen–Tal–Wang](https://eccc.weizmann.ac.il/report/2026/039/); [Li](https://eccc.weizmann.ac.il/report/2023/156/revision/1/download/); [Chen–Li–Liang](https://eccc.weizmann.ac.il/report/2024/182/revision/2/download/); [Ren–Williams](https://eccc.weizmann.ac.il/report/2026/118/revision/1/download/).

Promise, search, algebraic-function, and quantitative tracks could address such omissions, but they change the benchmark’s objects and admission rules. This review does not assume permission to add them. Within the ordinary-language format, the immediate decision is which broad scientific questions deserve direct endpoints. Any adopted addition still needs its own definition, complete pre-cutoff pair audit, and implication review before a provisional release can claim the established baseline quality.
