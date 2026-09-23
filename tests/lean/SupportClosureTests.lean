import InclusionSupport.Closure

set_option warningAsError true

open InclusionBench InclusionBench.Support
open InclusionBench.Machines InclusionBench.Counting InclusionBench.RealSyntax

-- Ordinary computation can be assembled from known polynomial algorithms.
example {f g : Word → Word} {predicate : Language}
    (hf : PolynomialTimeComputable f) (hg : PolynomialTimeComputable g)
    (hp : PolynomialPredicate predicate) :
    polynomialTime (fun word => f word = g word ∧ ¬ predicate word) :=
  p_of_predicate (polynomialPredicate_and (polynomialPredicate_eq hf hg)
    (polynomialPredicate_not hp))

-- A textbook NP certificate argument exposes no machine states or tape moves.
example {f g : Word → Word} {predicate : Language}
    (hf : PolynomialTimeComputable f) (hg : PolynomialTimeComputable g)
    (hp : PolynomialPredicate predicate) (length : List Nat) :
    nondeterministicPolynomialTime (fun input => ∃ witness : Word,
      witness.length = polynomialValue length input.length ∧
        (f input = g witness ∧ predicate witness)) :=
  np_of_relation
    (polynomialRelation_and (polynomialRelation_precompose polynomialRelation_eq hf hg)
      (polynomialRelation_right hp)) length (fun _ => Iff.rfl)

example {f g : Word → Word}
    (hf : PolynomialTimeComputable f) (hg : PolynomialTimeComputable g) (length : List Nat) :
    coClass nondeterministicPolynomialTime (fun input => ∀ witness : Word,
      witness.length = polynomialValue length input.length → f input ≠ g witness) :=
  coNP_of_forall
    (polynomialRelation_not (polynomialRelation_precompose polynomialRelation_eq hf hg))
    length (fun _ => Iff.rfl)

example {first second : Word → Nat → Prop}
    (hf : PolynomialIndexedPredicate first) (hs : PolynomialIndexedPredicate second)
    (bound : List Nat) :
    polynomialTime (fun word => ∃ index,
      index < polynomialValue bound word.length ∧ (first word index ∨ ¬ second word index)) :=
  p_of_predicate (polynomialPredicate_exists_range
    (polynomialIndexedPredicate_or hf (polynomialIndexedPredicate_not hs)) bound)

-- Empty iteration is handled by the mathematical quantifier, with no extra axiom.
example {predicate : Word → Nat → Prop} (hp : PolynomialIndexedPredicate predicate) :
    PolynomialPredicate (fun _ => True) := by
  apply polynomialPredicate_congr (polynomialPredicate_forall_range hp [])
  simp [polynomialValue]

example {predicate : Word → Nat → Prop} (hp : PolynomialIndexedPredicate predicate) :
    PolynomialPredicate (fun _ => False) := by
  apply polynomialPredicate_congr (polynomialPredicate_exists_range hp [])
  simp [polynomialValue]

example {source target : Language} (reduces : PolynomialManyOne source target)
    (member : nondeterministicPolynomialTime target) : nondeterministicPolynomialTime source :=
  np_closed_under_reductions reduces member

example {source target : Language} (reduces : PolynomialManyOne source target)
    (member : coClass nondeterministicPolynomialTime target) :
    coClass nondeterministicPolynomialTime source :=
  coNP_closed_under_reductions reduces member

example {family : ComplexityClass} (closed : ClosedUnderPolyReductions family) :
    ClosedUnderPolyReductions (coClass family) := coClass_closed_under_reductions closed

#print axioms InclusionBench.Support.polynomialRelation_iff_predicate
#print axioms InclusionBench.Support.polynomialRelation_precompose
#print axioms InclusionBench.Support.polynomialPredicate_exists_range
#print axioms InclusionBench.Support.coNP_closed_under_reductions
