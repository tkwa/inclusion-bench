# How the provisional roster will be selected

The roster should expose important research questions across complexity theory. It is not a forecast of which problems will be solved soon. Neither anticipated mathematical tractability nor ease of writing a Lean definition is a selection criterion.

## Evidence and judgment

Begin with named open questions and research programs, then ask which exact class endpoints represent them. A class earns a strong case when it adds an established question that the other selected endpoints do not capture. Evidence should come from primary research, author surveys, expert problem collections and conference or program descriptions available by the benchmark cutoff. Post-cutoff breakthroughs must not make a class more attractive because an answer has become easy to retrieve.

The [CCC 2026 call for papers](https://computationalcomplexity.org/Archive/2026/cfp.html) spans much more than decision classes: circuits, algebraic and proof complexity, randomness, average-case and quantum complexity, and several other models. It is a breadth check, not a prescription for equal quotas. The [Simons lower-bounds program](https://simons.berkeley.edu/programs/lower-bounds-computational-complexity) likewise connects Boolean, algebraic and interactive models. These sources support considering several kinds of computational problem; they do not establish a numerical distribution of scientific importance.

Use three kinds of evidence separately:

1. **Established importance:** the question is a central problem in an author survey or expert open-problem collection, or organizes a sustained primary research program.
2. **Distinct coverage:** the candidate represents a question not already captured by another scored pair. A complementary spelling or an equivalent model needs a separate reason to receive another scored slot.
3. **Faithful meaning:** the actual target matches the literature's universe, promise convention, uniformity, gate model and parameters. A nearby total-language statement must not be advertised as the canonical promise separation without a justified implication.

Family balance is a judgment constrained by these questions. It need not assign the same number of classes to every family, and the families overlap. Count slots, unresolved endpoints and distinct unresolved pairs touching each family; report all three rather than choose the number that makes a proposal look balanced. Do not maximize the number of unknown pairs: obscure cross-comparisons can inflate it without adding a central question.

## Comparisons to retain in the review

For each proposed addition or demotion, give its strongest scientific reason, the important question gained or lost, the counterargument, precise representation caveats and the sources. Compare at least a conservative roster and a broader problem-driven roster. Check whether the recommendation survives reasonable changes in emphasis among circuits, structural complexity, randomness, quantum, counting, space and other represented models. Any illustrative importance weights must be labeled editorial sensitivity assumptions, not measurements or probabilities.

Separate scored endpoints from useful inference vocabulary if needed. A demoted class can remain an explicitly unscored background node, preserving cited facts, Lean definitions and implication paths. A class with no unresolved incident pairs can be useful background without occupying an open-problem slot. A class with few open pairs can still be scientifically essential; low degree alone is not a demotion argument.

There is no claim to cover every important advance. [The 2023 Simons meta-complexity problem collection](https://wiki.simons.berkeley.edu/doku.php?id=mc23:list-of-open-problems) includes hardness, witnessing and quantitative questions that do not simply assert inclusions between familiar classes. Record such coverage limits rather than rename them into artificial classes to manufacture points.

## Audit and publication

The mathematical cutoff remains September 1, 2026. The roster decision and all changed class conventions precede the new classification audit. Reuse prior evidence only where the exact mathematical statement and historical scope remain unchanged. New definitions, new endpoints and new implication rules require their own review. The original v0.3.1 release remains available, and the provisional v0.4.0 PR must make the score-comparison and migration consequences explicit.

This is an AI-assisted proposal for human review. Independent agent agreement is useful error checking, not a human expert endorsement or an empirical calibration of importance.
