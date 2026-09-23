import InclusionSupport.IntegerArrays

/-!
Succinct finite integer arrays. Their length is computed in binary and can be
numerically exponential. One entry algorithm is uniform in both original input
and binary index. This contract does not promise efficient whole-array output,
sums or dot products. Materialization requires an additional polynomial bound
on the NUMBER of entries. This module introduces no axioms.
-/

namespace InclusionBench.Support

open Counting Transducers ProofSystems RealSyntax

/-- Only indices below `length` belong to the finite array. `entry` is a total
extension, allowing one uniform algorithm to handle every binary index. -/
structure SuccinctIntegerArray where
  length : Nat
  entry : Nat → Int

def PolynomialSuccinctIntegerArray (array : Word → SuccinctIntegerArray) : Prop :=
  PolynomialNatural (fun input => (array input).length) ∧
  PolynomialIntegerEntry (fun input index => (array input).entry index)

def succinctIntegerArrayRead (array : SuccinctIntegerArray) (index : Nat) : Int :=
  if index < array.length then array.entry index else 0

def succinctIntegerArrayMap (operation : Int → Int) (array : SuccinctIntegerArray) : SuccinctIntegerArray :=
  ⟨array.length, fun index => operation (array.entry index)⟩

/-- The result has the first length. Public binary-computation rules require
matching lengths, so both entries are valid at each result index. -/
def succinctIntegerArrayZip (operation : Int → Int → Int)
    (first second : SuccinctIntegerArray) : SuccinctIntegerArray :=
  ⟨first.length, fun index => operation (first.entry index) (second.entry index)⟩

def materializeSuccinctIntegerArray (array : SuccinctIntegerArray) : List Int :=
  (List.range array.length).map array.entry

def succinctIntegerArrayOfList (values : List Int) : SuccinctIntegerArray :=
  ⟨values.length, fun index => values.getD index 0⟩

theorem polynomialSuccinctIntegerArray_intro {array : Word → SuccinctIntegerArray}
    (length : PolynomialNatural (fun input => (array input).length))
    (entry : PolynomialIntegerEntry (fun input index => (array input).entry index)) :
    PolynomialSuccinctIntegerArray array := ⟨length, entry⟩

theorem polynomialSuccinctIntegerArray_length {array : Word → SuccinctIntegerArray}
    (ha : PolynomialSuccinctIntegerArray array) : PolynomialNatural (fun input => (array input).length) := ha.1

theorem polynomialSuccinctIntegerArray_entry {array : Word → SuccinctIntegerArray}
    (ha : PolynomialSuccinctIntegerArray array) :
    PolynomialIntegerEntry (fun input index => (array input).entry index) := ha.2

/-- The length's binary representation is small; its numeric value need not be. -/
theorem polynomialSuccinctIntegerArray_length_bits {array : Word → SuccinctIntegerArray}
    (ha : PolynomialSuccinctIntegerArray array) :
    ∃ bound : List Nat, ∀ input,
      integerBitSize ((array input).length : Int) ≤ polynomialValue bound input.length :=
  fp_integer_bit_bound ha.1

/-- Exact size of the paired input charged to the one entry machine: two framing
bits per input/index bit plus three field terminators. The sign bit counts. -/
theorem polynomialIntegerEntry_bit_bound {entry : Word → Nat → Int}
    (he : PolynomialIntegerEntry entry) :
    ∃ bound : List Nat, ∀ input index,
      integerBitSize (entry input index) ≤
        polynomialValue bound (2 * (input.length + integerBitSize (index : Int)) + 3) := by
  obtain ⟨bound, bounded⟩ := fp_integer_bit_bound he
  refine ⟨bound, fun input index => ?_⟩
  have h := bounded (pairWords input (encodeInt (index : Int)))
  simp only [firstWord_pair, secondWord_pair, decodeInt_encodeInt, Int.toNat_ofNat] at h
  simpa only [pairWords, encodeTriple_length, List.length_nil, Nat.add_zero, integerBitSize] using h

theorem polynomialSuccinctIntegerArray_entry_bits {array : Word → SuccinctIntegerArray}
    (ha : PolynomialSuccinctIntegerArray array) :
    ∃ bound : List Nat, ∀ input index,
      integerBitSize ((array input).entry index) ≤
        polynomialValue bound (2 * (input.length + integerBitSize (index : Int)) + 3) :=
  polynomialIntegerEntry_bit_bound ha.2

theorem succinctIntegerArrayRead_inside (array : SuccinctIntegerArray) (index : Nat)
    (inside : index < array.length) : succinctIntegerArrayRead array index = array.entry index := by
  simp [succinctIntegerArrayRead, inside]

theorem succinctIntegerArrayRead_outside (array : SuccinctIntegerArray) (index : Nat)
    (outside : array.length ≤ index) : succinctIntegerArrayRead array index = 0 := by
  simp [succinctIntegerArrayRead, Nat.not_lt.mpr outside]

