# Counting, ambiguity, and the scope of the v0.4.0 roster

This is a scientific selection review, dated September 20, 2026, for the provisional v0.4.0 branch. The mathematical cutoff remains September 1, 2026. It recommends portfolios for discussion; it does not change the roster, certify the complete baseline for a new class, or forecast which questions will be solved. Implementation cost played no role in the recommendations. The companion JSON records definitions, evidence, alternatives, and unresolved review obligations.

**Recommendation under a total-language-only scope:** compare an eight-class block **UP, SPP, C=P, PP, ⊕P, AWPP, P^PP, CH** with a nine-class version that also retains **FewP**. Keep coUP, LWPP, WPP, and any demoted FewP as unscored background classes. The strongest proposed additions are P^PP and CH. PP^PP and Mod₃P have defensible cases, but they should compete for explicit scientific coverage rather than be appended automatically.

This recommendation favors breadth across counting questions: ambiguity, exact gaps, zero tests, parity, approximate gaps, adaptive counting, and iterated counting. A specialist emphasizing ambiguity or exact normalization can reasonably prefer FewP or LWPP/WPP to one of the added hierarchy endpoints. The evidence below explains those disagreements. It does not measure an objective percentage of complexity theory that counting deserves.

## What the present block weights

The ten existing classes UP, coUP, FewP, SPP, C=P, PP, ⊕P, AWPP, LWPP, and WPP occupy 20% of the 50 slots. They touch 900 of the 2,500 ordered pairs, or 36%, before excluding known results. In the frozen v0.3.1 profile they touch **608 distinct unresolved ordered pairs out of 1,378, or 44.12%**. The profile's 661 unresolved endpoint incidences count each of the 53 unresolved internal counting pairs twice. These are different denominators and should remain separate in any comparison.

The profile used here has dataset digest `6cf78ea6cf5edd43e5c327a90ba54765871cfd552800637cbecfbc646eef7742`. Its classifications are inherited evidence for unchanged endpoints, not a historical audit of P^PP, PP^PP, CH, or Mod₃P. No projected unknown-pair counts are assigned to those additions.

