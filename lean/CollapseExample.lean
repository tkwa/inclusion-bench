import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: ad63448e6e4679f4640d5f3d9b96e6330d5cca7d5354a2ac1b41f40665ba75dc
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
