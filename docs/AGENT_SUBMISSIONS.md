# Submitting a textbook-level argument

Write the new argument using standard complexity-theory results. You do not need to reconstruct a tape machine or re-prove a paper merely to use its theorem. The support library provides familiar class names, polynomial reductions, verifier characterizations, counting algebra, and oracle/hierarchy interfaces. Additional published results can be cited with their exact Lean statements.

The final theorem still refers to the benchmark's fixed class definitions. The library supplies the bridges to those definitions; a reviewer checks any additional bridge that your argument needs.

## Start with the target

From the benchmark checkout:

```sh
python3 -m inclusion_bench submission-init my-proof --claim inclusion NP P
```

This creates `proof.lean`, `claims.json`, `literature.json`, and instructions for an agent. The editable target is simply:

```lean
open InclusionBench InclusionBench.Support
open InclusionBench.Support.Classes

namespace Submission

theorem result_1 : Includes NP P := by
  sorry

end Submission
```

Replace the placeholder with the new argument. `NP` and `P` are definitional aliases for the frozen benchmark targets. `Includes NP P` means that every language in NP belongs to P. All 61 scored and background class definitions have these short aliases. A separation uses `NonIncludes A B` and requires a language in A that is outside B.

This scaffold does not assume the requested result. An unfinished proof containing `sorry` fails checking.

## Find existing results

```sh
python3 -m inclusion_bench theorems --search 'verifier'
python3 -m inclusion_bench theorems --search 'GapP' --json
python3 -m inclusion_bench theorems --search 'PSPACE'
```

The catalog includes the existing benchmark facts and implication rules, their readable `InclusionBench.Known.*` theorem names, support declarations, exact types, and citations. The support source files are under `support/InclusionSupport/`. The names below live in `InclusionBench.Support` unless qualified otherwise.

| Argument step | Interface |
| --- | --- |
| Use familiar classes | `Support.Classes.P`, `NP`, `BPP`, `PSPACE`, `QMA`, and the other class aliases |
| Show that a mathematical predicate is in P | `p_of_predicate`, `p_iff_predicate` |
| Give an NP witness relation | `PolynomialRelation`, `np_of_relation`, `np_iff_verifier` |
| Give a coNP universal certificate condition | `coNP_of_forall` |
| Combine polynomial-time predicates | `polynomialPredicate_and`, `polynomialPredicate_or`, `polynomialPredicate_not` |
| Pair inputs or compare computed values | `polytime_pair`, `polytime_first`, `polytime_second`, `polynomialPredicate_eq` |
| Iterate over polynomially many indices | `polynomialPredicate_forall_range`, `polynomialPredicate_exists_range` |
| Build or compose polynomial reductions | `reduction_intro`, `reduction_trans`, `reduction_complement` |
| Reduce a class containment to a complete problem | `includes_iff_complete_problem`, `includes_of_hard_problem` |
| Combine GapP functions | `gapP_add`, `gapP_sub`, `gapP_mul`, `gapP_pow`, `gapP_int` |
| Recognize a counting class | `pp_of_gap`, `spp_iff_characteristic` |
| Use oracle monotonicity | `pOracle_mono`, `npOracle_mono`, `ppOracle_mono` |
| Prove containment of a finite hierarchy | `ph_in_of_npOracle_closed`, `ch_in_of_ppOracle_closed` |

For example, the common complete-problem argument is a short theorem:

```lean
open InclusionBench InclusionBench.Support

example {source target : ComplexityClass} {problem : Language}
    (complete : PolynomialComplete source problem)
    (closed : ClosedUnderPolyReductions target)
    (algorithm : target problem) : Includes source target :=
  (includes_iff_complete_problem complete closed).mpr algorithm
```

The three hypotheses are explicit mathematical obligations. Established completeness and closure results can come from the trusted catalog or from cited dependencies. The new algorithm or argument must still be proved.

The predicate combinators preserve polynomial running time while handling the machine simulation internally. Bounded iteration is over a polynomial number of numeric indices; it does not treat exhaustive search over exponentially many bitstrings as polynomial time.

An NP proof can be stated using a mathematical relation:

```lean
open InclusionBench InclusionBench.Support

example {language : Language} {relation : Word → Word → Prop}
    (efficient : PolynomialRelation relation) (bound : List Nat)
    (correct : ∀ input, language input ↔ ∃ certificate,
      certificate.length = Counting.polynomialValue bound input.length ∧
      relation input certificate) : Machines.nondeterministicPolynomialTime language :=
  np_of_relation efficient bound correct
```

