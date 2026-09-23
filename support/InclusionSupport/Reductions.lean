import InclusionSupport.Counting

/-!
Polynomial-time many-one reductions and the textbook NP verifier interface.
The operational predicates are the existing core definitions. Five explicit
literature imports are registered in `support/registry-reductions.json`;
all reduction, completeness and predicate wrappers below are proved in Lean.
-/

namespace InclusionBench.Support

open Machines Counting ProofSystems RealSyntax

namespace Literature

axiom polytime_identity : PolynomialTimeComputable (fun word => word)

axiom polytime_compose {first second : Word → Word}
    (hf : PolynomialTimeComputable first) (hs : PolynomialTimeComputable second) :
  PolynomialTimeComputable (fun word => second (first word))

axiom p_precompose {language : Language} {preprocess : Word → Word}
    (member : polynomialTime language) (computable : PolynomialTimeComputable preprocess) :
  polynomialTime (fun word => language (preprocess word))

axiom p_iff_decider (language : Language) :
  polynomialTime language ↔ ∃ decider : Verifier, ∀ input,
    decider.result input = true ↔ language input

/-- A single total verifier works for every input and witness. Witness length
depends only on input length, and no randomness or advice is supplied. -/
axiom np_iff_verifier (language : Language) :
  nondeterministicPolynomialTime language ↔
    ∃ verifier : Verifier, ∃ witnessLength : List Nat, ∀ input,
      language input ↔ ∃ witness : Word,
        witness.length = polynomialValue witnessLength input.length ∧
        verifier.acceptsTriple input [] witness = true

end Literature

def PolynomialPredicate (predicate : Language) : Prop :=
  ∃ decider : Verifier, ∀ input, decider.result input = true ↔ predicate input

theorem p_iff_predicate (language : Language) :
    polynomialTime language ↔ PolynomialPredicate language := Literature.p_iff_decider language

theorem p_of_predicate {language : Language} (computable : PolynomialPredicate language) :
    polynomialTime language := (p_iff_predicate language).mpr computable

theorem p_of_decider {language : Language} (decider : Verifier)
    (correct : ∀ input, decider.result input = true ↔ language input) : polynomialTime language :=
  p_of_predicate ⟨decider, correct⟩

theorem polytime_id : PolynomialTimeComputable (fun word => word) := Literature.polytime_identity

theorem polytime_comp {first second : Word → Word}
    (hf : PolynomialTimeComputable first) (hs : PolynomialTimeComputable second) :
    PolynomialTimeComputable (fun word => second (first word)) := Literature.polytime_compose hf hs

theorem class_member_congr {family : ComplexityClass} {first second : Language}
    (same : ∀ word, first word ↔ second word) (member : family first) : family second := by
  have equality : first = second := funext (fun word => propext (same word))
  exact equality ▸ member

theorem reduction_intro {source target : Language} {function : Word → Word}
    (computable : PolynomialTimeComputable function)
    (correct : ∀ word, source word ↔ target (function word)) : PolynomialManyOne source target :=
  ⟨function, computable, correct⟩

theorem reduction_iff {source target : Language} :
    PolynomialManyOne source target ↔
      ∃ function : Word → Word, PolynomialTimeComputable function ∧
        ∀ word, source word ↔ target (function word) := Iff.rfl

theorem reduction_refl (language : Language) : PolynomialManyOne language language :=
  reduction_intro polytime_id (fun _ => Iff.rfl)

theorem reduction_trans {first second third : Language}
    (left : PolynomialManyOne first second) (right : PolynomialManyOne second third) :
    PolynomialManyOne first third := by
  obtain ⟨firstFunction, firstComputable, firstCorrect⟩ := left
  obtain ⟨secondFunction, secondComputable, secondCorrect⟩ := right
  exact reduction_intro (polytime_comp firstComputable secondComputable)
    (fun word => (firstCorrect word).trans (secondCorrect (firstFunction word)))

theorem reduction_complement {source target : Language}
    (reduction : PolynomialManyOne source target) :
    PolynomialManyOne (complementLanguage source) (complementLanguage target) := by
  obtain ⟨function, computable, correct⟩ := reduction
  refine reduction_intro computable ?_
  intro word
  exact not_congr (correct word)

theorem reduction_preimage (target : Language) {function : Word → Word}
    (computable : PolynomialTimeComputable function) :
    PolynomialManyOne (fun word => target (function word)) target :=
  reduction_intro computable (fun _ => Iff.rfl)

