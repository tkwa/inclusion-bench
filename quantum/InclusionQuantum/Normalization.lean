import InclusionQuantum.Quantum

/-!
# Normalization for the concrete quantum model

These results concern the exact amplitudes and register embedding in Quantum.lean.
They do not assume textbook equivalence, amplification, or any class inclusion.
-/

namespace InclusionBench.Quantum

open scoped BigOperators

noncomputable section

theorem normSquared_reindex {qubits : Nat} (state : State qubits)
    (permutation : Basis qubits → Basis qubits)
    (bijective : Function.Bijective permutation) :
    normSquared (fun basis => state (permutation basis)) = normSquared state := by
  exact bijective.sum_comp (fun basis => Complex.normSq (state basis))

theorem pauliX_preserves_normSquared {qubits : Nat} (target : Fin qubits)
    (state : State qubits) :
    normSquared ((Gate.pauliX target).apply state) = normSquared state := by
  exact normSquared_reindex state (fun basis => flipped basis target)
    (Function.Involutive.bijective (fun basis => flipped_twice basis target))

theorem cnot_basis_twice {qubits : Nat} (control target : Fin qubits)
    (distinct : control ≠ target) :
    Function.Involutive (fun basis : Basis qubits =>
      if basis control then flipped basis target else basis) := by
  intro basis
  cases h : basis control <;> simp [h, flipped, distinct]

theorem cnot_preserves_normSquared {qubits : Nat} (control target : Fin qubits)
    (distinct : control ≠ target) (state : State qubits) :
    normSquared ((Gate.cnot control target distinct).apply state) = normSquared state := by
  exact normSquared_reindex state _ (cnot_basis_twice control target distinct).bijective

theorem sqrt_two_normSq : Complex.normSq (Real.sqrt 2 : ℂ) = 2 := by
  rw [Complex.normSq_ofReal]
  nlinarith [Real.sq_sqrt (show (0 : ℝ) ≤ 2 by norm_num)]

theorem tPhase_normSq : Complex.normSq tPhase = 1 := by
  rw [tPhase, Complex.normSq_div, sqrt_two_normSq]
  norm_num [Complex.normSq_apply]

theorem phaseT_preserves_normSquared {qubits : Nat} (target : Fin qubits)
    (state : State qubits) :
    normSquared ((Gate.phaseT target).apply state) = normSquared state := by
  classical
  unfold normSquared
  apply Finset.sum_congr rfl
  intro basis _
  cases h : basis target <;> simp [Gate.apply, h, Complex.normSq_mul, tPhase_normSq]

theorem hadamard_scalar_pair (a b : ℂ) :
    Complex.normSq ((a + b) / (Real.sqrt 2 : ℂ)) +
      Complex.normSq ((a - b) / (Real.sqrt 2 : ℂ)) =
      Complex.normSq a + Complex.normSq b := by
  rw [Complex.normSq_div, Complex.normSq_div, sqrt_two_normSq,
    Complex.normSq_add, Complex.normSq_sub]
  ring

theorem update_current_bit {qubits : Nat} (basis : Basis qubits)
    (target : Fin qubits) (value : Bool) (same : basis target = value) :
    Function.update basis target value = basis := by
  funext index
  by_cases h : index = target
  · subst index
    simp [same]
  · simp [h]

theorem hadamard_point_pair {qubits : Nat} (target : Fin qubits)
    (state : State qubits) (basis : Basis qubits) :
    Complex.normSq ((Gate.hadamard target).apply state basis) +
      Complex.normSq ((Gate.hadamard target).apply state (flipped basis target)) =
      Complex.normSq (state basis) + Complex.normSq (state (flipped basis target)) := by
  cases h : basis target
  · have current := update_current_bit basis target false h
    simpa [Gate.apply, flipped, h, current, sub_eq_add_neg]
      using hadamard_scalar_pair (state basis) (state (Function.update basis target true))
  · have current := update_current_bit basis target true h
    simpa [Gate.apply, flipped, h, current, sub_eq_add_neg, add_comm]
      using hadamard_scalar_pair (state (Function.update basis target false)) (state basis)

