import InclusionBench.Catalog

namespace InclusionBench

-- Dataset SHA-256: ad63448e6e4679f4640d5f3d9b96e6330d5cca7d5354a2ac1b41f40665ba75dc
-- This theorem is conditional on its visible hypotheses.
-- It verifies inference, not the submitted result or the historical literature.
theorem ExampleConsequence (model : Interpretation ClassId)
    (leaf0 : NonIncludes (model .NP) (model .BPP))
    (leaf1 : Includes (model .coNP) (model .CeqP))
    (leaf2 : Includes (model .CeqP) (model .PP))
    (dual0 : model .NP = coClass (model .coNP))
    (dual1 : model .PP = coClass (model .PP))
    (leaf3 : Includes (model .PP) (model .PSPACE))
    (leaf4 : Includes (model .P) (model .ZPP))
    (leaf5 : Includes (model .ZPP) (model .RP))
    (leaf6 : Includes (model .RP) (model .BPP))
    : NonIncludes (model .PSPACE) (model .P) := by
  classical
  have step0 : NonIncludes (model .NP) (model .BPP) := leaf0
  have step1 : Includes (model .coNP) (model .CeqP) := leaf1
  have step2 : Includes (model .CeqP) (model .PP) := leaf2
  have step3 : Includes (model .coNP) (model .PP) := includes_trans step1 step2
  have step4 : Includes (model .NP) (model .PP) := includes_cast (includes_complement step3) dual0 dual1
  have step5 : Includes (model .PP) (model .PSPACE) := leaf3
  have step6 : Includes (model .NP) (model .PSPACE) := includes_trans step4 step5
  have step7 : NonIncludes (model .PSPACE) (model .BPP) := nonincludes_expand step0 step6 (includes_refl _)
  have step8 : Includes (model .P) (model .ZPP) := leaf4
  have step9 : Includes (model .ZPP) (model .RP) := leaf5
  have step10 : Includes (model .P) (model .RP) := includes_trans step8 step9
  have step11 : Includes (model .RP) (model .BPP) := leaf6
  have step12 : Includes (model .P) (model .BPP) := includes_trans step10 step11
  have step13 : NonIncludes (model .PSPACE) (model .P) := nonincludes_expand step7 (includes_refl _) step12
  exact step13

#print axioms ExampleConsequence

end InclusionBench
