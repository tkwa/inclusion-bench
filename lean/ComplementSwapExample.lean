import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: e929704944eba030d541cf2a12a6aa012cb7a0f10c003ca308a1dda65cd85ef5
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
