import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: 0aa915caa5b84a095278864dba0a1ab9ee4bdf54648e3b87e52a72208104dfbc
-- This theorem is conditional on its visible hypotheses.
-- It verifies inference, not the submitted result or the historical literature.
theorem ComplementExample (model : Interpretation ClassId)
    (leaf0 : Includes (model .P) (model .UP))
    (dual0 : model .P = coClass (model .P))
    (dual1 : model .coUP = coClass (model .UP))
    : Includes (model .P) (model .coUP) := by
  classical
  have step0 : Includes (model .P) (model .UP) := leaf0
  have step1 : Includes (model .P) (model .coUP) := includes_cast (includes_complement step0) dual0 dual1
  exact step1

#print axioms ComplementExample

end InclusionBench