theorem reduction_congr {source target otherSource otherTarget : Language}
    (reduction : PolynomialManyOne source target)
    (left : ∀ word, otherSource word ↔ source word)
    (right : ∀ word, target word ↔ otherTarget word) :
    PolynomialManyOne otherSource otherTarget := by
  obtain ⟨function, computable, correct⟩ := reduction
  exact reduction_intro computable
    (fun word => (left word).trans ((correct word).trans (right (function word))))

def ClosedUnderPolyReductions (family : ComplexityClass) : Prop :=
  ∀ {source target : Language}, PolynomialManyOne source target → family target → family source

def PolynomialHard (family : ComplexityClass) (problem : Language) : Prop :=
  ∀ language, family language → PolynomialManyOne language problem

def PolynomialComplete (family : ComplexityClass) (problem : Language) : Prop :=
  family problem ∧ PolynomialHard family problem

theorem includes_of_hard_problem {source target : ComplexityClass} {problem : Language}
    (hard : PolynomialHard source problem) (closed : ClosedUnderPolyReductions target)
    (solved : target problem) : Includes source target :=
  fun language member => closed (hard language member) solved

theorem includes_iff_complete_problem {source target : ComplexityClass} {problem : Language}
    (complete : PolynomialComplete source problem) (closed : ClosedUnderPolyReductions target) :
    Includes source target ↔ target problem :=
  ⟨fun included => included problem complete.1,
    fun solved => includes_of_hard_problem complete.2 closed solved⟩

theorem hard_of_reduction {family : ComplexityClass} {first second : Language}
    (hard : PolynomialHard family first) (reduction : PolynomialManyOne first second) :
    PolynomialHard family second :=
  fun language member => reduction_trans (hard language member) reduction

theorem p_closed_under_reductions : ClosedUnderPolyReductions polynomialTime := by
  intro source target reduction member
  obtain ⟨function, computable, correct⟩ := reduction
  exact class_member_congr (fun word => (correct word).symm)
    (Literature.p_precompose member computable)

theorem spp_closed_under_reductions : ClosedUnderPolyReductions SPP := by
  intro source target reduction member
  obtain ⟨function, computable, correct⟩ := reduction
  exact class_member_congr (fun word => (correct word).symm) (spp_precompose member computable)

theorem pp_closed_under_reductions : ClosedUnderPolyReductions PP := by
  intro source target reduction member
  obtain ⟨function, computable, correct⟩ := reduction
  exact class_member_congr (fun word => (correct word).symm) (pp_precompose member computable)

theorem ceqp_closed_under_reductions : ClosedUnderPolyReductions CeqP := by
  intro source target reduction member
  obtain ⟨function, computable, correct⟩ := reduction
  exact class_member_congr (fun word => (correct word).symm) (ceqp_precompose member computable)

theorem np_iff_verifier (language : Language) :
    nondeterministicPolynomialTime language ↔
      ∃ verifier : Verifier, ∃ witnessLength : List Nat, ∀ input,
        language input ↔ ∃ witness : Word,
          witness.length = polynomialValue witnessLength input.length ∧
          verifier.acceptsTriple input [] witness = true := Literature.np_iff_verifier language

theorem np_of_verifier {language : Language} (verifier : Verifier) (witnessLength : List Nat)
    (correct : ∀ input, language input ↔ ∃ witness : Word,
      witness.length = polynomialValue witnessLength input.length ∧
      verifier.acceptsTriple input [] witness = true) : nondeterministicPolynomialTime language :=
  (np_iff_verifier language).mpr ⟨verifier, witnessLength, correct⟩

/-- Polynomial decidability of a binary relation via one total deterministic
verifier. The relation may be mathematical; its computation remains explicit. -/
def PolynomialRelation (relation : Word → Word → Prop) : Prop :=
  ∃ verifier : Verifier, ∀ input witness,
    verifier.acceptsTriple input [] witness = true ↔ relation input witness

theorem np_of_relation {language : Language} {relation : Word → Word → Prop}
    (computable : PolynomialRelation relation) (witnessLength : List Nat)
    (correct : ∀ input, language input ↔ ∃ witness : Word,
      witness.length = polynomialValue witnessLength input.length ∧ relation input witness) :
    nondeterministicPolynomialTime language := by
  obtain ⟨verifier, decides⟩ := computable
  apply np_of_verifier verifier witnessLength
  intro input
  rw [correct input]
  constructor
  · rintro ⟨witness, length, member⟩
    exact ⟨witness, length, (decides input witness).mpr member⟩
  · rintro ⟨witness, length, member⟩
    exact ⟨witness, length, (decides input witness).mp member⟩

