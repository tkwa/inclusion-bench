import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: 6cf78ea6cf5edd43e5c327a90ba54765871cfd552800637cbecfbc646eef7742
-- This theorem is conditional on its visible hypotheses.
-- It verifies inference, not the submitted result or the historical literature.
theorem ComplementSwapExample (model : Interpretation ClassId)
    (leaf0 : NonIncludes (model .NP) (model .coNP))
    (dual0 : model .coNP = coClass (model .NP))
    (dual1 : model .NP = coClass (model .coNP))
    : NonIncludes (model .coNP) (model .NP) := by
  classical
  have step0 : NonIncludes (model .NP) (model .coNP) := leaf0
  have step1 : NonIncludes (model .coNP) (model .NP) := nonincludes_cast (nonincludes_complement step0) dual0 dual1
  exact step1

#print axioms ComplementSwapExample

end InclusionBench
