import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: ad63448e6e4679f4640d5f3d9b96e6330d5cca7d5354a2ac1b41f40665ba75dc
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
