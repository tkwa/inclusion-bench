import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: 8f69436c927248a9b7615fa97543f83764fef4afdc7b6a61b2ae9de1b4665d1d
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