theorem hadamard_preserves_normSquared {qubits : Nat} (target : Fin qubits)
    (state : State qubits) :
    normSquared ((Gate.hadamard target).apply state) = normSquared state := by
  classical
  have paired := Finset.sum_congr (s₁ := Finset.univ) (s₂ := Finset.univ) rfl
    (fun basis _ => hadamard_point_pair target state basis)
  rw [Finset.sum_add_distrib, Finset.sum_add_distrib] at paired
  have h1 := normSquared_reindex ((Gate.hadamard target).apply state)
    (fun basis => flipped basis target)
    (Function.Involutive.bijective (fun basis => flipped_twice basis target))
  have h2 := pauliX_preserves_normSquared target state
  change (∑ basis, Complex.normSq ((Gate.hadamard target).apply state (flipped basis target))) =
    normSquared ((Gate.hadamard target).apply state) at h1
  change (∑ basis, Complex.normSq (state (flipped basis target))) = normSquared state at h2
  rw [h1, h2] at paired
  change normSquared ((Gate.hadamard target).apply state) +
    normSquared ((Gate.hadamard target).apply state) = normSquared state + normSquared state at paired
  linarith

theorem gate_preserves_normSquared {qubits : Nat} (gate : Gate qubits)
    (state : State qubits) : normSquared (gate.apply state) = normSquared state := by
  cases gate with
  | hadamard target => exact hadamard_preserves_normSquared target state
  | phaseT target => exact phaseT_preserves_normSquared target state
  | pauliX target => exact pauliX_preserves_normSquared target state
  | cnot control target distinct => exact cnot_preserves_normSquared control target distinct state

theorem circuit_preserves_normSquared {qubits : Nat} (circuit : Circuit qubits)
    (state : State qubits) : normSquared (circuit.run state) = normSquared state := by
  have h : ∀ (gates : List (Gate qubits)) (input : State qubits),
      normSquared (gates.foldl (fun current gate => gate.apply current) input) = normSquared input := by
    intro gates
    induction gates with
    | nil => intro input; rfl
    | cons gate gates ih =>
      intro input
      simpa only [List.foldl_cons, gate_preserves_normSquared] using ih (gate.apply input)
  exact h circuit.gates state

theorem circuit_preserves_normalized {qubits : Nat} (circuit : Circuit qubits)
    (state : State qubits) (normalized : Normalized state) : Normalized (circuit.run state) := by
  unfold Normalized at *
  rw [circuit_preserves_normSquared]
  exact normalized

/-- Extend a witness basis string by the fixed classical input and zero ancillas. -/
def embedWitnessBasis (input : Word) (witness ancilla : Nat) (bits : Basis witness) :
    Basis (input.length + witness + ancilla + 1) :=
  fun index =>
    if h : index.val < input.length then input.get ⟨index.val, h⟩
    else if h₂ : index.val < input.length + witness then
      bits ⟨index.val - input.length, by omega⟩
    else false

theorem embedWitnessBasis_input (input : Word) (witness ancilla : Nat)
    (bits : Basis witness) (index : Fin input.length) :
    embedWitnessBasis input witness ancilla bits (inputWire input.length witness ancilla index) =
      input.get index := by
  simp [embedWitnessBasis, inputWire]

theorem embedWitnessBasis_witness (input : Word) (witness ancilla : Nat)
    (bits : Basis witness) (index : Fin witness) :
    embedWitnessBasis input witness ancilla bits (witnessWire input.length witness ancilla index) =
      bits index := by
  simp [embedWitnessBasis, witnessWire, show ¬ input.length + index.val < input.length by omega,
    show input.length + index.val < input.length + witness by omega]

theorem embedWitnessBasis_ancilla (input : Word) (witness ancilla : Nat)
    (bits : Basis witness) (index : Fin (ancilla + 1)) :
    embedWitnessBasis input witness ancilla bits (ancillaWire input.length witness ancilla index) =
      false := by
  simp [embedWitnessBasis, ancillaWire,
    show ¬ input.length + witness + index.val < input.length by omega,
    show ¬ input.length + witness + index.val < input.length + witness by omega]

theorem initialState_embedWitnessBasis (input : Word) (witness ancilla : Nat)
    (proof : State witness) (bits : Basis witness) :
    initialState input witness ancilla proof (embedWitnessBasis input witness ancilla bits) =
      proof bits := by
  simp [initialState, embedWitnessBasis_input, embedWitnessBasis_witness,
    embedWitnessBasis_ancilla]

