import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: e09e6cf8dfa1233f754dc4ecf935ea7db6831f24046cde0cbb1eebfedf4349c3
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
