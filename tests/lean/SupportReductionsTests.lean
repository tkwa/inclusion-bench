import InclusionSupport.Reductions
import InclusionSupport.Hierarchy

set_option warningAsError true

open InclusionBench InclusionBench.Support
open InclusionBench.Machines InclusionBench.Counting InclusionBench.RealSyntax

example {language : Language} (computable : PolynomialPredicate language) :
    polynomialTime language := p_of_predicate computable

example {language : Language} (member : polynomialTime language) :
    polynomialTime (complementLanguage language) := p_complement member

example {language : Language} {relation : Word → Word → Prop}
    (computable : PolynomialRelation relation) (length : List Nat)
    (correct : ∀ input, language input ↔ ∃ witness : Word,
      witness.length = polynomialValue length input.length ∧ relation input witness) :
    nondeterministicPolynomialTime language := np_of_relation computable length correct

example {language : Language} {relation : Word → Word → Prop}
    (computable : PolynomialRelation relation) (length : List Nat)
    (correct : ∀ input, language input ↔ ∀ witness : Word,
      witness.length = polynomialValue length input.length → relation input witness) :
    coClass nondeterministicPolynomialTime language := coNP_of_forall computable length correct

example {first second third : Language} (left : PolynomialManyOne first second)
    (right : PolynomialManyOne second third) :
    PolynomialManyOne (complementLanguage first) (complementLanguage third) :=
  reduction_complement (reduction_trans left right)

example {language : Language} : PolynomialManyOne language language := reduction_refl language

example {source target : Language} (reduction : PolynomialManyOne source target)
    (member : PP target) : CountingHierarchy.CH source :=
  ch_of_pp (pp_closed_under_reductions reduction member)

example {source target : ComplexityClass} {problem : Language}
    (complete : PolynomialComplete source problem) (closed : ClosedUnderPolyReductions target)
    (solved : target problem) : Includes source target :=
  (includes_iff_complete_problem complete closed).mpr solved

-- No domain-specific complexity assumption is needed to negate a verifier.
#print axioms InclusionBench.Support.polynomialRelation_not
#print axioms InclusionBench.Support.coNP_of_forall
#print axioms InclusionBench.Support.reduction_trans
#print axioms InclusionBench.Support.includes_iff_complete_problem
