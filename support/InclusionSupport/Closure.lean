import InclusionSupport.Reductions

/-!
Elementary polynomial-time computation and safe reduction-closure interfaces.
The literature imports are elementary consequences of the standard machine
model, listed separately in `registry-closure.json`. Public combinators below
are kernel-proved from those imports and the existing operational definitions.
-/

namespace InclusionBench.Support

open Machines Counting ProofSystems RealSyntax

/-- A fixed, injective, linear-size encoding compatible with verifier inputs. -/
def pairWords (first second : Word) : Word := encodeTriple first [] second

def firstWord (encoded : Word) : Word :=
  match decodeTriple encoded with
  | some (first, _, _) => first
  | none => []

def secondWord (encoded : Word) : Word :=
  match decodeTriple encoded with
  | some (_, _, second) => second
  | none => []

@[simp] theorem firstWord_pair (first second : Word) :
    firstWord (pairWords first second) = first := by
  simp [firstWord, pairWords, decodeTriple_encode]

@[simp] theorem secondWord_pair (first second : Word) :
    secondWord (pairWords first second) = second := by
  simp [secondWord, pairWords, decodeTriple_encode]

/-- An index is charged for its unary length. Bounded-iteration theorems below
only inspect polynomially many such indices. -/
def PolynomialIndexedPredicate (predicate : Word → Nat → Prop) : Prop :=
  PolynomialRelation (fun input index => predicate input index.length)

namespace Literature

axiom polytime_constant (value : Word) : PolynomialTimeComputable (fun _ => value)

axiom polytime_pair {first second : Word → Word}
    (hf : PolynomialTimeComputable first) (hs : PolynomialTimeComputable second) :
  PolynomialTimeComputable (fun word => pairWords (first word) (second word))

axiom polytime_first : PolynomialTimeComputable firstWord

axiom polytime_second : PolynomialTimeComputable secondWord

axiom polynomialPredicate_and {first second : Language}
    (hf : PolynomialPredicate first) (hs : PolynomialPredicate second) :
  PolynomialPredicate (fun word => first word ∧ second word)

axiom polynomialRelation_eq : PolynomialRelation (fun first second => first = second)

axiom polynomialPredicate_forall_range {predicate : Word → Nat → Prop}
    (computable : PolynomialIndexedPredicate predicate) (bound : List Nat) :
  PolynomialPredicate (fun word => ∀ index,
    index < polynomialValue bound word.length → predicate word index)

axiom np_precompose {language : Language} {preprocess : Word → Word}
    (member : nondeterministicPolynomialTime language)
    (computable : PolynomialTimeComputable preprocess) :
  nondeterministicPolynomialTime (fun word => language (preprocess word))

end Literature

theorem polytime_const (value : Word) : PolynomialTimeComputable (fun _ => value) :=
  Literature.polytime_constant value

theorem polytime_pair {first second : Word → Word}
    (hf : PolynomialTimeComputable first) (hs : PolynomialTimeComputable second) :
    PolynomialTimeComputable (fun word => pairWords (first word) (second word)) :=
  Literature.polytime_pair hf hs

theorem polytime_first : PolynomialTimeComputable firstWord := Literature.polytime_first

theorem polytime_second : PolynomialTimeComputable secondWord := Literature.polytime_second

theorem polynomialPredicate_congr {first second : Language}
    (computable : PolynomialPredicate first) (same : ∀ word, first word ↔ second word) :
    PolynomialPredicate second := by
  obtain ⟨verifier, correct⟩ := computable
  exact ⟨verifier, fun word => (correct word).trans (same word)⟩

theorem polynomialPredicate_and {first second : Language}
    (hf : PolynomialPredicate first) (hs : PolynomialPredicate second) :
    PolynomialPredicate (fun word => first word ∧ second word) :=
  Literature.polynomialPredicate_and hf hs

theorem polynomialPredicate_or {first second : Language}
    (hf : PolynomialPredicate first) (hs : PolynomialPredicate second) :
    PolynomialPredicate (fun word => first word ∨ second word) := by
  classical
  apply polynomialPredicate_congr
    (polynomialPredicate_not (polynomialPredicate_and
      (polynomialPredicate_not hf) (polynomialPredicate_not hs)))
  intro word
  by_cases member : first word <;> simp_all [complementLanguage]

