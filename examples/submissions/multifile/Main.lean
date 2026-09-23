import Lemmas.Reflexivity

open InclusionBench InclusionBench.Support.Classes

-- An infrastructure example of module reuse; this known claim earns no points.
theorem Submission.result_1 : Includes P P :=
  Submission.Lemmas.identity_inclusion P
