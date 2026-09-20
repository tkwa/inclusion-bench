import InclusionBench.Semantics

namespace InclusionBench

/-- A metatheoretic interface. To specialize this to ZFC, a concrete syntax,
negation, and ZFC derivation relation must be supplied and justified.
This structure does not assert that such an implementation is already present. -/
structure ProofTheory (Sentence : Type) where
  negation : Sentence → Sentence
  proves : Sentence → Prop

def Independent {S : Type} (theory : ProofTheory S) (sentence : S) : Prop :=
  ¬ theory.proves sentence ∧ ¬ theory.proves (theory.negation sentence)

/-- An independence certificate is tied to exactly one formal sentence. -/
structure IndependenceCertificate {S : Type} (theory : ProofTheory S) where
  sentence : S
  unprovable : ¬ theory.proves sentence
  unrefutable : ¬ theory.proves (theory.negation sentence)

theorem IndependenceCertificate.independent {S : Type} {theory : ProofTheory S}
    (certificate : IndependenceCertificate theory) : Independent theory certificate.sentence :=
  ⟨certificate.unprovable, certificate.unrefutable⟩

theorem independent_not_provable {S : Type} {theory : ProofTheory S} {s : S}
    (h : Independent theory s) : ¬ theory.proves s := h.1

theorem independent_not_refutable {S : Type} {theory : ProofTheory S} {s : S}
    (h : Independent theory s) : ¬ theory.proves (theory.negation s) := h.2

/-- A sentence can be independent in a sound incomplete theory. This example
guards against confusing independence with a contradiction in the metatheory. -/
def emptyTheory : ProofTheory Bool := ⟨Bool.not, fun _ => False⟩

theorem emptyTheory_independent (sentence : Bool) : Independent emptyTheory sentence :=
  ⟨fun h => h, fun h => h⟩

namespace Arithmetic

/-- First-order arithmetic terms with exactly `variables` available de Bruijn
variables. The type rules out free variables in a closed sentence. -/
inductive Term (variables : Nat) where
  | var (index : Fin variables)
  | zero
  | succ (term : Term variables)
  | add (left right : Term variables)
  | mul (left right : Term variables)
  deriving DecidableEq, Repr

/-- First-order arithmetic formulas. The language has equality, order, all
Boolean connectives, and quantification over individual natural numbers.
Under a quantifier, variable zero denotes the newly bound variable. -/
inductive Formula : Nat → Type where
  | falsum {variables : Nat} : Formula variables
  | equal {variables : Nat} (left right : Term variables) : Formula variables
  | less {variables : Nat} (left right : Term variables) : Formula variables
  | neg {variables : Nat} (formula : Formula variables) : Formula variables
  | conj {variables : Nat} (left right : Formula variables) : Formula variables
  | disj {variables : Nat} (left right : Formula variables) : Formula variables
  | implies {variables : Nat} (left right : Formula variables) : Formula variables
  | forallE {variables : Nat} (body : Formula (variables + 1)) : Formula variables
  | existsE {variables : Nat} (body : Formula (variables + 1)) : Formula variables
  deriving Repr

abbrev Sentence := Formula 0

def Term.evaluate {variables : Nat} (environment : Fin variables → Nat) :
    Term variables → Nat
  | .var index => environment index
  | .zero => 0
  | .succ term => Nat.succ (term.evaluate environment)
  | .add left right => left.evaluate environment + right.evaluate environment
  | .mul left right => left.evaluate environment * right.evaluate environment

def extendEnvironment {variables : Nat} (environment : Fin variables → Nat)
    (value : Nat) : Fin (variables + 1) → Nat :=
  Fin.cases value environment

/-- Actual semantics in the standard natural numbers. In particular,
quantifiers range over Lean's `Nat`, not a supplied model or truth predicate. -/
def Formula.Holds {variables : Nat} :
    Formula variables → (Fin variables → Nat) → Prop
  | .falsum, _ => False
  | .equal left right, environment => left.evaluate environment = right.evaluate environment
  | .less left right, environment => left.evaluate environment < right.evaluate environment
  | .neg formula, environment => ¬ formula.Holds environment
  | .conj left right, environment => left.Holds environment ∧ right.Holds environment
  | .disj left right, environment => left.Holds environment ∨ right.Holds environment
  | .implies left right, environment => left.Holds environment → right.Holds environment
  | .forallE body, environment => ∀ value : Nat, body.Holds (extendEnvironment environment value)
  | .existsE body, environment => ∃ value : Nat, body.Holds (extendEnvironment environment value)

def TrueInN (sentence : Sentence) : Prop := sentence.Holds Fin.elim0

def zeroEqualsOne : Sentence := .equal .zero (.succ .zero)

