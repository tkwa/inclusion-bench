import InclusionQuantum.Normalization

/-!
# Stoquastic Merlin-Arthur verification

The verifier below has classical reversible NOT, CNOT, and Toffoli gates,
classical input, a quantum witness, zero ancillas and plus-state ancillas,
and a final X-basis measurement accepting the plus outcome. Its gate list is
the output of a concrete polynomial-time transducer. No arbitrary unitary,
sampler, or acceptance interpretation is supplied.

Completeness and soundness are rational functions of input length computed by
three total FP transducers, with an explicit inverse-polynomial gap. The
class is a union over these threshold choices. It does not assert amplification
or equivalence of every fixed parameter pair. In particular, the exact
soundness-1/2 boundary has an NP characterization (Liu, TQC 2021, Corollary 24).

This is the total-language restriction of the verifier model in Aharonov,
Grilo and Liu, Definition 2.3 and Remarks 2.4–2.5:
https://arxiv.org/abs/2010.02835v4 . Model equivalence and the literature
containments are separate trusted bridges, not axioms in this module.
-/

namespace InclusionBench.Quantum

open scoped BigOperators
open Counting (polynomialValue)

noncomputable section

inductive ReversibleGate (qubits : Nat) where
  | not (target : Fin qubits)
  | cnot (control target : Fin qubits) (distinct : control ≠ target)
  | toffoli (first second target : Fin qubits)
      (controls_distinct : first ≠ second)
      (first_distinct : first ≠ target) (second_distinct : second ≠ target)

def toffoliBasis {qubits : Nat} (first second target : Fin qubits)
    (basis : Basis qubits) : Basis qubits :=
  if basis first && basis second then flipped basis target else basis

def ReversibleGate.apply {qubits : Nat} (gate : ReversibleGate qubits)
    (state : State qubits) : State qubits :=
  fun basis => match gate with
    | .not target => state (flipped basis target)
    | .cnot control target _ => state (if basis control then flipped basis target else basis)
    | .toffoli first second target _ _ _ => state (toffoliBasis first second target basis)

theorem toffoliBasis_twice {qubits : Nat} (first second target : Fin qubits)
    (first_distinct : first ≠ target) (second_distinct : second ≠ target) :
    Function.Involutive (toffoliBasis first second target) := by
  intro basis
  cases h₁ : basis first <;> cases h₂ : basis second <;>
    simp [toffoliBasis, flipped, first_distinct, second_distinct, h₁, h₂]

theorem reversibleGate_preserves_normSquared {qubits : Nat}
    (gate : ReversibleGate qubits) (state : State qubits) :
    normSquared (gate.apply state) = normSquared state := by
  cases gate with
  | not target => exact pauliX_preserves_normSquared target state
  | cnot control target distinct => exact cnot_preserves_normSquared control target distinct state
  | toffoli first second target _ first_distinct second_distinct =>
    exact normSquared_reindex state _
      (toffoliBasis_twice first second target first_distinct second_distinct).bijective

structure StoquasticCircuit (qubits : Nat) where
  gates : List (ReversibleGate qubits)
  output : Fin qubits

def StoquasticCircuit.run {qubits : Nat} (circuit : StoquasticCircuit qubits)
    (initial : State qubits) : State qubits :=
  circuit.gates.foldl (fun state gate => gate.apply state) initial

def reversibleGateFields {qubits : Nat} : ReversibleGate qubits → List Nat
  | .not target => [0, target.val, 0, 0]
  | .cnot control target _ => [1, control.val, target.val, 0]
  | .toffoli first second target _ _ _ => [2, first.val, second.val, target.val]

def StoquasticCircuit.serialize {qubits : Nat} (circuit : StoquasticCircuit qubits) : Word :=
  UniformCircuits.encodeNaturals
    (qubits :: circuit.output.val :: circuit.gates.length ::
      circuit.gates.flatMap reversibleGateFields)

theorem reversibleGateFields_injective {qubits : Nat} :
    Function.Injective (@reversibleGateFields qubits) := by
  intro left right same
  cases left <;> cases right <;> simp_all [reversibleGateFields, Fin.ext_iff]

theorem stoquasticCircuit_preserves_normSquared {qubits : Nat}
    (circuit : StoquasticCircuit qubits) (state : State qubits) :
    normSquared (circuit.run state) = normSquared state := by
  have h : ∀ (gates : List (ReversibleGate qubits)) (input : State qubits),
      normSquared (gates.foldl (fun current gate => gate.apply current) input) =
        normSquared input := by
    intro gates
    induction gates with
    | nil => intro input; rfl
    | cons gate gates ih =>
      intro input
      simpa only [List.foldl_cons, reversibleGate_preserves_normSquared]
        using ih (gate.apply input)
  exact h circuit.gates state

/-- Measure X and accept +1: a Hadamard followed by measurement of zero. -/
def plusAcceptance {qubits : Nat} (output : Fin qubits) (state : State qubits) : ℝ :=
  ∑ basis, if basis output then 0
    else Complex.normSq ((Gate.hadamard output).apply state basis)

theorem plusAcceptance_nonnegative {qubits : Nat} (output : Fin qubits)
    (state : State qubits) : 0 ≤ plusAcceptance output state := by
  classical
  apply Finset.sum_nonneg
  intro basis _
  split_ifs
  · exact le_rfl
  · exact Complex.normSq_nonneg _

