import InclusionSupport.IntegerArrays

open InclusionBench InclusionBench.Support

theorem submitted : Includes Machines.polynomialTime Machines.polynomialTime := by
  intro language member
  have dot := fp_integerArray_dot (polynomialIntegerArray_const [1, 2])
    (polynomialIntegerArray_const [3, 4])
  have equal := polynomialPredicate_integer_eq dot dot
  apply p_of_predicate
  apply polynomialPredicate_congr (polynomialPredicate_and ((p_iff_predicate _).mp member) equal)
  intro word
  constructor
  · exact And.left
  · intro accepted
    exact ⟨accepted, rfl⟩
