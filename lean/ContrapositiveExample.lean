import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: 0aa915caa5b84a095278864dba0a1ab9ee4bdf54648e3b87e52a72208104dfbc
-- This theorem is conditional on its visible hypotheses.
-- It verifies inference, not the submitted result or the historical literature.
theorem ContrapositiveExample (model : Interpretation ClassId)
    (leaf0 : NonIncludes (model .PH) (model .Sigma2P))
    (citedRule0 : (Includes (model .NP) (model .Ppoly)) → (Includes (model .PH) (model .Sigma2P)))
    : NonIncludes (model .NP) (model .Ppoly) := by
  classical
  have step0 : NonIncludes (model .PH) (model .Sigma2P) := leaf0
  have step1 : NonIncludes (model .NP) (model .Ppoly) := by
    intro missingPremise
    exact step0 (citedRule0 missingPremise)
  exact step1

#print axioms ContrapositiveExample

end InclusionBench