theorem polynomialPredicate_precompose {predicate : Language} {function : Word → Word}
    (computable : PolynomialPredicate predicate) (hf : PolynomialTimeComputable function) :
    PolynomialPredicate (fun word => predicate (function word)) :=
  (p_iff_predicate _).mp (Literature.p_precompose (p_of_predicate computable) hf)

/-- A relation can be handled through an ordinary polynomial predicate on pairs.
Behavior on malformed pairs is deliberately left unrestricted. -/
theorem polynomialRelation_iff_predicate (relation : Word → Word → Prop) :
    PolynomialRelation relation ↔ ∃ predicate : Language,
      PolynomialPredicate predicate ∧
        ∀ first second, predicate (pairWords first second) ↔ relation first second := by
  constructor
  · rintro ⟨verifier, correct⟩
    exact ⟨fun word => verifier.result word = true, ⟨verifier, fun _ => Iff.rfl⟩, correct⟩
  · rintro ⟨predicate, ⟨verifier, computes⟩, correct⟩
    exact ⟨verifier, fun first second => (computes _).trans (correct first second)⟩

theorem polynomialPredicate_relation {relation : Word → Word → Prop}
    {first second : Word → Word} (computable : PolynomialRelation relation)
    (hf : PolynomialTimeComputable first) (hs : PolynomialTimeComputable second) :
    PolynomialPredicate (fun word => relation (first word) (second word)) := by
  obtain ⟨predicate, hp, correct⟩ := (polynomialRelation_iff_predicate relation).mp computable
  exact polynomialPredicate_congr
    (polynomialPredicate_precompose hp (polytime_pair hf hs))
    (fun word => correct (first word) (second word))

theorem polynomialRelation_and {first second : Word → Word → Prop}
    (hf : PolynomialRelation first) (hs : PolynomialRelation second) :
    PolynomialRelation (fun input witness => first input witness ∧ second input witness) := by
  obtain ⟨left, hl, cl⟩ := (polynomialRelation_iff_predicate first).mp hf
  obtain ⟨right, hr, cr⟩ := (polynomialRelation_iff_predicate second).mp hs
  apply (polynomialRelation_iff_predicate _).mpr
  exact ⟨fun word => left word ∧ right word, polynomialPredicate_and hl hr,
    fun input witness => and_congr (cl input witness) (cr input witness)⟩

theorem polynomialRelation_or {first second : Word → Word → Prop}
    (hf : PolynomialRelation first) (hs : PolynomialRelation second) :
    PolynomialRelation (fun input witness => first input witness ∨ second input witness) := by
  obtain ⟨left, hl, cl⟩ := (polynomialRelation_iff_predicate first).mp hf
  obtain ⟨right, hr, cr⟩ := (polynomialRelation_iff_predicate second).mp hs
  apply (polynomialRelation_iff_predicate _).mpr
  exact ⟨fun word => left word ∨ right word, polynomialPredicate_or hl hr,
    fun input witness => or_congr (cl input witness) (cr input witness)⟩

theorem polynomialRelation_precompose {relation : Word → Word → Prop}
    {first second : Word → Word} (computable : PolynomialRelation relation)
    (hf : PolynomialTimeComputable first) (hs : PolynomialTimeComputable second) :
    PolynomialRelation (fun input witness => relation (first input) (second witness)) := by
  apply (polynomialRelation_iff_predicate _).mpr
  refine ⟨fun word => relation (first (firstWord word)) (second (secondWord word)),
    polynomialPredicate_relation computable
      (polytime_comp polytime_first hf) (polytime_comp polytime_second hs), ?_⟩
  intro input witness
  simp

theorem polynomialRelation_left {predicate : Language} (computable : PolynomialPredicate predicate) :
    PolynomialRelation (fun input _ => predicate input) := by
  apply (polynomialRelation_iff_predicate _).mpr
  exact ⟨fun word => predicate (firstWord word),
    polynomialPredicate_precompose computable polytime_first, by simp⟩

theorem polynomialRelation_right {predicate : Language} (computable : PolynomialPredicate predicate) :
    PolynomialRelation (fun _ witness => predicate witness) := by
  apply (polynomialRelation_iff_predicate _).mpr
  exact ⟨fun word => predicate (secondWord word),
    polynomialPredicate_precompose computable polytime_second, by simp⟩

