import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: ad63448e6e4679f4640d5f3d9b96e6330d5cca7d5354a2ac1b41f40665ba75dc
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
