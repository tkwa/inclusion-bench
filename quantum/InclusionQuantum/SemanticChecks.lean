import InclusionQuantum.Statistical
import InclusionQuantum.Stoquastic

/-!
# Independent semantic regression checks

These checks target ways a superficially similar definition could name the
wrong complexity class. They do not establish textbook model equivalence.
The product minor and Bell-pattern obstruction check the QMA(2) boundary;
environment-sign invariance checks that QSZK cannot inspect a discarded
register; width determinacy rules out hidden BQL size advice; and integer
threshold constraints check the StoqMA gap convention.
-/

namespace InclusionBench.Quantum.Review
open scoped BigOperators
noncomputable section

/-- Tensor coordinates respect the explicit register split. -/
theorem product_coefficient {left right : Nat}
    (first : State left) (second : State right)
    (a : Basis left) (b : Basis right) :
    productState first second (joinBasis (a,b)) = first a * second b := by
  simp only [productState, split_join_basis]

/-- Every 2×2 coefficient minor of a product witness vanishes. An arbitrary
joint witness would not satisfy this invariant. -/
theorem product_minor_vanishes {left right : Nat}
    (first : State left) (second : State right)
    (a c : Basis left) (b d : Basis right) :
    productState first second (joinBasis (a,b)) *
      productState first second (joinBasis (c,d)) =
    productState first second (joinBasis (a,d)) *
      productState first second (joinBasis (c,b)) := by
  simp only [product_coefficient]
  ring

/-- A diagonal Bell pattern. Taking amplitude 1/sqrt(2) gives the familiar
normalized Bell state; the obstruction below holds for any nonzero amplitude. -/
def correlatedState (amplitude : ℂ) : State (1+1) :=
  fun bits => if (splitBasis bits).1 0 = (splitBasis bits).2 0 then amplitude else 0

/-- A Bell-pattern state cannot enter through the two-product-witness
interface, even without imposing normalization on the proposed factors. -/
theorem correlated_state_not_product (amplitude : ℂ) (nonzero : amplitude ≠ 0) :
    ¬ ∃ first second : State 1, productState first second = correlatedState amplitude := by
  rintro ⟨first,second,equal⟩
  have minor := product_minor_vanishes first second
    (fun _ => false) (fun _ => true) (fun _ => false) (fun _ => true)
  rw [equal] at minor
  simp only [correlatedState,split_join_basis] at minor
  simp at minor
  exact nonzero minor

/-- The mathematical measurement acts linearly, not by an arbitrary predicate. -/
theorem matrixAction_neg {qubits : Nat}
    (matrix : Basis qubits → Basis qubits → ℂ) (state : State qubits) :
    matrixAction matrix (fun b => -state b) = fun b => -matrixAction matrix state b := by
  funext output
  simp [matrixAction]

/-- Change phases using only the discarded environment basis label. -/
def environmentSignFlip {output environment : Nat}
    (sign : Basis environment → Bool) (state : State (output+environment)) :
    State (output+environment) :=
  fun basis => if sign (splitBasis basis).2 then -state basis else state basis

/-- Any sign change confined to the environment is invisible to every
allowed output measurement. Measuring the full purification would fail this
check: the two Bell phases are distinguishable jointly. -/
theorem environment_sign_invisible {output environment : Nat}
    (measurement : OutputMeasurement output) (sign : Basis environment → Bool)
    (state : State (output+environment)) :
    measurement.probability (environmentSignFlip sign state) = measurement.probability state := by
  classical
  unfold OutputMeasurement.probability
  apply Finset.sum_congr rfl
  intro rest _
  apply Finset.sum_congr rfl
  intro result _
  simp only [environmentSignFlip,split_join_basis]
  cases h : sign rest <;> simp [h,matrixAction_neg]

/-- The circuit header constrains its width. An arbitrary width function
cannot supply information beyond the concrete generator's serialized output. -/
theorem serialized_width_determined {left right : Nat}
    (first : Circuit left) (second : Circuit right)
    (equal : first.serialize = second.serialize) : left = right := by
  simp only [Circuit.serialize] at equal
  have fields := UniformCircuits.encode_naturals_injective equal
  exact (List.cons.inj fields).1

/-- Cross-multiplied threshold validity forces a positive denominator,
positive soundness numerator, ordered thresholds, and a nonzero gap bound. -/
theorem stoq_threshold_integer_sanity (parameters : StoquasticThresholds) (n : Nat) :
    let word := Transducers.unary n
    0 < parameters.denominator word ∧
    0 < parameters.soundnessNumerator word ∧
    parameters.soundnessNumerator word < parameters.completenessNumerator word ∧
    parameters.completenessNumerator word ≤ parameters.denominator word ∧
    0 < Counting.polynomialValue parameters.gapPolynomial n := by
  dsimp
  obtain ⟨denom,half,strict,upper,gap⟩ := parameters.valid n
  refine ⟨denom,by omega,strict,upper,?_⟩
  by_contra notpositive
  have zero : Counting.polynomialValue parameters.gapPolynomial n = 0 := by omega
  rw [zero] at gap
  simp at gap
  omega

end
end InclusionBench.Quantum.Review
