# Round 2: classical, circuit, and space cross-review

No incorrect classification or concrete operational-model mismatch was found in the audited groups. The review supports the newly added NEXP ⊄ Θ₂P seed and its NE consequence. It also supplies a primary source for the 264 separations arising from nonuniform circuits and recursive target classes.

The reviewed snapshot is `03a20575c82bab512158a0bb0bb7766c4066b5c8ecc645c012d16053ad1714e2`: 709 inclusions, 413 separations, and 1378 candidate pairs. This is a targeted adversarial review, not a certification of every candidate pair. The [JSON dossier](audit-round2-cross-classical.json) records 68 reviewed seed IDs, exact source/model checks, file hashes, and every lost classification in the ablation experiments.

## Nonuniform circuits versus recursive languages

The six nonuniform entries are AC⁰, ACC⁰, TC⁰, NC¹, P/poly, and NP/poly. The other 44 entries have only recursive languages under the stated total-language and finite computable-gate conventions.

For an undecidable set S of natural numbers, let L contain every word of length n exactly when n ∈ S. A circuit family can choose a single constant gate independently at each length. This is a size-one, depth-zero family in the exact Lean model. A decider for its language would decide S by running on 0ⁿ. Thus it witnesses all 264 ordered noninclusions from the six nonuniform classes into the 44 recursive ones.