theorem polynomialRelation_eq : PolynomialRelation (fun first second => first = second) :=
  Literature.polynomialRelation_eq

theorem polynomialPredicate_eq {first second : Word → Word}
    (hf : PolynomialTimeComputable first) (hs : PolynomialTimeComputable second) :
    PolynomialPredicate (fun word => first word = second word) :=
  polynomialPredicate_relation polynomialRelation_eq hf hs

theorem polynomialPredicate_true : PolynomialPredicate (fun _ => True) :=
  polynomialPredicate_congr (polynomialPredicate_eq polytime_id polytime_id) (by simp)

theorem polynomialPredicate_false : PolynomialPredicate (fun _ => False) :=
  polynomialPredicate_congr (polynomialPredicate_not polynomialPredicate_true)
    (by simp [complementLanguage])

theorem polynomialIndexedPredicate_not {predicate : Word → Nat → Prop}
    (computable : PolynomialIndexedPredicate predicate) :
    PolynomialIndexedPredicate (fun word index => ¬ predicate word index) :=
  polynomialRelation_not computable

theorem polynomialIndexedPredicate_and {first second : Word → Nat → Prop}
    (hf : PolynomialIndexedPredicate first) (hs : PolynomialIndexedPredicate second) :
    PolynomialIndexedPredicate (fun word index => first word index ∧ second word index) :=
  polynomialRelation_and hf hs

theorem polynomialIndexedPredicate_or {first second : Word → Nat → Prop}
    (hf : PolynomialIndexedPredicate first) (hs : PolynomialIndexedPredicate second) :
    PolynomialIndexedPredicate (fun word index => first word index ∨ second word index) :=
  polynomialRelation_or hf hs

/-- This loops over `q(n)` indices. It does not quantify over all words of
length `q(n)`, whose number could be exponential. -/
theorem polynomialPredicate_forall_range {predicate : Word → Nat → Prop}
    (computable : PolynomialIndexedPredicate predicate) (bound : List Nat) :
    PolynomialPredicate (fun word => ∀ index,
      index < polynomialValue bound word.length → predicate word index) :=
  Literature.polynomialPredicate_forall_range computable bound

theorem polynomialPredicate_exists_range {predicate : Word → Nat → Prop}
    (computable : PolynomialIndexedPredicate predicate) (bound : List Nat) :
    PolynomialPredicate (fun word => ∃ index,
      index < polynomialValue bound word.length ∧ predicate word index) := by
  classical
  apply polynomialPredicate_congr
    (polynomialPredicate_not
      (polynomialPredicate_forall_range (polynomialIndexedPredicate_not computable) bound))
  intro word
  simp [complementLanguage]

theorem p_intersection {first second : Language}
    (hf : polynomialTime first) (hs : polynomialTime second) :
    polynomialTime (fun word => first word ∧ second word) :=
  p_of_predicate (polynomialPredicate_and ((p_iff_predicate _).mp hf) ((p_iff_predicate _).mp hs))

theorem p_union {first second : Language}
    (hf : polynomialTime first) (hs : polynomialTime second) :
    polynomialTime (fun word => first word ∨ second word) :=
  p_of_predicate (polynomialPredicate_or ((p_iff_predicate _).mp hf) ((p_iff_predicate _).mp hs))

theorem np_precompose {language : Language} {preprocess : Word → Word}
    (member : nondeterministicPolynomialTime language)
    (computable : PolynomialTimeComputable preprocess) :
    nondeterministicPolynomialTime (fun word => language (preprocess word)) :=
  Literature.np_precompose member computable

theorem np_closed_under_reductions : ClosedUnderPolyReductions nondeterministicPolynomialTime := by
  intro source target reduction member
  obtain ⟨function, computable, correct⟩ := reduction
  exact class_member_congr (fun word => (correct word).symm) (np_precompose member computable)

theorem coClass_closed_under_reductions {family : ComplexityClass}
    (closed : ClosedUnderPolyReductions family) : ClosedUnderPolyReductions (coClass family) := by
  intro source target reduction member
  exact closed (reduction_complement reduction) member

theorem coNP_closed_under_reductions :
    ClosedUnderPolyReductions (coClass nondeterministicPolynomialTime) :=
  coClass_closed_under_reductions np_closed_under_reductions

end InclusionBench.Support