`efficient` states polynomial-time decidability of the relation. An existing algorithm can supply that fact through the support library or a cited theorem. The witness bound is a polynomial coefficient list: `[3, 2, 1]` represents `3 + 2n + n²`. The trusted NP characterization handles the fixed encoding, machine simulation, and witness padding. It does not accept a separate algorithm for each input or an unspecified nonuniform family.

The checked examples in `tests/lean/Support*Tests.lean` cover these patterns and counting/oracle arguments. They are infrastructure examples, not solutions to open benchmark questions.

## Cite a missing published theorem

Declare its precise type in `proof.lean`, under the reserved submission namespace `Literature`:

```lean
axiom Literature.paper_lemma : YOUR_EXACT_LEAN_STATEMENT
```

Use `Literature.paper_lemma` in the new proof. Add the citation to `literature.json`:

```json
{
  "requests": [{
    "name": "Literature.paper_lemma",
    "statement": "The exact mathematical statement, explained for a reader",
    "sources": [{
      "title": "Actual paper or textbook title",
      "url": "https://...",
      "locator": "Theorem number and page",
      "publication_date": "1994"
    }],
    "rationale": "Why its hypotheses, uniformity, encoding, error bounds, and other relevant conventions match this use"
  }]
}
```

Replace the placeholders with the actual theorem and citation. Older sources may use a year or year-month. A date near the September 1, 2026 cutoff needs enough precision to establish eligibility. The JSON description is for the reader; the auditor reconstructs the actual Lean type independently.

Citations do not automatically authorize axioms. The checker returns `needs_literature_review` after verifying that the new argument follows from the listed dependencies. A maintainer then checks the published statement and its applicability. **Formalizing the cited theorem's original proof is not required.** A new result cannot be made trusted by citing it as its own dependency.

Reviews bind the exact declaration, all its local defining dependencies, its citation, the benchmark dataset, the target baseline, and the trusted library/checker versions. A local definition cannot quietly change the meaning of an approved proposition. Changing only the new proof body can reuse the approval; changing its targets, supporting definitions, or citations requires a new matching review. A later rejection revokes the prior approval.

## Check the submission

Use the [verifier setup instructions](PROOF_REVIEW.md#set-up-a-public-linux-verifier) to prepare Lean, its pinned dependencies, and Docker. Then run:

```sh
python3 -m inclusion_bench check-submission my-proof \
  --runtime .tools/proofcheck-runtime.json
```

The report is written to `my-proof/proof-report.json`. A submission may keep its own runtime configuration at `my-proof/.tools/proofcheck-runtime.json`. Without either configuration, this command uses local Docker and the already-installed `ubuntu:22.04` image. It does not choose a private SSH host.

The reports distinguish:

- `verified`: the target follows in the fresh Lean kernel, with any literature dependencies approved.
- `needs_literature_review`: the kernel checked the argument conditional on the listed published results, but at least one dependency lacks current approval.
- `rejected`: elaboration, export, exact target checking, or kernel checking failed.
- `unavailable`: the verification environment could not provide valid evidence.

To review a cited dependency, copy one complete `literature_dependencies` entry from the report into a review document:

```json
{
  "schema_version": 1,
  "reviewer": "Reviewer name",
  "status": "accepted",
  "rationale": "Source and model-alignment findings",
  "dependency": {},
  "checks": {
    "published_before_cutoff": true,
    "exact_statement": true,
    "model_alignment": true,
    "no_new_result_assumed": true
  }
}
```

The empty `dependency` above is a placeholder for the full report entry. After performing the checks, a maintainer records the decision and reruns verification:

```sh
python3 -m inclusion_bench review-literature reviewed-lemma.json
python3 -m inclusion_bench check-submission my-proof --runtime .tools/proofcheck-runtime.json
```

The append-only decisions are stored in `support/literature-reviews.json`. These are trusted maintainer records, like the existing proof and historical reviews. Keep them separate from model-controlled output. A verifier report still awards no points; proof admission, run provenance, and historical eligibility remain separate.

## Scope

This release improves the mathematical interface and reuse of established results. It does not make Lean accept informal arguments. A new algorithm still needs a precise correctness and complexity argument, but its standard computational and mathematical dependencies can be reused rather than rebuilt.

The current submission is one Lean source body under fixed trusted imports. New submitted structures and inductive declarations remain unsupported by the proof codec; use the imported library types and ordinary definitions and theorems. Only declarations needed by the requested targets are exported. This removes irrelevant elaborator-generated material while retaining every assumption used by the proof. Source and export limits remain 2 MiB and 32 MiB respectively.