theorem embedWitnessBasis_restrict (input : Word) (witness ancilla : Nat)
    (basis : Basis (input.length + witness + ancilla + 1))
    (valid : (∀ index : Fin input.length,
        basis (inputWire input.length witness ancilla index) = input.get index) ∧
      (∀ index : Fin (ancilla + 1),
        basis (ancillaWire input.length witness ancilla index) = false)) :
    embedWitnessBasis input witness ancilla
      (fun index => basis (witnessWire input.length witness ancilla index)) = basis := by
  funext index
  unfold embedWitnessBasis
  split
  · rename_i h
    have eqIndex : inputWire input.length witness ancilla ⟨index.val, h⟩ = index := by
      apply Fin.ext
      rfl
    simpa only [eqIndex] using (valid.1 ⟨index.val, h⟩).symm
  · rename_i h
    split
    · rename_i h₂
      dsimp only
      congr 1
      apply Fin.ext
      dsimp [witnessWire]
      omega
    · rename_i h₂
      let aindex : Fin (ancilla + 1) := ⟨index.val - input.length - witness, by omega⟩
      have eqIndex : ancillaWire input.length witness ancilla aindex = index := by
        apply Fin.ext
        dsimp [ancillaWire, aindex]
        omega
      simpa only [eqIndex] using (valid.2 aindex).symm

theorem initialState_preserves_normSquared (input : Word) (witness ancilla : Nat)
    (proof : State witness) :
    normSquared (initialState input witness ancilla proof) = normSquared proof := by
  classical
  have valid_of : ∀ basis, Complex.normSq (initialState input witness ancilla proof basis) ≠ 0 →
      (∀ index : Fin input.length,
        basis (inputWire input.length witness ancilla index) = input.get index) ∧
      (∀ index : Fin (ancilla + 1),
        basis (ancillaWire input.length witness ancilla index) = false) := by
    intro basis nonzero
    by_contra invalid
    apply nonzero
    simp only [initialState, if_neg invalid, Complex.normSq_zero]
  unfold normSquared
  apply Finset.sum_bij_ne_zero
    (fun basis _ _ => fun index => basis (witnessWire input.length witness ancilla index))
  · intro _ _ _
    exact Finset.mem_univ _
  · intro basis₁ _ nonzero₁ basis₂ _ nonzero₂ same
    have one := embedWitnessBasis_restrict input witness ancilla basis₁ (valid_of basis₁ nonzero₁)
    have two := embedWitnessBasis_restrict input witness ancilla basis₂ (valid_of basis₂ nonzero₂)
    rw [← one, ← two, same]
  · intro bits _ nonzero
    refine ⟨embedWitnessBasis input witness ancilla bits, Finset.mem_univ _, ?_, ?_⟩
    · simpa only [initialState_embedWitnessBasis] using nonzero
    · funext index
      exact embedWitnessBasis_witness input witness ancilla bits index
  · intro basis _ nonzero
    simp only [initialState, if_pos (valid_of basis nonzero)]

theorem initialState_preserves_normalized (input : Word) (witness ancilla : Nat)
    (proof : State witness) (normalized : Normalized proof) :
    Normalized (initialState input witness ancilla proof) := by
  unfold Normalized at *
  rw [initialState_preserves_normSquared]
  exact normalized

theorem acceptanceProbability_nonnegative {qubits : Nat} (circuit : Circuit qubits)
    (state : State qubits) : 0 ≤ circuit.acceptanceProbability state := by
  classical
  apply Finset.sum_nonneg
  intro basis _
  split_ifs
  · exact Complex.normSq_nonneg _
  · exact le_rfl

theorem acceptanceProbability_le_normSquared {qubits : Nat} (circuit : Circuit qubits)
    (state : State qubits) : circuit.acceptanceProbability state ≤ normSquared state := by
  classical
  calc
    circuit.acceptanceProbability state ≤ normSquared (circuit.run state) := by
      apply Finset.sum_le_sum
      intro basis _
      split_ifs
      · exact le_rfl
      · exact Complex.normSq_nonneg _
    _ = normSquared state := circuit_preserves_normSquared circuit state

theorem acceptanceProbability_bounded {qubits : Nat} (circuit : Circuit qubits)
    (state : State qubits) (normalized : Normalized state) :
    0 ≤ circuit.acceptanceProbability state ∧ circuit.acceptanceProbability state ≤ 1 := by
  exact ⟨acceptanceProbability_nonnegative circuit state,
    (acceptanceProbability_le_normSquared circuit state).trans_eq normalized⟩

theorem acceptance_bounded {witnessLength ancillaLength : List Nat}
    (family : Family witnessLength ancillaLength) (input : Word)
    (proof : State (Counting.polynomialValue witnessLength input.length))
    (normalized : Normalized proof) :
    0 ≤ acceptance family input proof ∧ acceptance family input proof ≤ 1 := by
  exact acceptanceProbability_bounded _ _
    (initialState_preserves_normalized input _ _ proof normalized)

theorem empty_witness_normalized : Normalized (qubits := 0) (fun _ => (1 : ℂ)) := by
  simp [Normalized, normSquared]


end
end InclusionBench.Quantum
