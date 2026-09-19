import InclusionBench.Certificate
import InclusionBench.Scoring

namespace InclusionBench

/-- Catalog names, not assertions that the named semantic definitions have
been formalized. `Interpretation ClassId` remains an explicit argument. -/
inductive ClassId where
  | AC0 | ACC0 | TC0 | NC1 | L | NL | LogCFL | NC | SC | P
  | RP | coRP | ZPP | BPP | UP | coUP | NP | coNP | FewP | SPP
  | CeqP | PP | parityP | AWPP | LWPP | WPP | MA | coMA | AM | coAM
  | QCMA | QMA | coQMA | BQP | SBP | SZK | NPcapcoNP | Sigma2P | Pi2P | Delta2P
  | Theta2P | PH | Ppoly | NPpoly | PSPACE | EXP | NEXP | EXPSPACE | E | NE
  deriving DecidableEq, BEq, Repr, Lean.ToJson, Lean.FromJson

def allClasses : List ClassId :=
  [.AC0, .ACC0, .TC0, .NC1, .L, .NL, .LogCFL, .NC, .SC, .P,
   .RP, .coRP, .ZPP, .BPP, .UP, .coUP, .NP, .coNP, .FewP, .SPP,
   .CeqP, .PP, .parityP, .AWPP, .LWPP, .WPP, .MA, .coMA, .AM, .coAM,
   .QCMA, .QMA, .coQMA, .BQP, .SBP, .SZK, .NPcapcoNP, .Sigma2P, .Pi2P, .Delta2P,
   .Theta2P, .PH, .Ppoly, .NPpoly, .PSPACE, .EXP, .NEXP, .EXPSPACE, .E, .NE]

theorem roster_size : allClasses.length = 50 := rfl

theorem roster_no_duplicates : allClasses.eraseDups = allClasses := by decide

def allOrderedPairs : List (OrderedPair ClassId) :=
  allClasses.flatMap (fun left => allClasses.map (fun right => (left, right)))

theorem full_matrix_size : allOrderedPairs.length = 2500 := by
  simp only [allOrderedPairs, List.length_flatMap, List.length_map, roster_size]
  rfl

theorem full_matrix_score_bound (isResolved : OrderedPair ClassId → Bool) :
    score allOrderedPairs isResolved ≤ 2500 := by
  have bound := score_bound_by_input_length allOrderedPairs isResolved
  simpa only [full_matrix_size] using bound

end InclusionBench
