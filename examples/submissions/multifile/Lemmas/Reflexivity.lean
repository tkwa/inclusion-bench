import TrustedBaseline

open InclusionBench

theorem Submission.Lemmas.identity_inclusion (family : ComplexityClass) :
    Includes family family :=
  includes_refl family
