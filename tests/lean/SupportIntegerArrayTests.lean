import InclusionSupport.IntegerArrays

set_option warningAsError true

open InclusionBench InclusionBench.Support
open InclusionBench.Machines InclusionBench.Counting InclusionBench.Transducers

example : decodeInteger (encodeInt (-257)) = -257 := decodeInt_encodeInt _
#eval do
  unless encodeInt 0 == [false] do throw (IO.userError "zero encoding")
  unless encodeInt (-5) == [true, true, false, true] do throw (IO.userError "negative encoding")
  unless integerBitSize ((2 : Int) ^ 128) == 130 do throw (IO.userError "large positive bit size")
  unless integerBitSize (-((2 : Int) ^ 128)) == 130 do throw (IO.userError "large negative bit size")
  unless integerArrayBitSize [0, -1, 257] == 29 do throw (IO.userError "array framing size")

example {first second : List Int} (encoded : encodeIntArray first = encodeIntArray second) :
    first = second := encodeIntArray_injective encoded

example {values : Word → List Int} (hv : PolynomialIntegerArray values) :
    ∃ bound : List Nat, IntegerArrayBounds values bound bound := polynomialIntegerArray_bounds hv

example {values : Word → List Int} (hv : PolynomialIntegerArray values) :
    ∃ bound : List Nat, ∀ input,
      integerArrayBitSize (values input) ≤ polynomialValue bound input.length :=
  polynomialIntegerArray_output_bound hv

-- Uniform random access requires a numeric length bound before materialization.
example {values : Word → List Int}
    (hl : PolynomialNatural (fun input => (values input).length))
    (he : PolynomialIntegerEntry (fun input index => (values input).getD index 0))
    (bound : List Nat) (small : ∀ input, (values input).length ≤ polynomialValue bound input.length) :
    PolynomialIntegerArray values := polynomialIntegerArray_of_access hl he bound small

-- A concrete table construction, with the same computation for every input.
example {value : Word → Int} (hv : FP value) :
    PolynomialIntegerArray (fun input => List.replicate 3 (value input)) :=
  polynomialIntegerArray_replicate (fp_const 3) hv [3] (by intro input; simp [polynomialValue])

example {values : Word → List Int} {index : Word → Nat}
    (hv : PolynomialIntegerArray values) (hi : PolynomialNatural index) :
    FP (fun input => (values input).getD (index input) 0) := fp_integerArray_get hv hi

example {values : Word → List Int} {index : Word → Nat} {value : Word → Int}
    (hv : PolynomialIntegerArray values) (hi : PolynomialNatural index) (hx : FP value) :
    PolynomialIntegerArray (fun input => (values input).set (index input) (value input)) :=
  polynomialIntegerArray_update hv hi hx

-- Out-of-range writes never grow an array, even at enormous binary indices.
example : ([1, 2, 3] : List Int).set (2 ^ 128) 9 = [1, 2, 3] :=
  integerArray_update_outside _ _ _ (by decide)
example : ([1, 2, 3] : List Int).getD 100 0 = 0 := by decide
example : (([1, 2, 3] : List Int).set 1 (-9)).getD 1 0 = -9 :=
  integerArray_read_update _ _ _ (by decide)

-- Generic maps must supply a uniform algorithm measured in signed binary bits.
example {values : Word → List Int} {operation : Int → Int}
    (hv : PolynomialIntegerArray values) (ho : PolynomialIntegerMap operation) :
    PolynomialIntegerArray (fun input => (values input).map operation) :=
  polynomialIntegerArray_map hv ho

-- An arithmetic array argument, with no encoding or machine obligations in the proof.
example {first second : Word → List Int} {scalar : Word → Int}
    (hf : PolynomialIntegerArray first) (hs : PolynomialIntegerArray second) (hc : FP scalar) :
    FP (fun input => integerDot ((first input).map (fun value => scalar input * value)) (second input)
      - (first input ++ second input).sum) :=
  fp_sub (fp_integerArray_dot (polynomialIntegerArray_scale hf hc) hs)
    (fp_integerArray_sum (polynomialIntegerArray_append hf hs))

-- The arithmetic equality language is in the benchmark's actual P definition.
example {first second : Word → List Int}
    (hf : PolynomialIntegerArray first) (hs : PolynomialIntegerArray second) :
    polynomialTime (fun input => integerDot (first input) (second input) = (first input).sum) :=
  p_of_predicate (polynomialPredicate_integer_eq (fp_integerArray_dot hf hs) (fp_integerArray_sum hf))

example {values : Word → List Int} (hv : PolynomialIntegerArray values) :
    GapP (fun input => (values input).sum) := gapP_of_fp (fp_integerArray_sum hv)

-- Arithmetic output growth is covered by the same bit-time contract.
example {first second : Word → List Int}
    (hf : PolynomialIntegerArray first) (hs : PolynomialIntegerArray second) :
    ∃ bound : List Nat, ∀ input,
      integerBitSize (integerDot (first input) (second input)) ≤ polynomialValue bound input.length :=
  fp_integer_bit_bound (fp_integerArray_dot hf hs)

example (first second : List Int) : (first ++ second).sum = first.sum + second.sum :=
  integerArray_sum_append first second
example (first second : List Int) : integerDot first second = integerDot second first :=
  integerDot_comm first second
example : integerDot [2, -3] [4, 5] = -7 := by decide
example : integerDot [2, -3] [4] = 8 := by decide
example : integerDot [] [4] = 0 := by decide

example {value : Word → Int} (hv : FP value) :
    PolynomialIntegerMatrix (fun input => tabulateIntegerMatrix 2 3 (fun _ _ => value input)) :=
  polynomialIntegerMatrix_tabulate (fp_const 2) (fp_const 3)
    (polynomialIntegerEntry_input hv) [2] [3] [6]
    (by intro input; simp [polynomialValue]) (by intro input; simp [polynomialValue])

example : (tabulateIntegerMatrix 2 3 (fun row column => (row + column : Int))).entries =
    [0, 1, 2, 1, 2, 3] := by decide
example : (tabulateIntegerMatrix 0 3 (fun _ _ => 7)).entries = [] := by decide
example : (tabulateIntegerMatrix 3 0 (fun _ _ => 7)).entries = [] := by decide

#print axioms InclusionBench.Support.integerArray_tabulate_get
#print axioms InclusionBench.Support.polynomialIntegerArray_bounds
#print axioms InclusionBench.Support.fp_integerArray_dot
#print axioms InclusionBench.Support.polynomialIntegerMatrix_tabulate
