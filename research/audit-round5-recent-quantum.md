# Round 5: recent quantum/SZK literature and quantum normalization

No additional established ordinary inclusion or separation was found. This is a bounded search of recent primary indexes and selected papers, not a certification that every remaining candidate is historically open. The machine-readable companion records each entry, review level, exclusion and uncertainty allowance.

The reviewed dataset has digest `e09e6cf8dfa1233f754dc4ecf935ea7db6831f24046cde0cbb1eebfedf4349c3`. The 475 ordered pairs touching BQP, QCMA, QMA, coQMA or SZK contain 104 known inclusions, 40 known noninclusions and 331 candidates. These are the scope of the additional recent-literature allowance; they are not 475 independently reviewed theorems.

## What was searched

| Primary index | Inventory | Review performed |
|---|---:|---|
| [Quantum volume 8](https://quantum-journal.org/volumes/8/) | 365 articles in 2024 | Parsed all entries; broad keyword filter and selected primary scope checks |
| [Quantum volume 9](https://quantum-journal.org/volumes/9/) | 378 articles in 2025 | Same |
| [Quantum volume 10](https://quantum-journal.org/volumes/10/) | 253 entries; 241 published by September 1, 2026 | Same; 12 later articles excluded |
| [TQC 2024](https://drops.dagstuhl.de/entities/volume/LIPIcs-volume-310), [2025](https://drops.dagstuhl.de/entities/volume/LIPIcs-volume-350), [2026](https://drops.dagstuhl.de/entities/volume/LIPIcs-volume-389) | 32 research-paper titles | All titles screened; selected abstracts checked |
| [TQC 2026 accepted talks](https://tqc-conference.org/2026/accepted-papers/) | 87 titles | All titles screened; selected author-submitted abstracts checked |
| [QIC publisher index](https://www.rintonpress.com/journals/qiconline.html) | 35 PDF-linked 2024 titles | All titles screened; selected theorem statements checked |

The Quantum inventory has 984 cutoff-eligible entries. The broad title filter selected 94 for manual title screening; the other 890 are an inventory only. The filter is preserved in JSON, including terms for complexity, QMA/QCMA/BQP, proofs, zero knowledge, PCPs, postselection, advice, hardness, universality and computational advantage. The TQC and journal counts overlap and must not be added as unique-paper counts. TQC 2026 proceedings were published August 25; individual accepted-talk page versions were not independently archived at the cutoff.

The retrieved QIC index ends at volume 24 (2024). It does **not** establish coverage of QIC 2025–2026. Targeted arXiv searches supplement the indexes, but do not enumerate the full preprint corpus. QIP workshop lists, ACM Transactions on Quantum Computing, Quantum Information Processing and all physics journals were not comprehensively indexed. Two 2026 stoquastic-Hamiltonian pages and the July 20 quantum-Zeno k-SAT page failed retrieval; their titles were screened, but their abstracts are not claimed as reviewed.

There are 27 selected primary scope checks. Most are abstract checks; the JSON identifies the passages where theorem statements and model definitions were inspected. A title or abstract check does not amount to verification of the paper's proof.

## Results that could otherwise be misclassified

The new [QSZK upper-bound paper](https://arxiv.org/abs/2512.11597v2), initially posted December 12, 2025 and revised June 28, 2026, restricts the honest prover's space in a two-message quantum protocol. It does not replace the ordinary PSPACE bound by PP or BQP. Polynomial time in the dimension of a quantum state can be exponential in its number of qubits.

[Order interference](https://arxiv.org/abs/2503.21400) gives an SZK simulation in BQP with an additional oracle. This is not an SZK-to-BQP inclusion. [Space-bounded quantum interactive proofs](https://arxiv.org/abs/2410.23958) likewise use different classes: the verifier's space and intermediate measurements are constrained.

Theorem 1.1 of [the fully quantum black-box simulation barrier paper](https://arxiv.org/html/2409.06317v2) does imply BQP membership from its constant-round protocol hypothesis. Ordinary SZK membership does not supply that hypothesis. Section 1.4 explicitly distinguishes the expected-QPT notion used by the theorem from coherent-runtime simulation. It would be incorrect to drop these conditions and claim SZK or QMA is contained in BQP.

[Separating quantum and classical advice with good codes](https://arxiv.org/abs/2602.09385) proves oracle separations. [Unique quantum witnesses and approximate counting](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2026.10) also relies on a quantum oracle for its class separations. Neither changes an ordinary roster label. [Quantum-input promise classes](https://arxiv.org/abs/2411.03716) have quantum states as inputs; their unconditional separations do not transfer to total languages over bitstrings.

The [pure quantum polynomial hierarchy result](https://drops.dagstuhl.de/storage/00lipics/lipics-vol374-icalp2026/html/LIPIcs.ICALP.2026.103/LIPIcs.ICALP.2026.103.html) concerns quantum quantifiers and QMA(2), not the classical PH. [Unentangled interactive proofs](https://arxiv.org/abs/2509.15319) and [internally separable witnesses](https://arxiv.org/abs/2410.19152) change the proof model. Their NEXP characterizations do not show NEXP is contained in ordinary QMA.

The QIC [state-synthesis paper](https://www.rintonpress.com/xxqic24/qic-24-910/0754-0765.pdf) has a conditional route from a synthesis separation to BQP≠QCMA. Its unconditional impossibility of reducing synthesis error does not establish that premise. The [unconditional shallow-circuit advantage](https://quantum-journal.org/papers/q-2026-08-12-2188/) is for sampling with restricted classical circuits, not an ordinary BQP/BPP separation. The [uniformity-testing algorithm](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.TQC.2025.7) has dimension-dependent cost; succinct exponentially large output domains do not yield an SZK algorithm in BQP.

[QMA has perfect completeness](https://arxiv.org/abs/2609.13032) was submitted September 11, after the cutoff. It is excluded regardless of validity; this audit does not review its proof. QMA1 is also outside the roster.

## Separate recent-literature allowance

The earlier recent census was mainly classical/time/counting. I do not extend its numerical allowance to this newly examined scope. My additional subjective expectation is **0.15 wrong current pair labels**:

| Residual event over the whole scope | Probability | Mean additional distinct affected labels if it occurs | Contribution |
|---|---:|---:|---:|
| At least one missed recent localized quantum/SZK result or corollary | 0.025 | 4 | 0.10 |
| A missed recent result with a broad additional propagation footprint | 0.002 | 25 | 0.05 |

Each row concerns an event anywhere in its scope, not one event per paper or pair. Conditional impact counts a union of additional distinct wrong labels. It must not be multiplied again by the number of candidates. Labels already attributed to another recent-paper component should not be charged twice.

These are judgmental values, not calibrated probabilities. At fixed conditional means, the stated probability sensitivities give 0.025–0.57 expected labels; allowing the conditional impact ranges to vary gives 0.007–1.4. They are not confidence intervals. A subtle corollary in an unindexed paper remains possible. The values were not chosen to meet the global stopping threshold. Future flaws in currently accepted proofs are excluded, as requested; present scope mistakes and omissions are included.

## Independent review of the new normalization module

I independently read the exact definitions and all new statements and proofs in `quantum/InclusionQuantum/Normalization.lean`. Its frozen SHA-256 is `c2e67506a2fb2d0cd94c51974dc4b9ad68b95bae5fd8700b5ab3a600d0a0ebc1`. The author reports a clean Lean 4.19 build of the quantum modules and 11 axiom audits, using one CPU and 8 GiB. I did not run a second build. The reported axioms are only `propext`, `Classical.choice` and `Quot.sound`; the module is now imported by the mandatory quantum entry point.

The statements refer directly to the model used by the benchmark:

- `gate_preserves_normSquared` covers every actual gate and every state, without assuming normalization or unitarity. For Hadamard, the two-amplitude identity cancels the cross terms, and the flip permutation accounts for the finite sum. The exact T phase has norm one. X and CNOT are permutations; the CNOT proof uses the required distinct control and target.
- `circuit_preserves_normSquared` follows the precise fold in `Circuit.run`.
- `initialState_preserves_normSquared` constructs the inverse between witness basis strings and valid input/ancilla support. It includes every wire, including the extra ancilla, and handles zero witness amplitudes correctly through a nonzero-support sum bijection.
- `acceptance_bounded` bounds the actual family acceptance expression after the actual register embedding. `empty_witness_normalized` handles the single empty basis assignment used by BQP.

No statement substitutes a different model or assumes the desired identity. I found no concrete semantic defect. The results do not prove efficient universal compilation, amplification, complete textbook equivalence, or all classical/quantum simulation inclusions. Norm preservation alone is not a universality theorem.

This is meaningful additional evidence for the existing quantum definition/application risk row. I recommend replacing its event probability **0.006 with 0.004**, retaining the conditional mean of 35 distinct affected labels: **0.21 becomes 0.14**. The sensitivity interval at that fixed impact is 0.035–0.525. A modest one-third reduction reflects the newly discharged normalization and indexing risks, while preserving substantial uncertainty about model and theorem transfer. Do not alter the counting, SZK or seed-interpretation rows because of these proofs, and do not subtract this reduction from the separate recent-literature allowance.
