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

end InclusionBench
