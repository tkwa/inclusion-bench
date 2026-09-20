import InclusionQuantum.Unentangled
import InclusionQuantum.Logspace

/-!
# Quantum Statistical Difference on total inputs

Two concrete polynomial-time transducers generate quantum circuits from the
input. Each circuit starts in the all-zero state, produces a fixed polynomial
number of output qubits, and discards the remaining register. Only the output
register is accessible to a distinguishing measurement.

We use the finite-dimensional variational characterization of trace distance:
the maximum difference in acceptance probabilities over projective binary
measurements. A measurement is specified by a finite complex matrix preserving
the squared norm of every vector, followed by a subset of computational-basis
outcomes. The matrix action is an explicit finite sum. These unrestricted
measurements define the mathematical distance, not an efficient distinguishing
algorithm, an oracle, or an arbitrary interpretation of acceptance.

The yes condition is distance at least 2/3; the no condition is distance at most
1/3. Both conditions hold on every input. The circuits and their generators
therefore give a genuine polynomial-time reduction to Quantum State
Distinguishability. The Helstrom/variational characterization and QSD
completeness for full QSZK, including the honest-verifier equivalence, are
trusted mathematical bridges, not formal theorems asserted here. See Watrous,
Limits on the power of quantum statistical zero-knowledge (FOCS 2002),
https://arxiv.org/abs/quant-ph/0202111 , and Vidick and Watrous, Quantum Proofs,
section 5.3, https://arxiv.org/abs/1610.01664v1 .
-/

namespace InclusionBench.Quantum

open scoped BigOperators
open Counting (polynomialValue)

noncomputable section

def matrixAction {qubits : Nat} (matrix : Basis qubits → Basis qubits → ℂ)
    (state : State qubits) : State qubits :=
  fun output => ∑ input, matrix output input * state input

/-- A finite projective measurement after a unitary basis change. The
norm-preservation condition constrains an explicit linear matrix action. -/
structure OutputMeasurement (qubits : Nat) where
  matrix : Basis qubits → Basis qubits → ℂ
  preservesNorm : ∀ state : State qubits,
    normSquared (matrixAction matrix state) = normSquared state
  accepts : Basis qubits → Bool

def OutputMeasurement.probability {output environment : Nat}
    (measurement : OutputMeasurement output) (state : State (output + environment)) : ℝ :=
  ∑ rest : Basis environment, ∑ result : Basis output,
    if measurement.accepts result then
      Complex.normSq
        (matrixAction measurement.matrix (fun bits => state (joinBasis (bits, rest))) result)
    else 0

theorem measurement_probability_nonnegative {output environment : Nat}
    (measurement : OutputMeasurement output) (state : State (output + environment)) :
    0 ≤ measurement.probability state := by
  classical
  apply Finset.sum_nonneg
  intro rest _
  apply Finset.sum_nonneg
  intro result _
  split_ifs
  · exact Complex.normSq_nonneg _
  · exact le_rfl

theorem environment_sum_normSquared {output environment : Nat}
    (state : State (output + environment)) :
    (∑ rest : Basis environment,
      normSquared (fun bits : Basis output => state (joinBasis (bits, rest)) )) =
      normSquared state := by
  classical
  unfold normSquared
  dsimp only
  calc
    (∑ rest : Basis environment, ∑ bits : Basis output,
        Complex.normSq (state (joinBasis (bits, rest)))) =
        ∑ bits : Basis output, ∑ rest : Basis environment,
          Complex.normSq (state (joinBasis (bits, rest))) := Finset.sum_comm
    _ = ∑ pair : Basis output × Basis environment,
        Complex.normSq (state (joinBasis pair)) :=
      (Fintype.sum_prod_type (fun pair : Basis output × Basis environment =>
        Complex.normSq (state (joinBasis pair)))).symm
    _ = ∑ basis, Complex.normSq (state basis) := by
      simpa only [splitBasisEquiv] using
        (splitBasisEquiv output environment).symm.bijective.sum_comp
          (fun basis => Complex.normSq (state basis))

theorem measurement_probability_le_normSquared {output environment : Nat}
    (measurement : OutputMeasurement output) (state : State (output + environment)) :
    measurement.probability state ≤ normSquared state := by
  classical
  calc
    measurement.probability state ≤
        ∑ rest : Basis environment,
          normSquared
            (matrixAction measurement.matrix (fun bits => state (joinBasis (bits, rest)))) := by
      apply Finset.sum_le_sum
      intro rest _
      apply Finset.sum_le_sum
      intro result _
      split_ifs
      · exact le_rfl
      · exact Complex.normSq_nonneg _
    _ = ∑ rest : Basis environment,
        normSquared (fun bits : Basis output => state (joinBasis (bits, rest))) := by
      apply Finset.sum_congr rfl
      intro rest _
      exact measurement.preservesNorm _
    _ = normSquared state := environment_sum_normSquared state

