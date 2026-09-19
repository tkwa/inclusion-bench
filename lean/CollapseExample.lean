import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: e09e6cf8dfa1233f754dc4ecf935ea7db6831f24046cde0cbb1eebfedf4349c3
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
