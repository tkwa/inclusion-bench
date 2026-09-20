import InclusionQuantum.Quantum
import InclusionQuantum.Unentangled
import InclusionQuantum.Logspace
import InclusionQuantum.Stoquastic
import InclusionQuantum.Statistical
import InclusionQuantum.RealFeasibility

namespace InclusionBench.Quantum

/-- Every catalog name has a concrete operational definition. No default class
or opaque replacement is used for any catalog entry. -/
noncomputable def completeInterpretation : Interpretation ClassId
  | .AC0 => Circuits.nonuniformAC0
  | .ACC0 => Circuits.nonuniformACC0
  | .TC0 => Circuits.nonuniformTC0
  | .NC1 => Circuits.nonuniformNC1
  | .NC => UniformCircuits.NC
  | .LogCFL => LogCFL.contextFreeLogspace
  | .Ppoly => Circuits.polynomialCircuits
  | .L => Machines.logarithmicSpace
  | .NL => Machines.nondeterministicLogarithmicSpace
  | .SC => Machines.simultaneousPolytimePolylogspace
  | .P => Machines.polynomialTime
  | .RP => Randomized.oneSidedPolynomialTime
  | .coRP => Randomized.coOneSidedPolynomialTime
  | .ZPP => Randomized.zeroErrorPolynomialTime
  | .BPP => Randomized.boundedErrorPolynomialTime
  | .UP => Counting.UP
  | .coUP => Counting.coUP
  | .FewP => Counting.FewP
  | .SPP => Counting.SPP
  | .CeqP => Counting.CeqP
  | .PP => Counting.PP
  | .parityP => Counting.parityP
  | .AWPP => Counting.AWPP
  | .LWPP => Transducers.LWPP
  | .WPP => Transducers.WPP
  | .SBP => Randomized.smallBoundedProbability
  | .SZK => Statistical.SZK
  | .MA => ProofSystems.MA
  | .coMA => ProofSystems.coMA
  | .AM => ProofSystems.AM
  | .coAM => ProofSystems.coAM
  | .NPpoly => ProofSystems.NPpoly
  | .Sigma2P => Oracles.Sigma2P
  | .Pi2P => Oracles.Pi2P
  | .Delta2P => Oracles.Delta2P
  | .Theta2P => Oracles.Theta2P
  | .PH => Oracles.PH
  | .NP => Machines.nondeterministicPolynomialTime
  | .coNP => (coClass Machines.nondeterministicPolynomialTime)
  | .NPcapcoNP => (intersectClass Machines.nondeterministicPolynomialTime
      (coClass Machines.nondeterministicPolynomialTime))
  | .PSPACE => Machines.polynomialSpace
  | .E => Machines.linearExponentialTime
  | .EXP => Machines.exponentialTime
  | .EXPSPACE => Machines.exponentialSpace
  | .NE => Machines.nondeterministicLinearExponentialTime
  | .NEXP => Machines.nondeterministicExponentialTime
  | .BQP => BQP
  | .QCMA => QCMA
  | .QMA => QMA
  | .coQMA => coQMA
  | .BPL => LogspaceClasses.BPL
  | .UL => LogspaceClasses.UL
  | .PL => LogspaceClasses.PL
  | .BQL => BQL
  | .ExistsR => RealFeasibility.ExistsR
  | .PSharpP => CountingHierarchy.PSharpP
  | .CH => CountingHierarchy.CH
  | .QMA2 => QMA2
  | .StoqMA => StoqMA
  | .QSZK => QSZK
  | .UniformNC1 => AlternatingLogtime.UniformNC1


theorem complete_agrees_with_core : AgreesWithOperationalDefinitions completeInterpretation := by
  intro id definition known
  cases id <;> simp_all [operationalDefinition, completeInterpretation]

noncomputable def completeOperationalDefinition (id : ClassId) : Option ComplexityClass :=
  some (completeInterpretation id)

theorem every_class_defined (id : ClassId) :
    ∃ definition, completeOperationalDefinition id = some definition :=
  ⟨completeInterpretation id, rfl⟩

theorem all_catalog_classes_defined :
    allClasses.filter (fun id => (completeOperationalDefinition id).isSome) = allClasses := by
  simp [completeOperationalDefinition]

end InclusionBench.Quantum