theorem zeroEqualsOne_false : ¬ TrueInN zeroEqualsOne := by
  intro impossible
  exact Nat.zero_ne_add_one 0 impossible

theorem trueInN_neg (sentence : Sentence) :
    TrueInN (.neg sentence) ↔ ¬ TrueInN sentence := Iff.rfl

/-- Closed formulas exercising standard quantification and de Bruijn binding. -/
def successorNonzero : Sentence :=
  .forallE (.neg (.equal (.succ (.var ⟨0, by decide⟩)) .zero))

theorem successorNonzero_true : TrueInN successorNonzero := by
  intro value
  exact Nat.succ_ne_zero value

def additionCommutes : Sentence :=
  .forallE (.forallE (.equal
    (.add (.var ⟨1, by decide⟩) (.var ⟨0, by decide⟩))
    (.add (.var ⟨0, by decide⟩) (.var ⟨1, by decide⟩))))

theorem additionCommutes_true : TrueInN additionCommutes := by
  intro left right
  exact Nat.add_comm left right

end Arithmetic

/-- An explicit translation of closed arithmetic formulas into a proof theory.
The target syntax/proof relation and this map must be supplied. Negation
compatibility is checked, but the structure by itself does not establish that
the target is ZFC or that the map is ZFC's standard arithmetic interpretation. -/
structure ArithmeticTranslation {S : Type} (theory : ProofTheory S) where
  translate : Arithmetic.Sentence → S
  negation_compatible : ∀ sentence,
    theory.negation (translate sentence) = translate (.neg sentence)

/-- Every translated arithmetic theorem is true in the standard natural
numbers. This quantifies over all closed formulas, not merely a restricted
arithmetical hierarchy or consistency statement. It is a premise, not an axiom. -/
def ArithmeticSound {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory) : Prop :=
  ∀ sentence : Arithmetic.Sentence,
    theory.proves (translation.translate sentence) → Arithmetic.TrueInN sentence

/-- Syntactic consistency for the supplied proof relation. -/
def Consistent {S : Type} (theory : ProofTheory S) : Prop :=
  ∀ sentence, ¬ (theory.proves sentence ∧ theory.proves (theory.negation sentence))

/-- The precise logical assumption needed below: contradictory theorems imply
the translated false arithmetic sentence. Standard classical proof systems
satisfy this, but an arbitrary `ProofTheory` need not. -/
def ArithmeticExplosion {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory) : Prop :=
  ∀ sentence, theory.proves sentence → theory.proves (theory.negation sentence) →
    theory.proves (translation.translate Arithmetic.zeroEqualsOne)

/-- A sufficient, familiar logical rule for `ArithmeticExplosion`. -/
def ClassicalExplosion {S : Type} (theory : ProofTheory S) : Prop :=
  ∀ premise conclusion, theory.proves premise → theory.proves (theory.negation premise) →
    theory.proves conclusion

theorem classicalExplosion_arithmeticExplosion {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory) (explosion : ClassicalExplosion theory) :
    ArithmeticExplosion theory translation := by
  intro sentence positive negative
  exact explosion sentence (translation.translate Arithmetic.zeroEqualsOne) positive negative

theorem arithmeticSound_not_provable_false {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory) (sound : ArithmeticSound theory translation)
    (sentence : Arithmetic.Sentence) (falseInN : ¬ Arithmetic.TrueInN sentence) :
    ¬ theory.proves (translation.translate sentence) := by
  intro proof
  exact falseInN (sound sentence proof)

theorem arithmeticSound_not_refutable_true {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory) (sound : ArithmeticSound theory translation)
    (sentence : Arithmetic.Sentence) (trueInN : Arithmetic.TrueInN sentence) :
    ¬ theory.proves (theory.negation (translation.translate sentence)) := by
  rw [translation.negation_compatible]
  intro proof
  exact sound (.neg sentence) proof trueInN

/-- Soundness implies consistency only after the needed contradiction rule is
supplied. No property of an arbitrary opaque target proof theory is inferred. -/
theorem arithmeticSound_implies_consistent {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory)
    (explosion : ArithmeticExplosion theory translation)
    (sound : ArithmeticSound theory translation) : Consistent theory := by
  intro sentence contradictory
  exact Arithmetic.zeroEqualsOne_false
    (sound Arithmetic.zeroEqualsOne (explosion sentence contradictory.1 contradictory.2))

/-- A conditional metatheorem tied to one exact target sentence. The premise
must be retained publicly: this does not produce unconditional independence. -/
structure ConditionalIndependenceCertificate {S : Type} (theory : ProofTheory S)
    (premise : Prop) where
  sentence : S
  unprovable : premise → ¬ theory.proves sentence
  unrefutable : premise → ¬ theory.proves (theory.negation sentence)