/-- A computed binary index may itself be large. The hypothesis certifies that
this requested entry belongs to the represented finite array. -/
theorem fp_succinctIntegerArray_read {array : Word → SuccinctIntegerArray} {index : Word → Nat}
    (ha : PolynomialSuccinctIntegerArray array) (hi : PolynomialNatural index)
    (inside : ∀ input, index input < (array input).length) :
    FP (fun input => succinctIntegerArrayRead (array input) (index input)) :=
  fp_congr (fp_integerEntry ha.2 hi)
    (fun input => (succinctIntegerArrayRead_inside _ _ (inside input)).symm)

theorem polynomialIntegerEntry_map {entry : Word → Nat → Int} {operation : Int → Int}
    (he : PolynomialIntegerEntry entry) (ho : PolynomialIntegerMap operation) :
    PolynomialIntegerEntry (fun input index => operation (entry input index)) := fp_integer_map ho he

theorem polynomialSuccinctIntegerArray_map {array : Word → SuccinctIntegerArray} {operation : Int → Int}
    (ha : PolynomialSuccinctIntegerArray array) (ho : PolynomialIntegerMap operation) :
    PolynomialSuccinctIntegerArray (fun input => succinctIntegerArrayMap operation (array input)) :=
  ⟨ha.1, polynomialIntegerEntry_map ha.2 ho⟩

theorem polynomialSuccinctIntegerArray_zip {first second : Word → SuccinctIntegerArray}
    {operation : Int → Int → Int}
    (hf : PolynomialSuccinctIntegerArray first) (hs : PolynomialSuccinctIntegerArray second)
    (_sameLength : ∀ input, (first input).length = (second input).length)
    (ho : PolynomialIntegerBinary operation) :
    PolynomialSuccinctIntegerArray (fun input => succinctIntegerArrayZip operation (first input) (second input)) :=
  ⟨hf.1, fp_integer_binary ho hf.2 hs.2⟩

theorem polynomialSuccinctIntegerArray_add {first second : Word → SuccinctIntegerArray}
    (hf : PolynomialSuccinctIntegerArray first) (hs : PolynomialSuccinctIntegerArray second)
    (sameLength : ∀ input, (first input).length = (second input).length) :
    PolynomialSuccinctIntegerArray (fun input => succinctIntegerArrayZip (· + ·) (first input) (second input)) :=
  polynomialSuccinctIntegerArray_zip hf hs sameLength Literature.integer_add

theorem polynomialSuccinctIntegerArray_mul {first second : Word → SuccinctIntegerArray}
    (hf : PolynomialSuccinctIntegerArray first) (hs : PolynomialSuccinctIntegerArray second)
    (sameLength : ∀ input, (first input).length = (second input).length) :
    PolynomialSuccinctIntegerArray (fun input => succinctIntegerArrayZip (· * ·) (first input) (second input)) :=
  polynomialSuccinctIntegerArray_zip hf hs sameLength Literature.integer_mul

theorem polynomialSuccinctIntegerArray_neg {array : Word → SuccinctIntegerArray}
    (ha : PolynomialSuccinctIntegerArray array) :
    PolynomialSuccinctIntegerArray (fun input => succinctIntegerArrayMap Neg.neg (array input)) :=
  polynomialSuccinctIntegerArray_map ha Literature.integer_neg

/-- This is the only materialization bridge here: its separate numeric bound
rules out emitting exponentially many entries in polynomial time. -/
theorem polynomialSuccinctIntegerArray_materialize {array : Word → SuccinctIntegerArray}
    (ha : PolynomialSuccinctIntegerArray array) (bound : List Nat)
    (small : ∀ input, (array input).length ≤ polynomialValue bound input.length) :
    PolynomialIntegerArray (fun input => materializeSuccinctIntegerArray (array input)) :=
  polynomialIntegerArray_tabulate ha.1 ha.2 bound small

theorem polynomialSuccinctIntegerArray_of_array {values : Word → List Int}
    (hv : PolynomialIntegerArray values) :
    PolynomialSuccinctIntegerArray (fun input => succinctIntegerArrayOfList (values input)) :=
  ⟨polynomialIntegerArray_length hv, polynomialIntegerArray_access hv⟩

@[simp] theorem materializeSuccinctIntegerArray_length (array : SuccinctIntegerArray) :
    (materializeSuccinctIntegerArray array).length = array.length := by
  simp [materializeSuccinctIntegerArray]

@[simp] theorem materializeSuccinctIntegerArray_of_list (values : List Int) :
    materializeSuccinctIntegerArray (succinctIntegerArrayOfList values) = values :=
  integerArray_tabulate_get values

/-- For a uniformly accessible succinct array, materializability is equivalent
to a polynomial numeric length bound. Bit-size bounds alone are insufficient. -/
theorem polynomialSuccinctIntegerArray_materialize_iff {array : Word → SuccinctIntegerArray}
    (ha : PolynomialSuccinctIntegerArray array) :
    PolynomialIntegerArray (fun input => materializeSuccinctIntegerArray (array input)) ↔
      ∃ bound : List Nat, ∀ input, (array input).length ≤ polynomialValue bound input.length := by
  constructor
  · intro explicit
    obtain ⟨bound, bounded⟩ := polynomialIntegerArray_bounds explicit
    exact ⟨bound, fun input => by simpa using (bounded input).1⟩
  · rintro ⟨bound, small⟩
    exact polynomialSuccinctIntegerArray_materialize ha bound small

end InclusionBench.Support