The current allocation gives several slots to nearby exact-gap distinctions but none to the power of a deterministic counting oracle or to iterated majority. This is a coverage imbalance in my judgment, not an argument that the existing exact classes are obscure or easy. In particular, later work on robustness and restricted accepting-path counts shows that these remain active mathematical objects. [Hemaspaandra et al., *The Robustness of LWPP and WPP*, §§3–4](https://arxiv.org/pdf/1711.01250v3); [Hemaspaandra et al., *Gaps, Ambiguity, and Establishing Complexity-Class Containments*, Table 1 and §4](https://arxiv.org/pdf/2109.14764v5).

## Exact meaning of the candidates

All classes in this section contain total languages over binary strings. Machines have one fixed polynomial bound for all inputs. Let `#M(x)` be the number of accepting computation paths of a nondeterministic polynomial-time machine, counting multiplicities. GapP consists of differences of such counting functions. A polynomial bound on the number of accepting paths is a semantic restriction on every input, not a promise on the inputs presented to the machine. The standard function definitions and their polynomial-time closure properties are set out in [Fortnow, *Counting Complexity*, Definition 3.1 and §3](https://lance.fortnow.com/papers/files/counting.pdf).

| Class | Definition relevant to roster identity | What must not be substituted |
|---|---|---|
| UP | Some nondeterministic polynomial-time machine has at most one accepting path on every input and recognizes the language. | Promise-UniqueSAT; an isolation procedure that succeeds only randomly. |
| coUP | Complements of UP languages. | UP itself, or UP∩coUP. |
| FewP | Some recognizing machine has at most polynomially many accepting paths on every input. | Few, which permits a separate polynomial-time predicate on the count; a bound on all computation paths. |
| SPP | A GapP function is exactly 1 on yes instances and 0 on no instances. | UP: a gap of 1 need not mean exactly one accepting path. |
| C=P | A GapP function is zero exactly on yes instances. | coC=P, whose yes criterion is nonzero. |
| PP | A GapP function is positive exactly on yes instances. | BPP's constant error gap; a machine with arbitrary real transition probabilities. |
| ⊕P | An accepting-path count is odd exactly on yes instances. | The parity of the input bits, which is a single easy language. |
| LWPP | A GapP function is 0 on no instances and equals a nonzero FP integer depending only on input length on yes instances. | An arbitrary, possibly uncomputable, length-dependent normalizer. |
| WPP | The same condition with a nonzero FP integer depending on the whole input. | A #P function substituted for the FP normalizer. |
| AWPP | For every inverse-exponential error target, a GapP function divided by a length-dependent power of two approximates the characteristic function within that error and stays in [0,1] on every input. | Unbounded signed approximations, or postselection with an unrestricted normalization probability. |
| P^PP | Deterministic polynomial time with adaptive queries to one fixed PP language. | PP^PP; nonadaptive queries; one PP answer treated as a complete #P value. |
| PP^PP | A PP machine with a PP oracle; the second counting-hierarchy level C₂P. | P^PP. |
| CH | The union of CₖP for fixed finite k, where C₀P=P and Cₖ₊₁P=PP^(CₖP). | A depth that grows with the input, or an arbitrary oracle drawn afresh for each input. |
| Mod₃P | Some nondeterministic polynomial-time machine has an accepting-path count not divisible by 3 exactly on yes instances. | ModₖP with a variable modulus, arbitrary composite-modulus conventions, or an AC⁰ circuit class with MOD gates. |

The exact SPP/LWPP/WPP target conventions are explicit in [Hemaspaandra et al., Definitions 2.3–2.5](https://arxiv.org/pdf/1711.01250v3). The power-of-two AWPP definition and its equivalence to an FP-normalized version appear in [Fenner–Fortnow–Kurtz–Li, *An Oracle Builder's Toolkit*, Definition 6.1 and Lemma 6.3](https://lance.fortnow.com/papers/files/obt.pdf). CH's operator and oracle definitions are matched in [Bürgisser, *On Defining Integers in the Counting Hierarchy*, Definition 2.3 and equation (3)](https://eccc.weizmann.ac.il/report/2006/113/download/).

These definitions are a specification for scientific review. Existing Lean names with the same labels must still be checked against them before any new baseline statement is inherited.

## Reasons to retain, add, or demote

| Endpoint | Strongest reason for a scored slot | Cost of demotion or counterargument | Judgment |
|---|---|---|---|
| UP | Isolates the power of unambiguous nondeterminism; retains P versus UP and NP versus UP. | Worst-case inversion connections do not give average-case cryptographic security. | Retain. |
| coUP | Represents complement closure of unambiguous computation and asymmetric comparisons. | Much credit mirrors UP against complement-closed targets. Important UP=coUP outcomes still have some consequences among other scored classes. | Background in the breadth portfolio. |
| FewP | Tests whether polynomial ambiguity adds power beyond uniqueness; distinguishes UP=FewP from FewP=NP. | Some consequences survive through UP, NP, and SPP, but the small ambiguity collapse is a real lost target. | Retain in the nine-slot version; first extra counting slot. |
| SPP | Exact 0/1 gap class with structural closure and a graph-isomorphism connection. | GI membership in SPP does not mean a GI algorithm settles an SPP inclusion. | Retain. |
| C=P | Exact zero-testing is different from sign and parity; has natural arithmetic-circuit complete problems. | The complementary nonzero class is not separately scored. | Retain. |
| PP | Central majority counting and exact-counting boundary; P versus PP already tests whether all #P counts are efficiently computable. | Many whole-counting collapses are already reflected here, so a new function track should not claim entirely new coverage of that same collapse. | Retain. |
| ⊕P | Represents modular counting, with Toda-style links and a genuinely different acceptance predicate from PP. | Modulus 2 alone does not cover distinctions between characteristics. | Retain. |
| AWPP | A precise bridge between approximate gaps and bounded-error quantum computation. | It is an upper-bound class; a named quantum algorithm need not determine the whole class's relation to BQP. | Retain. |
| LWPP | Length-dependent exact normalization, Turing closure, and graph-reconstruction applications. | Keeping both it and WPP places extra weight on exact normalizers while omitting other computational models. | Background in the breadth portfolio. |
| WPP | Input-dependent exact normalization; open closure and comparison questions differ from LWPP. | It overlaps the region bounded by SPP, LWPP, and AWPP, though it is not interchangeable with any of them. | Background in the breadth portfolio. |
| P^PP | Directly asks whether deterministic counting can simulate polynomial-space computation; also exposes PP's adaptive Turing closure. | Shares major counting collapses with PP and CH, but not all of its principal questions are equivalent to theirs. | Add. |
| CH | Represents arbitrarily many fixed levels of majority counting and their comparison with PSPACE, PH, and circuits. | Less fine resolution than an explicit intermediate level; the union does not have the ordinary fixed-level complete-problem interpretation. | Add. |
| PP^PP | Has natural complete problems; locates a concrete level between P^PP and CH. | Two prominent collapse questions duplicate questions already represented by {PP,P^PP,CH}; intermediate comparisons remain distinct. | Alternative ninth or tenth slot. |
| Mod₃P | Adds the question of whether odd-prime modular counting differs from parity. | Choosing one prime is a deliberate sample of a family, not coverage of every modulus. | Alternative extra slot when algebraic characteristic is emphasized. |

Several primary anchors explain why these recommendations are not just changes in notation:

- Arvind and Kurur prove GI∈SPP and develop algorithms for related permutation-group problems. This supports SPP as a connection to a substantial problem family, while leaving the completeness caveat intact. [*Graph Isomorphism is in SPP*, abstract and main construction](https://www.cse.iitk.ac.in/users/ppk/research/publication/AK2006GI.pdf).
- Fortnow and Rogers prove BQP⊆AWPP in Theorem 3.1 and EQP⊆LWPP in Theorem 3.8. The two upper bounds concern different quantum error models. [*Complexity Limitations on Quantum Computation*](https://lance.fortnow.com/papers/files/quantum.pdf). Morimae and Nishimura later give AWPP a restricted-postselection characterization, strengthening the case that it represents a meaningful computational boundary. [*Quantum Interpretations of AWPP and APP*, 2016](https://www.rintonpress.com/xxqic16/qic-16-56/0498-0514.pdf).
- LWPP and WPP tolerate polynomial lists of exact target values, and the LWPP robustness theorem has graph-reconstruction applications. These are substantive reasons for an exact-counting specialist to retain one or both. They do not establish that the normalization distinctions deserve more benchmark weight than counting oracles. [Hemaspaandra et al., Theorems 3.1 and 3.7, §4](https://arxiv.org/pdf/1711.01250v3).
- Rothe and Hemaspaandra relate unambiguity and bounded ambiguity to worst-case invertibility questions, and expressly distinguish this setting from cryptographic one-way functions. The paper gives a fair reason to value both UP and FewP without advertising either as a full average-case cryptography track. [*Characterizations of the Existence of Partial and Total One-Way Permutations*, §§1–2 and Corollary 3.2](https://arxiv.org/pdf/cs/9907040).
- Fournier, Malod, and Mengel prove a zero-monomial-coefficient problem C=P-complete under specified circuit restrictions, and the decision problem asking whether an arithmetic circuit has at least a given number of monomials PP^PP-complete, even for restricted depth-4 formulas. These are total Boolean decision problems about finite arithmetic-circuit descriptions. [*Monomials in Arithmetic Circuits*, Theorems 3.1 and 4.3](https://arxiv.org/pdf/1110.6271).
- Beigel and Gill systematically study modular counting and prove the prime-power identity Mod_(p^i)P=Mod_pP. Distinct-prime questions are not reproduced by adding several prime powers. [*Counting Classes: Thresholds, Parity, Mods, and Fewness*, author abstract](https://cis.temple.edu/~beigel/papers/bg-mods-tcs.html). Williams' later time–space work treats modular counting as a separate lower-bound program and records the prime/composite closure distinctions. [*Time-Space Tradeoffs for Counting NP Solutions Modulo Integers*, §1.2](https://people.csail.mit.edu/rrw/mod-lbs-journal-final.pdf).

The argument for P^PP is especially direct: Fortnow explicitly identifies P^#P versus PSPACE as the question of whether counting can simulate polynomial alternation, and explains P^PP=P^#P. The same discussion distinguishes PP's proved truth-table closure from adaptive Turing closure. This is evidence of the question's established importance, not a claim that the 1990s survey certifies its September 2026 status. [*My Favorite Ten Complexity Theorems*, §§2.8–2.9](https://lance.fortnow.com/papers/files/topten.pdf).

## P^PP, PP^PP, and CH are different choices

Use the standard containments

`PP ⊆ P^PP ⊆ PP^PP ⊆ CH ⊆ PSPACE`.

Here are elementary consequences of the definitions, separated from source quotations. They need independent checking and formal inference rules if used in the benchmark:

1. **PP^PP=PP if and only if CH=PP.** The forward direction inducts on the hierarchy levels; the reverse direction uses PP^PP⊆CH. A scored CH-versus-PP pair already captures this first-level collapse.
2. **PP^PP=P^PP if and only if CH=P^PP.** Write D=P^PP. The simulation identity PP^(P^PP)=PP^PP holds by flattening each deterministic oracle subcomputation inside a probabilistic computation, with polynomial overhead. If C₂P=D, then C₃P=PP^D=C₂P and all higher levels collapse. The reverse direction follows from D⊆C₂P⊆CH. This argument preserves the fixed oracle and query encodings; it does not substitute a different oracle at each input.
3. **PP^PP=PP implies P^PP=PP.** The latter statement says PP is closed under polynomial-time adaptive Turing reductions. This review does **not** supply a converse. Known truth-table closure is insufficient for it. Do not merge these two proposed endpoints or encode the converse merely because both are described informally as “closure of PP.”
4. **CH=P^PP does not by itself identify CH with PP.** A collapse to the deterministic counting-oracle class and a collapse to the first majority level have different endpoints.

Thus PP^PP remains valuable for questions such as its comparison with a particular quantum or circuit class, or whether higher counting levels add power above C₂P. It is not needed solely to award credit for items 1 and 2 when PP, P^PP, and CH are already scored. CH=C₂P is itself a different possible collapse that the three-node selection omits as a direct pair.

## Portfolios and precisely what they lose

The six-class common core below is UP, SPP, C=P, PP, ⊕P, AWPP. All portfolios preserve the old definitions and approved inference paths as background.

| Portfolio | Scored counting classes | Net slots versus current ten | What it emphasizes | Principal loss |
|---|---|---:|---|---|
| Conservative ten | Current ten | 0 | Fine ambiguity, complements, exact normalization | No direct P^PP or CH boundary. |
| Hierarchy eight — preferred breadth comparison | Common six + P^PP + CH | −2 | Exact, modular, approximate, adaptive, and iterated counting | FewP=UP, WPP=LWPP, and related positive fine collapses lose direct endpoints. |
| Ambiguity nine | Hierarchy eight + FewP | −1 | Restores bounded-versus-unique ambiguity | Still removes exact-normalizer and coUP endpoints. |
| Compact seven | Common six + CH | −3 | Retains a hierarchy boundary while opening three other-family slots | P^PP=PP and P^PP=PSPACE cease to be direct pairs; CH does not replace them. |
| Concrete-level eight | Common six + P^PP + PP^PP | −2 | Adaptive versus one nested majority level, with natural completeness | Loses CH-versus-PSPACE and higher-level collapse questions. |
| Modular nine | Hierarchy eight + Mod₃P | −1 | Characteristic 2 versus odd-prime modular counting | Leaves bounded-ambiguity and exact-normalizer fine comparisons in background. |
| Exact-normalizer ten | Common six + LWPP + WPP + P^PP + CH | 0 | Retains both exact-normalizer distinctions and fills oracle gaps | FewP and coUP endpoints are lost, and no counting slots are freed for other areas. |

These are editorial sensitivity cases, not rankings by difficulty. The preferred eight-slot case is most persuasive if the full roster also adds omitted space, promise, or algebraic directions. The nine-slot ambiguity case is preferable if the revision remains focused on traditional structural decision complexity. An expert emphasizing finite characteristic can reasonably select Mod₃P over FewP; an expert emphasizing natural arithmetic-circuit decision problems can choose C₂P instead of CH.

Demotion has asymmetric consequences that should be visible to reviewers:

- **coUP:** establishing UP=coUP would imply the currently unresolved UP⊆coNP, so it would still have a scored consequence with UP and coNP retained. Establishing UP≠coUP implies UP≠P, also retained. These are implications, not equivalences; individual comparisons involving coUP can still disappear, and the number of points changes.
- **FewP:** proving FewP=UP need not settle any retained endpoint in the proposed eight-class block by a known implication. Proving FewP≠UP does imply NP≠UP, since UP⊆FewP⊆NP. Keeping only the stronger upper endpoint preserves some separation credit while losing the finer positive collapse.
- **LWPP and WPP:** proving LWPP=WPP need not settle a retained pair. Proving LWPP≠WPP implies AWPP≠P from P⊆LWPP⊆WPP⊆AWPP, so it retains a scored consequence. An ordinary proof that WPP is Turing closed is not the same theorem as WPP=LWPP, and a pair-only benchmark need not reward the closure theorem on its own.
- **SPP and AWPP:** membership of GI in SPP or BQP in AWPP does not make GI complete for SPP or BQP equal to AWPP. These classes support broad questions but cannot guarantee points for every algorithm in the connected application area.

Every implication here is relative to the retained endpoints and baseline-open facts. It is a coverage explanation, not a count of future points. The revised scorer must derive consequences through background nodes before restricting credit to pairs whose two endpoints are scored.

## #P is not a missing language label

#P contains functions from binary strings to natural numbers, with polynomially many output bits. GapP contains signed integer functions. Neither is a set of languages. A statement such as `#P ⊆ NP` in an untyped class-inclusion matrix is undefined without an additional interpretation.

There is a useful language-class substitution, but its scope should be stated exactly. With ordinary binary output, the following collapse is already captured by P versus PP:

`every #P function is in FP_N  ⇔  PP=P`.

For the forward direction, compute the count or gap defining a PP language and compare it to its threshold. For the reverse direction, use polynomially many PP threshold questions to recover a polynomial-bit #P value by binary search. Nonnegative polynomial-time functions lie in #P, so the function inclusion is also equality under these conventions. [Fortnow, *Counting Complexity*, Theorem 3.5](https://lance.fortnow.com/papers/files/counting.pdf).

For a richer decision interface use **P^PP=P^#P**. A #P query returns an entire polynomial-bit integer; it is not one Boolean PP query. In particular, the one-#P-query form of Toda's theorem must not be turned into `PH⊆PP` or `PH⊆P^PP[1]`. [Fortnow, *My Favorite Ten Complexity Theorems*, Theorem 8 and §2.9](https://lance.fortnow.com/papers/files/topten.pdf).

The graph language `(x,y): f(x)=y`, threshold language `(x,t): f(x)≥t`, and bit language `(x,i): bit_i(f(x))=1` expose different predicates of the count. Each may be useful in its own problem, but selecting one as “the language encoding of #P” changes the question being scored. A function track should instead retain the domain, codomain, output encoding, and function-reduction notion. It should distinguish exact computation from approximation and sampling.

## Important directions that require a different type of target

### Total search and optimization

TFNP consists of polynomially balanced, polynomial-time verifiable relations R(x,y) that have at least one witness y for every x. A solver chooses a valid witness; the existential decision language is trivial. This is the central reason that PPAD, PPA, PPP, and PLS cannot be inserted as language-class endpoints. The original TFNP paper explicitly organizes problems such as factoring, local optimization, and equilibria around total search. [Megiddo–Papadimitriou, *On Total Functions, Existence Theorems and Computational Complexity*, 1991, abstract and §1](https://www.sciencedirect.com/science/article/pii/030439759190200L).

A faithful optional track would use the shared universe of such relations and a stated search reduction. A reduction from R to S supplies polynomial-time functions f and g such that **every** valid S-solution y for f(x) yields an R-solution g(x,y). The reduction cannot choose a conveniently solvable target witness. A tractable base class can consist of total relations with polynomial-time selectors; call it `FP-search` or define that convention explicitly, rather than silently identifying a relation class with single-valued FP functions. The parity-argument classes were introduced in precisely this search setting. [Papadimitriou, *On the Complexity of the Parity Argument and Other Inefficient Proofs of Existence*, 1994](https://kam.mff.cuni.cz/~matousek/cla/papadimitriou-parityarguments-complexity.pdf).

An exploratory search portfolio is FP-search, TFNP, PPAD, PLS, PPA, and PPP, with CLS as a possible additional endpoint if continuous optimization is emphasized. This is **not** a proposal to add seven names without auditing their current relations. CLS=PPAD∩PLS is a major already-known equality and cannot be offered as a new open target. Its proof and the related gradient-descent problems demonstrate that search-class questions can represent important advances beyond the language matrix. [Fearnley–Goldberg–Hollender–Savani, *The Complexity of Gradient Descent: CLS=PPAD∩PLS*, 2021](https://www.cs.ox.ac.uk/people/paul.goldberg/papers/STOC2021-FGHS.pdf).

For equilibria, exact multi-player solutions can require irrational coordinates; an unqualified “Nash” target is therefore unsafe. A canonical PPAD example can instead specify two-player games with rational payoff encodings and polynomial-bit rational equilibrium witnesses, or an explicit approximation formulation. The distinction belongs in the scientific target, not an implementation footnote. The original Nash-complexity research provides the PPAD connection, but its exact and approximate formulations must be read with care. [Daskalakis–Goldberg–Papadimitriou, *The Complexity of Computing a Nash Equilibrium*, 2009](https://epubs.siam.org/doi/abs/10.1137/070699652). Etessami and Yannakakis distinguish proximity to an actual equilibrium from small payoff regret and introduce FIXP for algebraic fixed points; those distinctions preclude treating all these tasks as the same finite-witness PPAD problem. [*On the Complexity of Nash Equilibria and Other Fixed Points*, 2010](https://epubs.siam.org/doi/10.1137/080720826).

### Algebraic complexity

VP and VNP are classes of polynomial families over a specified field. For VP, the number of variables, degree, and arithmetic-circuit size are polynomially bounded in the family index. VNP permits an exponential Boolean sum of a VP family. The choice of field, characteristic, allowed constants, and uniformity changes the mathematical statement. These are not ordinary decision-language classes.

If broader tracks are authorized, **VP_Q versus VNP_Q** merits a direct proposal, accompanied by an explicit constant model. A constant-free VP⁰/VNP⁰ variant is a separate candidate, not a harmless alternate spelling. Bürgisser's definitions and discussion of the permanent make the constant-free distinctions explicit. His counting-hierarchy connection also supplies evidence for CH within the language roster. [*On Defining Integers in the Counting Hierarchy*, §§2.1–2.2](https://eccc.weizmann.ac.il/report/2006/113/download/). The foundational algebraic completeness framework is Valiant's [*Completeness Classes in Algebra*, 1979](https://doi.org/10.1145/800135.804419).

Arithmetic-circuit size counts operations rather than the bit cost of rational intermediates. Allowing arbitrary field constants also differs from requiring polynomial-bit encodings or a uniform generator. A Boolean permanent-value decision problem does not silently identify these models. In characteristic 2 the permanent equals the determinant, so a permanent-based VNP-completeness slogan must not be transferred unchanged across characteristics.

PIT adds a second limitation of the original scoring form. Derandomizing an appropriately specified polynomial identity test is a major target, but the Kabanets–Impagliazzo theorem gives a **disjunction** of Boolean and arithmetic circuit lower bounds. Even if both endpoint universes are present, proving a disjunction does not prove either individual inclusion's negation. [*Derandomizing Polynomial Identity Tests Means Proving Circuit Lower Bounds*, abstract and main theorem](https://www2.cs.sfu.ca/~kabanets/papers/poly_derand.pdf). Rewarding PIT itself or the disjunctive theorem requires registered problem/resource targets or compound propositions; adding VP and VNP alone does not solve that issue.

### Fine-grained and parameterized computation

ETH and SETH concern the exponent as a function of the number of variables in SAT instances, with quantifiers over clause width and exponent savings. They cannot be read off from an ordinary P/NP comparison. ETH implies P≠NP, so that direction already has a scored consequence. Refuting ETH by a subexponential but superpolynomial algorithm need not settle a familiar polynomial-class pair. A uniform `2^(0.99n) poly(m)` algorithm for unrestricted CNFSAT would refute SETH without thereby giving P=NP. The foundational exponential-time paper makes the parameter and quantifier choices explicit. [Impagliazzo–Paturi, *On the Complexity of k-SAT*, 2001, pp. 367–369](https://cseweb.ucsd.edu/~paturi/myPapers/pubs/ImpagliazzoPaturi_2001_jcss.pdf); [Cygan et al., *On Problems as Hard as CNFSAT*, 2011/2016](https://arxiv.org/abs/1112.2275).

Adding DTIME(n²), a generic SUBEXP class, or E does not faithfully replace the ETH/SETH/APSP/3SUM targets. The input measure, machine or RAM model, numerical bit width, randomized-error convention, and reduction's exponent loss matter. A typed quantitative-problem track is the clean option. Parameterized classes such as FPT and W[1] likewise need objects carrying an instance parameter; they are not extra names for total binary languages under the existing input-length convention. This review flags these directions for a separate source-led selection process rather than assigning speculative cross-type inclusions.

### Approximate counting and sampling

The permanent FPRAS is an example of a major advance that differs fundamentally from exact #P computation. It estimates the permanent of a nonnegative matrix to a specified relative error with high probability; the signs and error notion matter. [Jerrum–Sinclair–Vigoda, *A Polynomial-Time Approximation Algorithm for the Permanent of a Matrix with Non-negative Entries*, abstract and §1](https://www.dcs.ed.ac.uk/home/mrj/PermanentRev.pdf). An approximate-counting track must specify relative or additive error, zero values, confidence, and running-time dependence on accuracy. A sampling track must specify distributions and distance, including exact versus approximate sampling. A decision-language inclusion is not a substitute for these task definitions.

## Architecture consequences if the scientific scope expands

The scored/background distinction is useful under either outcome. It lets the benchmark retain mathematical vocabulary without allocating a scored slot to each inference helper. It does not make a lost question free: a theorem confined to background endpoints can still earn zero unless its consequences reach a scored pair.

If broader tracks are selected, each endpoint needs an object universe and conventions. Legal inclusion pairs require the **same** universe: languages, promise problems, total search relations, functions with fixed output conventions, polynomial families over a fixed field, or another explicitly defined type. Cross-track consequences must be registered mathematical bridges. A generic transitivity rule cannot connect a function inclusion, a search reduction, and a language inclusion just because their labels resemble one another.

Maintain the approximately 40–50 scored-endpoint budget across the selected portfolios if that remains the user's constraint; do not quietly add an extra matrix of incomparable objects. Report per-track eligible-pair counts and the changed aggregate denominator. One point per open legal pair remains coherent, but it weights a large track quadratically and a two-endpoint algebraic track sparsely. That is a policy consequence for human review, not a reason to invent extra algebraic classes.

Problem-level, resource-bound, and compound-proposition targets would be a further scope change. They address real coverage gaps, but they should not be smuggled into the class roster using singleton “classes.” In particular, proving that a particular problem is efficiently solvable yields a whole-class inclusion only with a relevant completeness theorem and compatible reduction closure.

## Checks required before a roster decision becomes a release

1. Settle language-only versus typed-track scope. The recommendation above does not assume authorization for new tracks.
2. Cross-review the two elementary counting-hierarchy collapse equivalences and the non-equivalence warning about adaptive PP closure. Keep any unproved converse out of the rule library.
3. Audit each newly selected endpoint against literature through September 1, 2026. This review establishes motivation and exact target definitions; it is not a complete new all-pairs classification audit.
4. Review Mod₃P's prime-specific closure and oracle conventions if it is selected. Do not transfer composite-modulus results or circuit MOD lower bounds by name.
5. Publish a loss list alongside gains, including positive FewP=UP and LWPP=WPP collapses if their endpoints are demoted. Preserve the old release's scores and disclose that a new roster changes weighting.
6. Obtain human scientific review of the final family balance. Agreement among these AI-generated reviews is useful cross-checking, not evidence of a community consensus or a calibrated importance ranking.
