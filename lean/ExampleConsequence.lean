import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: e09e6cf8dfa1233f754dc4ecf935ea7db6831f24046cde0cbb1eebfedf4349c3
-- This theorem is conditional on its visible hypotheses.
-- It verifies inference, not the submitted result or the historical literature.
theorem ExampleConsequence (model : Interpretation ClassId)
    (leaf0 : NonIncludes (model .NP) (model .BPP))
    (leaf1 : Includes (model .NP) (model .Theta2P))
    (leaf2 : Includes (model .Theta2P) (model .PP))
    (leaf3 : Includes (model .PP) (model .PSPACE))
    (leaf4 : Includes (model .P) (model .ZPP))
    (leaf5 : Includes (model .ZPP) (model .RP))
    (leaf6 : Includes (model .RP) (model .BPP))
    : NonIncludes (model .PSPACE) (model .P) := by
  classical
  have step0 : NonIncludes (model .NP) (model .BPP) := leaf0
  have step1 : Includes (model .NP) (model .Theta2P) := leaf1
  have step2 : Includes (model .Theta2P) (model .PP) := leaf2
  have step3 : Includes (model .NP) (model .PP) := includes_trans step1 step2
  have step4 : Includes (model .PP) (model .PSPACE) := leaf3
  have step5 : Includes (model .NP) (model .PSPACE) := includes_trans step3 step4
  have step6 : NonIncludes (model .PSPACE) (model .BPP) := nonincludes_expand step0 step5 (includes_refl _)
  have step7 : Includes (model .P) (model .ZPP) := leaf4
  have step8 : Includes (model .ZPP) (model .RP) := leaf5
  have step9 : Includes (model .P) (model .RP) := includes_trans step7 step8
  have step10 : Includes (model .RP) (model .BPP) := leaf6
  have step11 : Includes (model .P) (model .BPP) := includes_trans step9 step10
  have step12 : NonIncludes (model .PSPACE) (model .P) := nonincludes_expand step6 (includes_refl _) step11
  exact step12

#print axioms ExampleConsequence

end InclusionBench
