import Mathlib.Data.Complex.Basic
import Mathlib.Data.Real.Sqrt
import Mathlib.Data.Fintype.Pi
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import InclusionBench

/-!
# Concrete quantum circuit definitions

Amplitudes are complex numbers indexed by finite computational basis strings.
The only available gates are H, T, X, and CNOT with distinct control and
target. Their actions are explicit formulas; there is no arbitrary matrix or
acceptance predicate. A finite-control polynomial-time transducer generates
the complete serialized circuit on unary input length.

The definitions below use pure normalized quantum witnesses, classical input
bits, zero ancillary bits, and one measured output wire. Normalization.lean
proves gate/circuit norm preservation, register-embedding norm preservation,
and acceptance bounds for these exact definitions. Amplification, general
unitarity statements, and equivalence to textbook models remain separate
proof obligations. No such claim is assumed here.
-/

namespace InclusionBench.Quantum

open scoped BigOperators
open Counting (polynomialValue)

abbrev Basis (qubits : Nat) := Fin qubits → Bool
abbrev State (qubits : Nat) := Basis qubits → ℂ

noncomputable section

def normSquared {qubits : Nat} (state : State qubits) : ℝ :=
  ∑ basis, Complex.normSq (state basis)

def Normalized {qubits : Nat} (state : State qubits) : Prop := normSquared state = 1

def basisState {qubits : Nat} (bits : Basis qubits) : State qubits := by
  classical
  exact fun basis => if basis = bits then 1 else 0

inductive Gate (qubits : Nat) where
  | hadamard (target : Fin qubits)
  | phaseT (target : Fin qubits)
  | pauliX (target : Fin qubits)
  | cnot (control target : Fin qubits) (distinct : control ≠ target)

def flipped {qubits : Nat} (basis : Basis qubits) (target : Fin qubits) : Basis qubits :=
  Function.update basis target (!(basis target))

/-- T has phase exp(i*pi/4), written algebraically without an angle oracle. -/
def tPhase : ℂ := (1 + Complex.I) / (Real.sqrt 2 : ℂ)

def Gate.apply {qubits : Nat} (gate : Gate qubits) (state : State qubits) : State qubits :=
  fun basis => match gate with
    | .hadamard target =>
        (state (Function.update basis target false) +
          if basis target then -state (Function.update basis target true)
          else state (Function.update basis target true)) / (Real.sqrt 2 : ℂ)
    | .phaseT target => if basis target then tPhase * state basis else state basis
    | .pauliX target => state (flipped basis target)
    | .cnot control target _ => state (if basis control then flipped basis target else basis)

structure Circuit (qubits : Nat) where
  gates : List (Gate qubits)
  output : Fin qubits

def Circuit.run {qubits : Nat} (circuit : Circuit qubits) (initial : State qubits) : State qubits :=
  circuit.gates.foldl (fun state gate => gate.apply state) initial

def Circuit.acceptanceProbability {qubits : Nat} (circuit : Circuit qubits)
    (initial : State qubits) : ℝ :=
  ∑ basis, if basis circuit.output then Complex.normSq (circuit.run initial basis) else 0

/-- Every gate record has exactly three natural-number fields. The tag
distinguishes constructors; single-wire gates use zero in the final field. -/
def gateFields {qubits : Nat} : Gate qubits → List Nat
  | .hadamard target => [0, target.val, 0]
  | .phaseT target => [1, target.val, 0]
  | .pauliX target => [2, target.val, 0]
  | .cnot control target _ => [3, control.val, target.val]

def Circuit.serialize {qubits : Nat} (circuit : Circuit qubits) : Word :=
  UniformCircuits.encodeNaturals
    (qubits :: circuit.output.val :: circuit.gates.length :: circuit.gates.flatMap gateFields)

theorem gateFields_injective {qubits : Nat} : Function.Injective (@gateFields qubits) := by
  intro left right same
  cases left <;> cases right <;> simp_all [gateFields, Fin.ext_iff]

theorem basisState_normalized {qubits : Nat} (bits : Basis qubits) :
    Normalized (basisState bits) := by
  classical
  simp [Normalized, normSquared, basisState]

theorem flipped_twice {qubits : Nat} (bits : Basis qubits) (target : Fin qubits) :
    flipped (flipped bits target) target = bits := by
  funext index
  by_cases same : index = target
  · subst index
    simp [flipped]
  · simp [flipped, same]

