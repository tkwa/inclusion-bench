import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: 6cf78ea6cf5edd43e5c327a90ba54765871cfd552800637cbecfbc646eef7742
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
