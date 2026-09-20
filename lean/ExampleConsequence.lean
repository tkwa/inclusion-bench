import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: e929704944eba030d541cf2a12a6aa012cb7a0f10c003ca308a1dda65cd85ef5
-- This theorem is conditional on its visible hypotheses.
-- It verifies inference, not the submitted result or the historical literature.
theorem ExampleConsequence (model : Interpretation ClassId)
    (leaf0 : NonIncludes (model .NP) (model .BPP))
    (leaf1 : Includes (model .NP) (model .ExistsR))
    (leaf2 : Includes (model .ExistsR) (model .PSPACE))
    (leaf3 : Includes (model .P) (model .ZPP))
    (leaf4 : Includes (model .ZPP) (model .RP))
    (leaf5 : Includes (model .RP) (model .BPP))
    : NonIncludes (model .PSPACE) (model .P) := by
  classical
  have step0 : NonIncludes (model .NP) (model .BPP) := leaf0
  have step1 : Includes (model .NP) (model .ExistsR) := leaf1
  have step2 : Includes (model .ExistsR) (model .PSPACE) := leaf2
  have step3 : Includes (model .NP) (model .PSPACE) := includes_trans step1 step2
  have step4 : NonIncludes (model .PSPACE) (model .BPP) := nonincludes_expand step0 step3 (includes_refl _)
  have step5 : Includes (model .P) (model .ZPP) := leaf3
  have step6 : Includes (model .ZPP) (model .RP) := leaf4
  have step7 : Includes (model .P) (model .RP) := includes_trans step5 step6
  have step8 : Includes (model .RP) (model .BPP) := leaf5
  have step9 : Includes (model .P) (model .BPP) := includes_trans step7 step8
  have step10 : NonIncludes (model .PSPACE) (model .P) := nonincludes_expand step4 (includes_refl _) step9
  exact step10

#print axioms ExampleConsequence

end InclusionBench