[Borodin1977, printed p738, immediately after Theorem4](https://www.cs.toronto.edu/~bor/Papers/relating-time-space-size-depth.pdf) explicitly describes the same phenomenon: nonrecursive length languages with trivial circuits. Add this primary source to the 44 AC⁰ seed citations; it improves provenance without changing a label.

The recursive-target check includes the less obvious cases. The exact quantum definitions generate finite circuits using only H, T, X and CNOT. Their constants are algebraic. QMA witness optimization can be decided, without an efficiency claim, by real algebraic quantifier elimination on a finite-dimensional normalized state and the acceptance inequality. Arbitrary witness amplitudes therefore do not supply undecidable advice. For oracle classes, the oracle is one fixed language at a fixed finite level. For machine classes, any existential time bound is dominated by a computable polynomial or exponential bound, or the fixed machine is already required to halt on every input. The absence of a recursive enumeration of valid semantic machines does not make their individual languages nonrecursive.

## Circuit size and uniform NC

`Circuits.Program.encodingSize` charges every gate and every wire occurrence, including repeated inputs. It is not the literal serialized bit length, but the omitted index lengths add only a logarithmic factor. ACC's modulus is chosen once outside the family quantifier, so it cannot hide a growing amount of advice. TC⁰ is explicitly a majority-gate model matching the catalog. Ties at exactly half are a harmless convention because constant inputs convert between the usual variants.

`UniformCircuits.logspaceUniform` requires a concrete transducer to emit the entire circuit with logarithmic work space and polynomial time. Its output tape is append-only and unreadable. Unary circuit indices enlarge polynomial-size descriptions only polynomially. The same circuit must be generated on every input of a given length. There is no arbitrary family label standing in for uniform generation.

One detail deserves an explicit transfer argument: circuit depth counts only the output cone. Simply pruning unused gates would hide a reachability problem in a claimed logspace generator. Instead, for a known polylogarithmic output-depth bound d(n), create d(n)+1 layers of copies of every gate. Initialize input/constant gates at layer zero and compute each next layer from the preceding layer. By layer d(n), the designated output has its correct value. Every gate in the transformed circuit has polylogarithmic depth; the size stays polynomial and a logspace generator can emit it using counters and repeated access to the original generator. This avoids assuming L=NL.

A direct recursive evaluator stores a polylogarithmic stack of logarithmic-size gate addresses. Regenerating predecessors uses logarithmic additional space. Hence the exact NC model has a polylogarithmic-space simulation. [Borodin's Lemma1 and Theorem4](https://www.cs.toronto.edu/~bor/Papers/relating-time-space-size-depth.pdf) establish the published space/depth connection; the weaker stack bound already suffices here. The space hierarchy therefore supports PSPACE ⊄ NC. It does not settle P versus PSPACE.

## SC uses simultaneous resources

The SC definition chooses one deterministic machine, then gives separate halting witnesses for its polynomial time and polylogarithmic space predicates. These witnesses still constrain the same computation. Terminal configurations are frozen by `DMachine.after`, so both witnesses extend the same earliest halt. That earliest prefix meets the time bound and every space bound. This is the intended simultaneous-resource class.

The work-space measure counts the represented visited interval, including blanks. Erasing does not reduce the charged interval; moving within it preserves the length. The input head cannot move beyond the input endmarkers. No uncharged head position or readable output tape supplies hidden storage.

## EXPSPACE ⊄ NP/poly

I independently checked the benchmark's diagonalization, including nondeterministic witnesses and memory use. At length n, let s = 2^⌊n/4⌋. A bounded-fan-in nondeterministic circuit of at most s gates uses at most O(s) relevant witness bits after renaming. Its description takes O(s log(n+s)) bits, so there are fewer such circuits than the 2^(2ⁿ) possible truth tables.

Enumerate candidate truth tables of length 2ⁿ. For each candidate, enumerate every circuit description within the size bound. Test agreement by enumerating inputs and all assignments to the circuit's relevant witness bits. Some truth table is omitted by every circuit. The algorithm stores one candidate table, one circuit, the input and witness counters, and one circuit evaluation. This uses O(2ⁿ) space and finite, unrestricted time. Small lengths can be handled by constants.

Every NP/poly verifier yields a polynomial-size nondeterministic circuit family once its polynomial advice is fixed. Every fixed polynomial eventually lies below s. The resulting diagonal language is therefore in EXPSPACE and outside NP/poly. This argument has no corresponding EXP-time bound and supplies no separation of EXP or PSPACE from NP/poly.

The exact advice definition is appropriate: advice depends only on input length; its length is polynomial; the verifier is a single finite-control machine with a polynomial bound on every encoded or malformed word; witness length is a finite polynomial; and the triple encoding is injective with linear expansion. This checks the mathematical application of the [recorded derivation](classical-notes.md), rather than treating its source label as sufficient evidence.

## Hierarchies and the union over exponents

E and NE use linear exponential bounds with an arbitrary fixed constant. EXP and NEXP use arbitrary fixed polynomial exponents. Polynomial overhead in simulating fixed multitape machines preserves all four classes, including E and NE. Fixed initial input lengths are absorbed by finite control and constants.

For E versus P and NE versus NP, choose a hierarchy bound 2ⁿ. Every polynomial is smaller by the required asymptotic margin. For EXP versus E and NEXP versus NE, use 2^(n²); every fixed 2^(cn) is smaller. This is a single witness outside the whole smaller union, not a separate lower bound for each exponent. [Seiferas–Fischer–Meyer1978, Corollary4.1, printed p155](https://www.researchgate.net/publication/220430544_Separating_Nondeterministic_Time_Complexity_Classes) explicitly states the nondeterministic separation from the union of bounds T₁ with T₁(n+1)=o(T₂(n)). The linked full text was uploaded by coauthor Albert R. Meyer.

For the space cases, every polylogarithmic bound is eventually below n^(1/2), while every polynomial bound is eventually below 2^(n/2). Deterministic space hierarchy witnesses at n and 2ⁿ therefore give the needed PSPACE and EXPSPACE separations. [Seiferas1977, §2 and §4](https://www.researchgate.net/publication/220574510_Techniques_for_Separating_Space_Complexity_Classes) supplies the model conventions and diagonalization results; its author-uploaded full text was accessible when the publisher page was not. The original deterministic-time PDF timed out in this pass, so the JSON distinguishes that access limitation from the checked application of its accepted theorem.

## NEXP and NE versus Θ₂P

[Buhrman–Fortnow–Santhanam2009, Theorem6, printed p5](https://eccc.weizmann.ac.il/report/2009/064/download/) separates NEXP from polynomial time using at most nᶜ NP queries and nᶜ advice bits, for each fixed c. Taking c=1 covers Θ₂P: logarithmically many queries are eventually at most n, and no advice is required. Finite exceptional lengths may be hardwired. The polynomial running-time exponent remains unrestricted in this theorem.

If NE were contained in Θ₂P, a language in NEXP could first be padded from length n to p(n)=(n+2)ᵏ to obtain an NE language. Running its Θ₂P algorithm on the polynomial-length padding takes polynomial original time and uses O(log p(n))=O(log n) NP queries. That would put NEXP in Θ₂P, contradicting the theorem. The exact Lean oracle model matches these requirements.

[Fu–Li–Zhang2010, Theorem11](https://faculty.utrgv.edu/liyu.zhang/blz10-sepNE-joco.pdf) independently states the fixed-query/advice NEXP bound. The 1994 Fu–Li–Zhong result is also cited by [Fortnow–Klivans2004, §4](https://eccc.weizmann.ac.il/report/2004/103/download/). These are corroborating anchors; the accepted seed has a directly inspected proof statement in BFS2009.

The fixed c matters. Taking an unrestricted union of query exponents on the right would not establish NEXP ⊄ Δ₂P. Six associated noninclusions into coNP, coRP and coUP also have an elementary independent derivation: NE ⊆ coNP would force NP=coNP and then NE ⊆ NP, contradicting the hierarchy.

## Measured dependency and remaining risk

The following experiment removes each group of seed facts, keeps all other facts and rules, and reruns the current closure engine. Counts measure labels lost by that engine; they are neither probabilities nor an exhaustive mathematical consequence count. Alternate proofs can make a valid seed's removal have zero effect.

| Removed seed group | Seeds | Labels lost |
| --- | ---: | ---: |
| nonuniform_AC0_vs_recursive | 44 | 264 |
| EXPSPACE_not_NPpoly | 1 | 4 |
| E_not_P | 1 | 0 |
| EXP_not_E | 1 | 1 |
| NE_not_NP | 1 | 0 |
| NEXP_not_NE | 1 | 2 |
| PSPACE_not_SC | 1 | 1 |
| PSPACE_not_NC | 1 | 3 |
| EXPSPACE_not_PSPACE | 1 | 16 |
| NEXP_not_Theta2P | 1 | 8 |
| NE_ACC0_and_NEXP_ACC0 | 2 | 2 |

The union of the lost-label sets has 301 elements; group counts must not be added without checking overlaps. The complete lists and reproduction method are in the JSON dossier.

No new numerical bound on expected remaining classification errors follows from this clean targeted pass. The largest correlated risk would be a mistaken nonuniformity convention affecting 264 labels, but both the exact definitions and a one-gate primary-source-backed construction now support that block. The advice diagonalization, uniform NC normalization, SC interpretation, and Θ₂P query transfer likewise have explicit checked arguments and no identified counterexample.

The unproved machine-encoding equivalences are formalization work, which the user waived for existing results. The relevant remaining uncertainty is whether a cited theorem has been misapplied or whether historical literature outside this review settles another candidate pair. Future flaws in currently accepted proofs are excluded by the user's stated risk model. There is no calibrated error distribution here that would justify assigning tiny probabilities to these clusters or declaring the entire benchmark's expected remaining errors below two.


## Independent review of the May 2026 separation claim

[Montoya, arXiv2605.08555v1, submitted8May2026](https://arxiv.org/html/2605.08555v1), claims NL≠LogCFL. Admitting LogCFL ⊄ NL would change **70** current candidate labels. I independently read the relevant definitions and arguments and recommend withholding those labels because of present mathematical failures in the proof.

Theorem18, printedpp10–11, has a concrete counterexample. Let D={aⁿbⁿcⁿ:n≥0} and let T be its complement over {a,b,c}*. T is context-free: take the union of words outside a*b*c*, words aⁱbʲcᵏ with i≠j, and those with j≠k. Let L={ε} over a disjoint alphabet {d}. Restrict the paper's masked concatenation T⊗L to strings w#d with exactly one local factor. If w∈T, the selected cofactor is d, so the string is rejected. If w∉T, the selected concatenation is ε, so it is accepted. The restriction is exactly D#d. Closure under regular intersection and homomorphism would then make D context-free, a contradiction. Thus the claimed general closure lemma is false. Its PDA simulation wrongly uses a nondeterministic recognizer as if it computed a membership bit on every branch.

Theorem35, printedpp15–17, has two independent missing arguments. First, an arbitrary automaton need not call the local recognizer and global controller that the proof assumes; no normalization preserving configuration entropy is established. Second, uniformity on complete configurations does not survive arbitrary projection. For a uniform variable on three points with projection fibers of sizes2 and1, the local probabilities are2/3 and1/3. Its entropy is not that of the uniform distribution on two points.

The same finite example also challenges the last conditional-entropy identity: the conditional entropy is2/3 bit, while a variable uniform on an m-element support has entropy log₂m. No integer m has log₂m=2/3. The manuscript supplies no equipartition or support bijection that excludes this discrepancy. Its induction explicitly uses the disputed identity.

These checks concern the submitted argument. They neither refute NL≠LogCFL nor rule out a different proof. Venue and acceptance status play no role in the decision.

## Judgmental estimate requested after review

For errors attributable to this classical/circuit/space scope, my working estimate is **about1 wrong current pair label**, with an explicitly subjective sensitivity envelope of **0.14–8.21**. This is neither a confidence interval nor a rigorous global bound. I did not tune it to the benchmark's stopping target.

| Residual event | Subjective probability range | Affected labels if it occurs |
| --- | ---: | ---: |
| Shared mistake in the nonuniformity contract |0.01%–0.2%|264|
| Localized operational-model transfer error |0.2%–1%|1–12|
| Misapplication/transcription of an accepted seed theorem |0.2%–1%|1–16|
| Another older separation omitted from the historical record |5%–20%|2–16|
| Recent pre-cutoff result overlooked |1%–6%|1–70|

The contract risk receives the smallest range because both the exact definitions and a constant-gate construction were checked. The old-literature risk remains larger because this project actually missed the Θ₂P separation before the first-round review, and this targeted round was not another census. The recent-result range retains a low-probability large consequence count;70 is the measured size of the Montoya claim's consequences, whose current proof has now been rejected on mathematical grounds.

The JSON records working values behind the rounded estimate and the endpoint calculation. Overlapping events may count the same label twice. Root reports a complete SAT check within the present finite rule theory, so this estimate assigns no additional logical-closure omission conditional on that check being correct. Missing theorems are separate. Future flaws in accepted proofs remain excluded. The upper sensitivity estimate is well above two, so this round alone does not justify the global stopping criterion.
