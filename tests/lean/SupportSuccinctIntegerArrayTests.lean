import InclusionSupport.SuccinctIntegerArrays

set_option warningAsError true

open InclusionBench InclusionBench.Support
open InclusionBench.Counting InclusionBench.Transducers InclusionBench.ProofSystems

example {array : Word → SuccinctIntegerArray} (ha : PolynomialSuccinctIntegerArray array) :
    ∃ bound : List Nat, ∀ input index,
      integerBitSize ((array input).entry index) ≤
        polynomialValue bound (2 * (input.length + integerBitSize (index : Int)) + 3) :=
  polynomialSuccinctIntegerArray_entry_bits ha

example {array : Word → SuccinctIntegerArray} {index : Word → Nat}
    (ha : PolynomialSuccinctIntegerArray array) (hi : PolynomialNatural index)
    (valid : ∀ input, index input < (array input).length) :
    FP (fun input => succinctIntegerArrayRead (array input) (index input)) :=
  fp_succinctIntegerArray_read ha hi valid

example {first second : Word → SuccinctIntegerArray}
    (hf : PolynomialSuccinctIntegerArray first) (hs : PolynomialSuccinctIntegerArray second)
    (sameLength : ∀ input, (first input).length = (second input).length) :
    PolynomialSuccinctIntegerArray (fun input => succinctIntegerArrayZip (· * ·) (first input) (second input)) :=
  polynomialSuccinctIntegerArray_mul hf hs sameLength

example {array : Word → SuccinctIntegerArray} {operation : Int → Int}
    (ha : PolynomialSuccinctIntegerArray array) (ho : PolynomialIntegerMap operation) :
    PolynomialSuccinctIntegerArray (fun input => succinctIntegerArrayMap operation (array input)) :=
  polynomialSuccinctIntegerArray_map ha ho

example {array : Word → SuccinctIntegerArray} (ha : PolynomialSuccinctIntegerArray array)
    (bound : List Nat) (small : ∀ input, (array input).length ≤ polynomialValue bound input.length) :
    PolynomialIntegerArray (fun input => materializeSuccinctIntegerArray (array input)) :=
  polynomialSuccinctIntegerArray_materialize ha bound small

-- The numeric bound is necessary as well as sufficient for uniform materialization.
example {array : Word → SuccinctIntegerArray} (ha : PolynomialSuccinctIntegerArray array) :
    PolynomialIntegerArray (fun input => materializeSuccinctIntegerArray (array input)) ↔
      ∃ bound : List Nat, ∀ input, (array input).length ≤ polynomialValue bound input.length :=
  polynomialSuccinctIntegerArray_materialize_iff ha

example (values : List Int) : materializeSuccinctIntegerArray (succinctIntegerArrayOfList values) = values :=
  materializeSuccinctIntegerArray_of_list values

example {values : Word → List Int} (hv : PolynomialIntegerArray values) :
    PolynomialSuccinctIntegerArray (fun input => succinctIntegerArrayOfList (values input)) :=
  polynomialSuccinctIntegerArray_of_array hv

-- A concrete exponential-cardinality family constructed using only existing
-- word-pairing computation: length(false^n) = 6*4^n+1, and every entry is 7.
-- No whole-array computation is asserted or evaluated.
private def largeLength (input : Word) : Nat :=
  binaryMagnitude ([false, true, true] ++ encodeField input)

private theorem largeLength_computable : PolynomialNatural largeLength := by
  obtain ⟨machine, runtime, correct⟩ := polytime_pair (polytime_const [false]) polytime_id
  refine ⟨machine, runtime, fun input => ⟨(correct input).1, ?_⟩⟩
  change decodeInteger (machine.output input _) = (largeLength input : Int)
  rw [(correct input).2]
  rfl

private theorem falseField_value (count initial : Nat) :
    (encodeField (List.replicate count false)).foldl
      (fun value bit => 2 * value + if bit then 1 else 0) initial = 2 * initial * 4 ^ count + 1 := by
  induction count generalizing initial with
  | zero => simp [encodeField]
  | succ count ih =>
      simp only [List.replicate_succ, encodeField, List.foldl_cons, Bool.false_eq_true,
        if_false, Nat.add_zero]
      rw [ih]
      simp [Nat.pow_succ, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]
      apply congrArg (fun factor => initial * factor)
      omega

example (count : Nat) : largeLength (List.replicate count false) = 6 * 4 ^ count + 1 := by
  simp only [largeLength, binaryMagnitude, List.foldl_append, List.foldl_cons,
    List.foldl_nil, Bool.false_eq_true, Bool.true_eq, if_false, if_true]
  exact falseField_value count 3

private def largeArray (input : Word) : SuccinctIntegerArray := ⟨largeLength input, fun _ => 7⟩

private theorem largeArray_computable : PolynomialSuccinctIntegerArray largeArray :=
  ⟨largeLength_computable, polynomialIntegerEntry_input (fp_const 7)⟩

example : PolynomialSuccinctIntegerArray (fun input => succinctIntegerArrayMap Neg.neg (largeArray input)) :=
  polynomialSuccinctIntegerArray_neg largeArray_computable

#eval do
  let input := List.replicate 20 false
  unless (largeArray input).length == 6 * 4 ^ 20 + 1 do
    throw (IO.userError "succinct exponential cardinality")
  unless succinctIntegerArrayRead (largeArray input) (2 ^ 30) == 7 do
    throw (IO.userError "large binary-index read")
  unless succinctIntegerArrayRead (largeArray input) (largeArray input).length == 0 do
    throw (IO.userError "succinct out-of-range read")

-- The frequently used 2^n shape has the same interface: a uniform algorithm for
-- its binary length is the explicit premise, never a per-input machine choice.
example (countAlgorithm : PolynomialNatural (fun input => 2 ^ input.length)) :
    PolynomialSuccinctIntegerArray (fun input => ⟨2 ^ input.length, fun _ => 0⟩) :=
  ⟨countAlgorithm, polynomialIntegerEntry_input (fp_const 0)⟩

#print axioms InclusionBench.Support.polynomialSuccinctIntegerArray_entry_bits
#print axioms InclusionBench.Support.polynomialSuccinctIntegerArray_materialize_iff