theorem plusAcceptance_le_normSquared {qubits : Nat} (output : Fin qubits)
    (state : State qubits) : plusAcceptance output state ≤ normSquared state := by
  classical
  calc
    plusAcceptance output state ≤ normSquared ((Gate.hadamard output).apply state) := by
      apply Finset.sum_le_sum
      intro basis _
      split_ifs
      · exact Complex.normSq_nonneg _
      · exact le_rfl
    _ = normSquared state := hadamard_preserves_normSquared output state

def plusPreparation (input witness plus zeroAncillas : Nat) :
    List (Gate (input + witness + (plus + zeroAncillas) + 1)) :=
  List.ofFn fun index : Fin plus =>
    Gate.hadamard (ancillaWire input witness (plus + zeroAncillas) ⟨index.val, by omega⟩)

def stoquasticInitialState (input : Word) (witness plus zeroAncillas : Nat)
    (output : Fin (input.length + witness + (plus + zeroAncillas) + 1))
    (proof : State witness) : State (input.length + witness + (plus + zeroAncillas) + 1) :=
  (Circuit.mk (plusPreparation input.length witness plus zeroAncillas) output).run
    (initialState input witness (plus + zeroAncillas) proof)

theorem stoquasticInitialState_preserves_normSquared (input : Word)
    (witness plus zeroAncillas : Nat)
    (output : Fin (input.length + witness + (plus + zeroAncillas) + 1)) (proof : State witness) :
    normSquared (stoquasticInitialState input witness plus zeroAncillas output proof) =
      normSquared proof := by
  rw [stoquasticInitialState, circuit_preserves_normSquared, initialState_preserves_normSquared]

abbrev StoquasticFamily (witnessLength plusLength zeroLength : List Nat) :=
  (n : Nat) → StoquasticCircuit
    (n + polynomialValue witnessLength n +
      (polynomialValue plusLength n + polynomialValue zeroLength n) + 1)

def stoquasticUniform {width : Nat → Nat}
    (family : (n : Nat) → StoquasticCircuit (width n)) : Prop :=
  ∃ generator : Transducers.Transducer, ∃ runtime : List Nat,
    (∀ word, generator.haltsAt word (polynomialValue runtime word.length)) ∧
    ∀ n, generator.output (Transducers.unary n) (polynomialValue runtime n) =
      (family n).serialize

def stoquasticAcceptance {witnessLength plusLength zeroLength : List Nat}
    (family : StoquasticFamily witnessLength plusLength zeroLength) (input : Word)
    (proof : State (polynomialValue witnessLength input.length)) : ℝ :=
  plusAcceptance (family input.length).output
    ((family input.length).run
      (stoquasticInitialState input (polynomialValue witnessLength input.length)
        (polynomialValue plusLength input.length) (polynomialValue zeroLength input.length)
        (family input.length).output proof))

/-- All threshold integers are computed by total polynomial-time machines.
The common positive denominator avoids a convention about rational rounding.
The last inequality is the inverse-polynomial gap, cross-multiplied exactly. -/
structure StoquasticThresholds where
  completenessNumerator : Word → Int
  soundnessNumerator : Word → Int
  denominator : Word → Int
  completenessComputable : Transducers.FP completenessNumerator
  soundnessComputable : Transducers.FP soundnessNumerator
  denominatorComputable : Transducers.FP denominator
  gapPolynomial : List Nat
  valid : ∀ n,
    let word := Transducers.unary n
    0 < denominator word ∧
    denominator word ≤ 2 * soundnessNumerator word ∧
    soundnessNumerator word < completenessNumerator word ∧
    completenessNumerator word ≤ denominator word ∧
    denominator word ≤ (polynomialValue gapPolynomial n : Int) *
      (completenessNumerator word - soundnessNumerator word)

def StoquasticThresholds.completeness (parameters : StoquasticThresholds) (n : Nat) : ℝ :=
  (parameters.completenessNumerator (Transducers.unary n) : ℝ) /
    (parameters.denominator (Transducers.unary n) : ℝ)

def StoquasticThresholds.soundness (parameters : StoquasticThresholds) (n : Nat) : ℝ :=
  (parameters.soundnessNumerator (Transducers.unary n) : ℝ) /
    (parameters.denominator (Transducers.unary n) : ℝ)

def StoqMA : ComplexityClass :=
  fun L => ∃ witnessLength plusLength zeroLength : List Nat,
    ∃ family : StoquasticFamily witnessLength plusLength zeroLength,
    ∃ parameters : StoquasticThresholds,
    stoquasticUniform family ∧ ∀ input,
      (L input → ∃ proof : State (polynomialValue witnessLength input.length),
        Normalized proof ∧ parameters.completeness input.length ≤
          stoquasticAcceptance family input proof) ∧
      (¬ L input → ∀ proof : State (polynomialValue witnessLength input.length),
        Normalized proof → stoquasticAcceptance family input proof ≤
          parameters.soundness input.length)

theorem stoquasticAcceptance_bounded {witnessLength plusLength zeroLength : List Nat}
    (family : StoquasticFamily witnessLength plusLength zeroLength) (input : Word)
    (proof : State (polynomialValue witnessLength input.length))
    (normalized : Normalized proof) :
    0 ≤ stoquasticAcceptance family input proof ∧
      stoquasticAcceptance family input proof ≤ 1 := by
  refine ⟨plusAcceptance_nonnegative _ _, ?_⟩
  calc
    stoquasticAcceptance family input proof ≤
        normSquared ((family input.length).run
          (stoquasticInitialState input _ _ _ (family input.length).output proof)) :=
      plusAcceptance_le_normSquared _ _
    _ = normSquared proof := by
      rw [stoquasticCircuit_preserves_normSquared, stoquasticInitialState_preserves_normSquared]
    _ = 1 := normalized

end
end InclusionBench.Quantum