theorem polynomialRelation_congr {first second : Word → Word → Prop}
    (computable : PolynomialRelation first)
    (same : ∀ input witness, first input witness ↔ second input witness) :
    PolynomialRelation second := by
  obtain ⟨verifier, correct⟩ := computable
  exact ⟨verifier, fun input witness => (correct input witness).trans (same input witness)⟩

private def flipAnswers (machine : DMachine) : DMachine :=
  { machine with accept := fun state => !machine.accept state }

private theorem flipAnswers_after (machine : DMachine) (word : Word) (time : Nat) :
    (flipAnswers machine).after word time = machine.after word time := by
  induction time with
  | zero => rfl
  | succ time ih =>
      change ((flipAnswers machine).step word ((flipAnswers machine).after word time)).getD
        ((flipAnswers machine).after word time) =
        (machine.step word (machine.after word time)).getD (machine.after word time)
      rw [ih]
      rfl

/-- Complementing a deterministic verifier changes its final answer only.
The machine simulation, totality certificate and polynomial clock are reused. -/
def complementVerifier (verifier : Verifier) : Verifier where
  machine := flipAnswers verifier.machine
  runtime := verifier.runtime
  halts := by
    intro word
    change (flipAnswers verifier.machine).step word
      ((flipAnswers verifier.machine).after word (polynomialValue verifier.runtime word.length)) = none
    rw [flipAnswers_after]
    exact verifier.halts word

theorem complementVerifier_result (verifier : Verifier) (word : Word) :
    (complementVerifier verifier).result word = !verifier.result word := by
  change (!(verifier.machine.accept ((flipAnswers verifier.machine).after word
    (polynomialValue verifier.runtime word.length)).state)) = !verifier.result word
  rw [flipAnswers_after]
  rfl

theorem polynomialPredicate_not {predicate : Language} (computable : PolynomialPredicate predicate) :
    PolynomialPredicate (complementLanguage predicate) := by
  obtain ⟨verifier, correct⟩ := computable
  refine ⟨complementVerifier verifier, ?_⟩
  intro input
  rw [complementVerifier_result]
  have h := correct input
  cases value : verifier.result input <;> simp_all [complementLanguage]

theorem polynomialRelation_not {relation : Word → Word → Prop}
    (computable : PolynomialRelation relation) :
    PolynomialRelation (fun input witness => ¬ relation input witness) := by
  obtain ⟨verifier, correct⟩ := computable
  refine ⟨complementVerifier verifier, ?_⟩
  intro input witness
  change ((complementVerifier verifier).result (encodeTriple input [] witness) = true) ↔ _
  rw [complementVerifier_result]
  have h := correct input witness
  change (verifier.result (encodeTriple input [] witness) = true ↔ relation input witness) at h
  cases value : verifier.result (encodeTriple input [] witness) <;> simp_all

theorem p_complement {language : Language} (member : polynomialTime language) :
    polynomialTime (complementLanguage language) :=
  p_of_predicate (polynomialPredicate_not ((p_iff_predicate language).mp member))

/-- Textbook coNP introduction: supply a polynomially decidable relation and
prove that all polynomial-length certificates satisfy it. -/
theorem coNP_of_forall {language : Language} {relation : Word → Word → Prop}
    (computable : PolynomialRelation relation) (witnessLength : List Nat)
    (correct : ∀ input, language input ↔ ∀ witness : Word,
      witness.length = polynomialValue witnessLength input.length → relation input witness) :
    coClass nondeterministicPolynomialTime language := by
  classical
  apply np_of_relation (polynomialRelation_not computable) witnessLength
  intro input
  change (¬ language input) ↔ ∃ witness : Word,
    witness.length = polynomialValue witnessLength input.length ∧ ¬ relation input witness
  constructor
  · intro outside
    apply Classical.byContradiction
    intro noCounterexample
    apply outside
    apply (correct input).mpr
    intro witness length
    apply Classical.byContradiction
    intro fails
    exact noCounterexample ⟨witness, length, fails⟩
  · rintro ⟨witness, length, fails⟩ member
    exact fails ((correct input).mp member witness length)

end InclusionBench.Support
