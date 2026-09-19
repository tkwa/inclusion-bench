import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: 0aa915caa5b84a095278864dba0a1ab9ee4bdf54648e3b87e52a72208104dfbc
-- This theorem is conditional on its visible hypotheses.
-- It verifies inference, not the submitted result or the historical literature.
theorem CollapseExample (model : Interpretation ClassId)
    (leaf0 : Includes (model .NP) (model .P))
    (citedRule0 : (Includes (model .NP) (model .P)) → (Includes (model .PH) (model .P)))
    : Includes (model .PH) (model .P) := by
  classical
  have step0 : Includes (model .NP) (model .P) := leaf0
  have step1 : Includes (model .PH) (model .P) := citedRule0 step0
  exact step1

#print axioms CollapseExample

end InclusionBench