theorem ConditionalIndependenceCertificate.conditional {S : Type}
    {theory : ProofTheory S} {premise : Prop}
    (certificate : ConditionalIndependenceCertificate theory premise) :
    premise → Independent theory certificate.sentence :=
  fun assumed => ⟨certificate.unprovable assumed, certificate.unrefutable assumed⟩

/-- Instantiation requires an actual proof of the premise in the metatheory. -/
def ConditionalIndependenceCertificate.instantiate {S : Type}
    {theory : ProofTheory S} {premise : Prop}
    (certificate : ConditionalIndependenceCertificate theory premise)
    (assumed : premise) : IndependenceCertificate theory :=
  ⟨certificate.sentence, certificate.unprovable assumed, certificate.unrefutable assumed⟩

/-- Transport to a stronger premise. The implication direction is explicit. -/
def ConditionalIndependenceCertificate.ofStrongerPremise {S : Type}
    {theory : ProofTheory S} {oldPremise newPremise : Prop}
    (certificate : ConditionalIndependenceCertificate theory oldPremise)
    (implication : newPremise → oldPremise) :
    ConditionalIndependenceCertificate theory newPremise :=
  ⟨certificate.sentence,
    fun assumed => certificate.unprovable (implication assumed),
    fun assumed => certificate.unrefutable (implication assumed)⟩

abbrev ArithmeticSoundnessIndependenceCertificate {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory) :=
  ConditionalIndependenceCertificate theory (ArithmeticSound theory translation)

/-- A consistency-conditional independence certificate remains valid when its
premise is strengthened to arithmetic soundness, with explosion supplied. -/
def liftConsistencyIndependence {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory)
    (explosion : ArithmeticExplosion theory translation)
    (certificate : ConditionalIndependenceCertificate theory (Consistent theory)) :
    ArithmeticSoundnessIndependenceCertificate theory translation :=
  certificate.ofStrongerPremise
    (arithmeticSound_implies_consistent theory translation explosion)

theorem liftConsistencyIndependence_sentence {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory)
    (explosion : ArithmeticExplosion theory translation)
    (certificate : ConditionalIndependenceCertificate theory (Consistent theory)) :
    (liftConsistencyIndependence theory translation explosion certificate).sentence =
      certificate.sentence := rfl

/-- The benchmark's three allowed independence-premise categories. The ZFC
names express the admission policy: an expert must establish that the supplied
proof theory and arithmetic translation really are the intended ZFC objects. -/
inductive IndependencePremise where
  | unconditional
  | zfcConsistency
  | zfcArithmeticSoundness
  deriving DecidableEq, Repr

def IndependencePremise.Holds {S : Type} (premise : IndependencePremise)
    (theory : ProofTheory S) (translation : ArithmeticTranslation theory) : Prop :=
  match premise with
  | .unconditional => True
  | .zfcConsistency => Consistent theory
  | .zfcArithmeticSoundness => ArithmeticSound theory translation

/-- A certificate using an allowed premise category. The target is any exact
sentence of the supplied theory; it need not be an arithmetic sentence.
This type does not itself establish the external ZFC interpretation, the
target's meaning as a class inclusion, or completion of expert review. -/
abbrev AdmittedIndependenceCertificate {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory) (premise : IndependencePremise) :=
  ConditionalIndependenceCertificate theory (premise.Holds theory translation)

theorem IndependencePremise.unconditional_holds {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory) :
    IndependencePremise.unconditional.Holds theory translation := True.intro

theorem IndependencePremise.arithmeticSoundness_implies_consistency {S : Type}
    (theory : ProofTheory S) (translation : ArithmeticTranslation theory)
    (explosion : ArithmeticExplosion theory translation) :
    IndependencePremise.zfcArithmeticSoundness.Holds theory translation →
      IndependencePremise.zfcConsistency.Holds theory translation :=
  arithmeticSound_implies_consistent theory translation explosion

/-- Policy-level lifting preserves the target and strengthens only the premise. -/
def admitSoundnessFromConsistency {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory)
    (explosion : ArithmeticExplosion theory translation)
    (certificate : AdmittedIndependenceCertificate theory translation .zfcConsistency) :
    AdmittedIndependenceCertificate theory translation .zfcArithmeticSoundness :=
  liftConsistencyIndependence theory translation explosion certificate

theorem admitSoundnessFromConsistency_sentence {S : Type} (theory : ProofTheory S)
    (translation : ArithmeticTranslation theory)
    (explosion : ArithmeticExplosion theory translation)
    (certificate : AdmittedIndependenceCertificate theory translation .zfcConsistency) :
    (admitSoundnessFromConsistency theory translation explosion certificate).sentence =
      certificate.sentence := rfl

end InclusionBench
