import InclusionBench.Derivation

namespace InclusionBench

abbrev OrderedPair (C : Type) := C × C

/-- The eligibility list is an external, historically audited input. Missing
derivability from a finite baseline is not a proof of historical openness. -/
def uniqueEligible {C : Type} [DecidableEq C] (eligible : List (OrderedPair C)) := eligible.eraseDups

/-- One bit per ordered pair. Evidence of either polarity, or an independently
verified metatheoretic certificate for this exact pair, resolves the same bit. -/
def resolved {C : Type} (positive negative independent : OrderedPair C → Bool)
    (pair : OrderedPair C) : Bool := positive pair || negative pair || independent pair

def score {C : Type} [DecidableEq C] (eligible : List (OrderedPair C))
    (isResolved : OrderedPair C → Bool) : Nat :=
  ((uniqueEligible eligible).filter isResolved).length

theorem length_filter_bound {α : Type} (xs : List α) (p : α → Bool) :
    (xs.filter p).length ≤ xs.length := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      cases hx : p x <;> simp [List.filter_cons, hx]
      · exact Nat.le_trans ih (Nat.le_succ _)
      · exact ih

theorem length_filter_monotone {α : Type} (xs : List α) (p q : α → Bool)
    (h : ∀ x ∈ xs, p x = true → q x = true) :
    (xs.filter p).length ≤ (xs.filter q).length := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      have tail : ∀ y ∈ xs, p y = true → q y = true := by
        intro y hy
        exact h y (by simp [hy])
      have monotone := ih tail
      cases hp : p x with
      | false =>
          cases hq : q x <;> simp [List.filter_cons, hp, hq]
          · exact monotone
          · exact Nat.le_trans monotone (Nat.le_succ _)
      | true =>
          have hq : q x = true := h x (by simp) hp
          simpa [List.filter_cons, hp, hq] using Nat.succ_le_succ monotone

theorem score_bound {C : Type} [DecidableEq C] (eligible : List (OrderedPair C))
    (isResolved : OrderedPair C → Bool) :
    score eligible isResolved ≤ (uniqueEligible eligible).length :=
  length_filter_bound _ _

theorem eraseDups_loop_length_bound {α : Type} [BEq α] (pending seen : List α) :
    (List.eraseDups.loop pending seen).length ≤ pending.length + seen.length := by
  induction pending generalizing seen with
  | nil => simp [List.eraseDups.loop]
  | cons x xs ih =>
      cases hx : seen.elem x with
      | false =>
          simp only [List.eraseDups.loop, hx]
          have bound := ih (x :: seen)
          simp only [List.length_cons] at bound ⊢
          omega
      | true =>
          simp only [List.eraseDups.loop, hx]
          have bound := ih seen
          simp only [List.length_cons]
          omega

theorem score_bound_by_input_length {C : Type} [DecidableEq C]
    (eligible : List (OrderedPair C)) (isResolved : OrderedPair C → Bool) :
    score eligible isResolved ≤ eligible.length := by
  apply Nat.le_trans (score_bound eligible isResolved)
  simpa [uniqueEligible, List.eraseDups] using eraseDups_loop_length_bound eligible []

/-- A duplicated eligibility entry cannot add a numerical point, for every
resolution predicate, not just for one concrete example. -/
theorem duplicate_eligibility_same_score {C : Type} [DecidableEq C]
    (pair : OrderedPair C) (isResolved : OrderedPair C → Bool) :
    score [pair, pair] isResolved = score [pair] isResolved := by
  simp [score, uniqueEligible, List.eraseDups, List.eraseDups.loop]

theorem score_monotone {C : Type} [DecidableEq C] (eligible : List (OrderedPair C))
    (before after : OrderedPair C → Bool)
    (h : ∀ pair ∈ uniqueEligible eligible, before pair = true → after pair = true) :
    score eligible before ≤ score eligible after :=
  length_filter_monotone _ _ _ h

theorem empty_submission_zero {C : Type} [DecidableEq C] (eligible : List (OrderedPair C)) :
    score eligible (fun _ => false) = 0 := by
  simp [score]

theorem multiple_evidence_one_point {C : Type} (pair : OrderedPair C) :
    resolved (fun _ => true) (fun _ => true) (fun _ => true) pair = true := rfl

end InclusionBench
