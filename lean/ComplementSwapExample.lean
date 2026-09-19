import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: 0aa915caa5b84a095278864dba0a1ab9ee4bdf54648e3b87e52a72208104dfbc
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
