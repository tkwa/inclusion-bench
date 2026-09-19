import InclusionBench

namespace InclusionBench.Examples

private def baseline : List (Fact ClassId) := [.inclusion .P .NP, .inclusion .NP .PSPACE]
private def rule : Rule ClassId := transitivityRule .P .NP .PSPACE
private def proof : List (CertificateStep ClassId) :=
  [.baseline (.inclusion .P .NP), .baseline (.inclusion .NP .PSPACE), .applyRule rule]

/-- The checker accepts a correctly ordered transitivity certificate. -/
example : checkCertificate baseline [] [rule] proof [] =
    some [.inclusion .P .PSPACE, .inclusion .NP .PSPACE, .inclusion .P .NP] := by decide

/-- A claimed leaf absent from the pinned baseline is rejected. -/
example : checkCertificate baseline [] [rule]
    [.baseline (.inclusion .NP .P)] [] = none := by decide

/-- A rule cannot be used before its premises have been checked. -/
example : checkCertificate baseline [] [rule] [.applyRule rule] [] = none := by decide

/-- Repeating an eligible ordered pair cannot manufacture a second point. -/
example : score (C := ClassId) [(.P, .NP), (.P, .NP)] (fun _ => true) = 1 := by decide

/-- The reversed ordered pair is a distinct question. -/
example : score (C := ClassId) [(.P, .NP), (.NP, .P)] (fun _ => true) = 2 := by decide

/-- Extra evidence categories resolve the same single bit. -/
example : score (C := ClassId) [(.P, .NP)]
    (resolved (fun _ => true) (fun _ => false) (fun _ => false)) =
    score (C := ClassId) [(.P, .NP)]
    (resolved (fun _ => true) (fun _ => true) (fun _ => true)) := by decide

end InclusionBench.Examples
