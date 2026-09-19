import InclusionBench.Transducers

/-!
# Context-free grammars and logarithmic-space reductions

Grammars have finitely many nonterminals, a finite list of productions, and
binary terminals. A rewrite replaces one nonterminal inside an unchanged
left and right context. Grammar membership is finite derivability from the
start symbol to the given terminal word.

The reduction is computed by a concrete total output transducer. Its output
tape is not readable by transitions and is excluded from work space. Both
the logarithmic work-space bound and a polynomial time bound are explicit.
Equivalence with textbook grammars, transducers, and alternative LogCFL
characterizations remains unproved.
-/

namespace InclusionBench.LogCFL

open Machines
open Counting (polynomialValue)
open Transducers (Transducer)

/-- Finite nonterminal symbols and binary terminal symbols. -/
abbrev Symbol (nonterminals : Nat) := Sum (Fin (nonterminals + 1)) Bool

abbrev SententialForm (nonterminals : Nat) := List (Symbol nonterminals)

structure Production (nonterminals : Nat) where
  left : Fin (nonterminals + 1)
  right : SententialForm nonterminals

structure Grammar where
  nonterminals : Nat
  start : Fin (nonterminals + 1)
  productions : List (Production nonterminals)

inductive Rewrite (grammar : Grammar) :
    SententialForm grammar.nonterminals → SententialForm grammar.nonterminals → Prop where
  | rule (leftContext rightContext : SententialForm grammar.nonterminals)
      (production : Production grammar.nonterminals)
      (present : production ∈ grammar.productions) :
      Rewrite grammar
        (leftContext ++ (Sum.inl production.left :: rightContext))
        (leftContext ++ (production.right ++ rightContext))

/-- Reflexive, transitive closure of the context-preserving grammar rewrite. -/
inductive Derives (grammar : Grammar) :
    SententialForm grammar.nonterminals → SententialForm grammar.nonterminals → Prop where
  | refl (form : SententialForm grammar.nonterminals) : Derives grammar form form
  | step {first middle last : SententialForm grammar.nonterminals}
      (previous : Derives grammar first middle) (next : Rewrite grammar middle last) :
      Derives grammar first last

def terminalForm (nonterminals : Nat) (word : Word) : SententialForm nonterminals :=
  word.map Sum.inr

def Grammar.language (grammar : Grammar) : Language :=
  fun word => Derives grammar [Sum.inl grammar.start] (terminalForm grammar.nonterminals word)

theorem derives_reflexive (grammar : Grammar) (form : SententialForm grammar.nonterminals) :
    Derives grammar form form := Derives.refl form

theorem derives_transitive {grammar : Grammar}
    {first middle last : SententialForm grammar.nonterminals}
    (left : Derives grammar first middle) (right : Derives grammar middle last) :
    Derives grammar first last := by
  induction right with
  | refl => exact left
  | step previous next ih => exact Derives.step ih next

theorem rewrite_is_derivation {grammar : Grammar}
    {first last : SententialForm grammar.nonterminals}
    (rewrite : Rewrite grammar first last) : Derives grammar first last :=
  Derives.step (Derives.refl first) rewrite

/-- A reusable concrete reduction interface. The runtime polynomial has a
finite coefficient list; the workspace bound measures only the ordinary
work tape at every visited time, including the halting configuration. -/
def logspaceTransduces (machine : Transducer) (reduction : Word → Word)
    (spaceCoefficient : Nat) (runtime : List Nat) : Prop :=
  ∀ word,
    machine.haltsAt word (polynomialValue runtime word.length) ∧
    machine.output word (polynomialValue runtime word.length) = reduction word ∧
    ∀ time ≤ polynomialValue runtime word.length,
      (machine.after word time).workSpace ≤
        spaceCoefficient * (Nat.log2 (word.length + 1) + 1)

def LogspaceComputable (reduction : Word → Word) : Prop :=
  ∃ machine : Transducer, ∃ spaceCoefficient : Nat, ∃ runtime : List Nat,
    logspaceTransduces machine reduction spaceCoefficient runtime

/-- Binary languages many-one reducible to a context-free language by one
total deterministic logarithmic-space transducer. -/
def contextFreeLogspace : ComplexityClass :=
  fun L => ∃ grammar : Grammar, ∃ reduction : Word → Word,
    LogspaceComputable reduction ∧
    ∀ word, L word ↔ grammar.language (reduction word)

theorem transduced_output_polynomial_length {machine : Transducer}
    {reduction : Word → Word} {spaceCoefficient : Nat} {runtime : List Nat}
    (computes : logspaceTransduces machine reduction spaceCoefficient runtime) (word : Word) :
    (reduction word).length ≤ polynomialValue runtime word.length := by
  rw [← (computes word).2.1]
  exact Transducers.output_length_le_time machine word _

end InclusionBench.LogCFL
