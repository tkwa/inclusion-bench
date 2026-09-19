import Std

/-!
# Extensional semantics

The theorems in this module concern actual sets of binary languages. They do
not assume that a catalog identifier has already been connected to a machine
or circuit definition. That separate obligation is exposed by `Interpretation`.
-/

namespace InclusionBench

abbrev Word := List Bool
abbrev Language := Word → Prop
abbrev ComplexityClass := Language → Prop
abbrev Interpretation (ClassId : Type) := ClassId → ComplexityClass

def Includes (A B : ComplexityClass) : Prop := ∀ L, A L → B L
def NonIncludes (A B : ComplexityClass) : Prop := ¬ Includes A B
def StrictIncludes (A B : ComplexityClass) : Prop := Includes A B ∧ NonIncludes B A
def Counterexample (A B : ComplexityClass) : Prop := ∃ L, A L ∧ ¬ B L

def complementLanguage (L : Language) : Language := fun w => ¬ L w
def coClass (A : ComplexityClass) : ComplexityClass := fun L => A (complementLanguage L)
def intersectClass (A B : ComplexityClass) : ComplexityClass := fun L => A L ∧ B L

theorem includes_refl (A : ComplexityClass) : Includes A A := fun _ h => h

theorem includes_trans {A B C : ComplexityClass}
    (hAB : Includes A B) (hBC : Includes B C) : Includes A C :=
  fun L h => hBC L (hAB L h)

theorem includes_cast {A B C D : ComplexityClass}
    (h : Includes A B) (hCA : C = A) (hDB : D = B) : Includes C D := by
  cases hCA
  cases hDB
  exact h

theorem nonincludes_cast {A B C D : ComplexityClass}
    (h : NonIncludes A B) (hCA : C = A) (hDB : D = B) : NonIncludes C D := by
  cases hCA
  cases hDB
  exact h

theorem nonincludes_iff_counterexample (A B : ComplexityClass) :
    NonIncludes A B ↔ Counterexample A B := by
  classical
  constructor
  · intro h
    apply Classical.byContradiction
    intro noWitness
    apply h
    intro L hA
    apply Classical.byContradiction
    intro hB
    exact noWitness ⟨L, hA, hB⟩
  · intro ⟨L, hA, hB⟩ h
    exact hB (h L hA)

/-- A witness in A outside B is also in C outside D when A ⊆ C and D ⊆ B. -/
theorem nonincludes_expand {A B C D : ComplexityClass}
    (hAB : NonIncludes A B) (hAC : Includes A C) (hDB : Includes D B) :
    NonIncludes C D := by
  intro hCD
  exact hAB (includes_trans hAC (includes_trans hCD hDB))

theorem nonincludes_left_expand {A B C : ComplexityClass}
    (hAB : NonIncludes A B) (hAC : Includes A C) : NonIncludes C B :=
  nonincludes_expand hAB hAC (includes_refl B)

theorem nonincludes_right_shrink {A B D : ComplexityClass}
    (hAB : NonIncludes A B) (hDB : Includes D B) : NonIncludes A D :=
  nonincludes_expand hAB (includes_refl A) hDB

theorem complement_involutive (L : Language) :
    complementLanguage (complementLanguage L) = L := by
  classical
  funext w
  exact propext (Classical.not_not)

theorem coClass_involutive (A : ComplexityClass) : coClass (coClass A) = A := by
  funext L
  simp only [coClass, complement_involutive]

theorem includes_complement {A B : ComplexityClass}
    (h : Includes A B) : Includes (coClass A) (coClass B) :=
  fun L hL => h (complementLanguage L) hL

theorem includes_complement_iff (A B : ComplexityClass) :
    Includes (coClass A) (coClass B) ↔ Includes A B := by
  constructor
  · intro h
    have hh := includes_complement h
    simpa only [coClass_involutive] using hh
  · exact includes_complement

theorem nonincludes_complement {A B : ComplexityClass}
    (h : NonIncludes A B) : NonIncludes (coClass A) (coClass B) :=
  fun hc => h ((includes_complement_iff A B).mp hc)

theorem intersect_left (A B : ComplexityClass) : Includes (intersectClass A B) A :=
  fun _ h => h.1

theorem intersect_right (A B : ComplexityClass) : Includes (intersectClass A B) B :=
  fun _ h => h.2

theorem includes_intersect {A B C : ComplexityClass}
    (hAB : Includes A B) (hAC : Includes A C) : Includes A (intersectClass B C) :=
  fun L h => ⟨hAB L h, hAC L h⟩

theorem strict_implies_distinct {A B : ComplexityClass}
    (h : StrictIncludes A B) : A ≠ B := by
  intro eq
  subst B
  exact h.2 (includes_refl A)

end InclusionBench