theorem pauliX_twice {qubits : Nat} (target : Fin qubits) (state : State qubits) :
    (Gate.pauliX target).apply ((Gate.pauliX target).apply state) = state := by
  funext basis
  simp [Gate.apply, flipped_twice]

/-- The generator is total and polynomial-time on all binary inputs. Its
output on unary n is exactly the complete circuit, including all wire indices. -/
def polynomialUniform {width : Nat → Nat} (family : (n : Nat) → Circuit (width n)) : Prop :=
  ∃ generator : Transducers.Transducer, ∃ runtime : List Nat,
    (∀ word, generator.haltsAt word (polynomialValue runtime word.length)) ∧
    ∀ n, generator.output (Transducers.unary n) (polynomialValue runtime n) =
      (family n).serialize

def inputWire (n witness ancilla : Nat) (index : Fin n) : Fin (n + witness + ancilla + 1) :=
  ⟨index.val, by omega⟩

def witnessWire (n witness ancilla : Nat) (index : Fin witness) : Fin (n + witness + ancilla + 1) :=
  ⟨n + index.val, by omega⟩

def ancillaWire (n witness ancilla : Nat) (index : Fin (ancilla + 1)) :
    Fin (n + witness + ancilla + 1) :=
  ⟨n + witness + index.val, by omega⟩

/-- Registers are ordered as input, witness, and zero ancillas. An extra
ancilla ensures that even the empty input has a possible output wire. -/
def initialState (input : Word) (witness ancilla : Nat) (proof : State witness) :
    State (input.length + witness + ancilla + 1) := by
  classical
  exact fun basis =>
    if (∀ index : Fin input.length,
        basis (inputWire input.length witness ancilla index) = input.get index) ∧
      (∀ index : Fin (ancilla + 1),
        basis (ancillaWire input.length witness ancilla index) = false)
    then proof (fun index => basis (witnessWire input.length witness ancilla index))
    else 0

abbrev Family (witnessLength ancillaLength : List Nat) :=
  (n : Nat) → Circuit (n + polynomialValue witnessLength n + polynomialValue ancillaLength n + 1)

def acceptance {witnessLength ancillaLength : List Nat}
    (family : Family witnessLength ancillaLength) (input : Word)
    (proof : State (polynomialValue witnessLength input.length)) : ℝ :=
  (family input.length).acceptanceProbability
    (initialState input (polynomialValue witnessLength input.length)
      (polynomialValue ancillaLength input.length) proof)

def BQP : ComplexityClass :=
  fun L => ∃ ancillaLength : List Nat, ∃ family : Family [] ancillaLength,
    polynomialUniform family ∧ ∀ input,
      (L input → 2 ≤ 3 * acceptance family input (fun _ => 1)) ∧
      (¬ L input → 3 * acceptance family input (fun _ => 1) ≤ 1)

def QCMA : ComplexityClass :=
  fun L => ∃ witnessLength ancillaLength : List Nat, ∃ family : Family witnessLength ancillaLength,
    polynomialUniform family ∧ ∀ input,
      (L input → ∃ proof : Basis (polynomialValue witnessLength input.length),
        2 ≤ 3 * acceptance family input (basisState proof)) ∧
      (¬ L input → ∀ proof : Basis (polynomialValue witnessLength input.length),
        3 * acceptance family input (basisState proof) ≤ 1)

def QMA : ComplexityClass :=
  fun L => ∃ witnessLength ancillaLength : List Nat, ∃ family : Family witnessLength ancillaLength,
    polynomialUniform family ∧ ∀ input,
      (L input → ∃ proof : State (polynomialValue witnessLength input.length),
        Normalized proof ∧ 2 ≤ 3 * acceptance family input proof) ∧
      (¬ L input → ∀ proof : State (polynomialValue witnessLength input.length),
        Normalized proof → 3 * acceptance family input proof ≤ 1)

def coQMA : ComplexityClass := coClass QMA

theorem empty_circuit_run {qubits : Nat} (output : Fin qubits) (state : State qubits) :
    (Circuit.mk [] output).run state = state := rfl

theorem cnot_control_distinct {qubits : Nat} (control target : Fin qubits)
    (distinct : control ≠ target) : control ≠ target := distinct

theorem coQMA_definition (L : Language) : coQMA L ↔ QMA (complementLanguage L) := Iff.rfl

end
end InclusionBench.Quantum