theorem measurement_probability_bounded {output environment : Nat}
    (measurement : OutputMeasurement output) (state : State (output + environment))
    (normalized : Normalized state) :
    0 ≤ measurement.probability state ∧ measurement.probability state ≤ 1 :=
  ⟨measurement_probability_nonnegative measurement state,
    (measurement_probability_le_normSquared measurement state).trans_eq normalized⟩

def computationalMeasurement (qubits : Nat) (accepts : Basis qubits → Bool) :
    OutputMeasurement qubits where
  matrix := fun output input => if output = input then 1 else 0
  preservesNorm := by
    intro state
    have action : matrixAction (fun output input : Basis qubits =>
        if output = input then 1 else 0) state = state := by
      funext output
      simp [matrixAction, ite_mul]
    rw [action]
  accepts := accepts

def polynomialInputUniform {width : Nat → Nat} (family : InputCircuitFamily width) : Prop :=
  ∃ generator : Transducers.Transducer, ∃ runtime : List Nat,
    ∀ input,
      generator.haltsAt input (polynomialValue runtime input.length) ∧
      generator.output input (polynomialValue runtime input.length) = (family input).serialize

/-- The output register comes first. The environment contains an extra qubit
so every circuit can have the output-wire field required by Circuit. That
field is unused in state generation; no measurement occurs before tracing out
the environment. The size bounds are uniform and hold on every input. -/
structure QuantumSampler (outputLength : List Nat) where
  environmentLength : List Nat
  family : InputCircuitFamily
    (fun n => polynomialValue outputLength n + (polynomialValue environmentLength n + 1))
  uniform : polynomialInputUniform family
  gateBound : List Nat
  bounded : ∀ input, (family input).gates.length ≤ polynomialValue gateBound input.length

def QuantumSampler.state {outputLength : List Nat}
    (sampler : QuantumSampler outputLength) (input : Word) :
    State (polynomialValue outputLength input.length +
      (polynomialValue sampler.environmentLength input.length + 1)) :=
  (sampler.family input).run (zeroState _)

theorem sampler_state_normalized {outputLength : List Nat}
    (sampler : QuantumSampler outputLength) (input : Word) :
    Normalized (sampler.state input) :=
  circuit_preserves_normalized _ _ (zeroState_normalized _)

def measurementDifference {outputLength : List Nat}
    (first second : QuantumSampler outputLength) (input : Word)
    (measurement : OutputMeasurement (polynomialValue outputLength input.length)) : ℝ :=
  |measurement.probability (first.state input) -
    measurement.probability (second.state input)|

def quantumFar {outputLength : List Nat}
    (first second : QuantumSampler outputLength) (input : Word) : Prop :=
  ∃ measurement : OutputMeasurement (polynomialValue outputLength input.length),
    2 ≤ 3 * measurementDifference first second input measurement

def quantumClose {outputLength : List Nat}
    (first second : QuantumSampler outputLength) (input : Word) : Prop :=
  ∀ measurement : OutputMeasurement (polynomialValue outputLength input.length),
    3 * measurementDifference first second input measurement ≤ 1

def QSZK : ComplexityClass :=
  fun L => ∃ outputLength : List Nat, ∃ first second : QuantumSampler outputLength,
    ∀ input,
      (L input → quantumFar first second input) ∧
      (¬ L input → quantumClose first second input)

theorem identical_quantum_samplers_close {outputLength : List Nat}
    (sampler : QuantumSampler outputLength) (input : Word) :
    quantumClose sampler sampler input := by
  intro measurement
  simp [measurementDifference]

theorem quantum_far_close_disjoint {outputLength : List Nat}
    (first second : QuantumSampler outputLength) (input : Word) :
    ¬ (quantumFar first second input ∧ quantumClose first second input) := by
  rintro ⟨⟨measurement, distant⟩, close⟩
  have near := close measurement
  linarith

theorem measurementDifference_bounded {outputLength : List Nat}
    (first second : QuantumSampler outputLength) (input : Word)
    (measurement : OutputMeasurement (polynomialValue outputLength input.length)) :
    0 ≤ measurementDifference first second input measurement ∧
      measurementDifference first second input measurement ≤ 1 := by
  have first_bounds := measurement_probability_bounded measurement (first.state input)
    (sampler_state_normalized first input)
  have second_bounds := measurement_probability_bounded measurement (second.state input)
    (sampler_state_normalized second input)
  refine ⟨abs_nonneg _, ?_⟩
  apply abs_le.mpr
  constructor <;> linarith

end
end InclusionBench.Quantum
