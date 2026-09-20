import InclusionBench.Catalog
import InclusionBench.Circuits
import InclusionBench.Randomized
import InclusionBench.Counting
import InclusionBench.Oracles
import InclusionBench.ProofSystems
import InclusionBench.Transducers
import InclusionBench.UniformCircuits
import InclusionBench.LogCFL
import InclusionBench.Statistical
import InclusionBench.LogspaceClasses
import InclusionBench.CountingHierarchy
import InclusionBench.AlternatingLogtime

namespace InclusionBench

/-- Concrete definitions currently supplied. A missing entry is represented
by `none`, never by an opaque axiom or an unconstrained replacement predicate.
The completed entries use the exact machines/circuits in this repository;
equivalence with a chosen published convention is a further proof obligation. -/
def operationalDefinition : ClassId → Option ComplexityClass
  | .AC0 => some Circuits.nonuniformAC0
  | .ACC0 => some Circuits.nonuniformACC0
  | .TC0 => some Circuits.nonuniformTC0
  | .NC1 => some Circuits.nonuniformNC1
  | .UniformNC1 => some AlternatingLogtime.UniformNC1
  | .NC => some UniformCircuits.NC
  | .LogCFL => some LogCFL.contextFreeLogspace
  | .Ppoly => some Circuits.polynomialCircuits
  | .L => some Machines.logarithmicSpace
  | .NL => some Machines.nondeterministicLogarithmicSpace
  | .BPL => some LogspaceClasses.BPL
  | .UL => some LogspaceClasses.UL
  | .PL => some LogspaceClasses.PL
  | .SC => some Machines.simultaneousPolytimePolylogspace
  | .P => some Machines.polynomialTime
  | .RP => some Randomized.oneSidedPolynomialTime
  | .coRP => some Randomized.coOneSidedPolynomialTime
  | .ZPP => some Randomized.zeroErrorPolynomialTime
  | .BPP => some Randomized.boundedErrorPolynomialTime
  | .UP => some Counting.UP
  | .coUP => some Counting.coUP
  | .FewP => some Counting.FewP
  | .SPP => some Counting.SPP
  | .CeqP => some Counting.CeqP
  | .PP => some Counting.PP
  | .PSharpP => some CountingHierarchy.PSharpP
  | .CH => some CountingHierarchy.CH
  | .parityP => some Counting.parityP
  | .AWPP => some Counting.AWPP
  | .LWPP => some Transducers.LWPP
  | .WPP => some Transducers.WPP
  | .SBP => some Randomized.smallBoundedProbability
  | .SZK => some Statistical.SZK
  | .MA => some ProofSystems.MA
  | .coMA => some ProofSystems.coMA
  | .AM => some ProofSystems.AM
  | .coAM => some ProofSystems.coAM
  | .NPpoly => some ProofSystems.NPpoly
  | .Sigma2P => some Oracles.Sigma2P
  | .Pi2P => some Oracles.Pi2P
  | .Delta2P => some Oracles.Delta2P
  | .Theta2P => some Oracles.Theta2P
  | .PH => some Oracles.PH
  | .NP => some Machines.nondeterministicPolynomialTime
  | .coNP => some (coClass Machines.nondeterministicPolynomialTime)
  | .NPcapcoNP => some (intersectClass Machines.nondeterministicPolynomialTime
      (coClass Machines.nondeterministicPolynomialTime))
  | .PSPACE => some Machines.polynomialSpace
  | .E => some Machines.linearExponentialTime
  | .EXP => some Machines.exponentialTime
  | .EXPSPACE => some Machines.exponentialSpace
  | .NE => some Machines.nondeterministicLinearExponentialTime
  | .NEXP => some Machines.nondeterministicExponentialTime
  | _ => none

def classesWithOperationalDefinitions : List ClassId :=
  allClasses.filter (fun id => (operationalDefinition id).isSome)

theorem operational_definition_count : classesWithOperationalDefinitions.length = 52 := by decide

/-- A complete model must agree with every concrete definition already supplied.
This proposition is a compatibility requirement, not a supplied complete model. -/
def AgreesWithOperationalDefinitions (model : Interpretation ClassId) : Prop :=
  ∀ id definition, operationalDefinition id = some definition → model id = definition

end InclusionBench
