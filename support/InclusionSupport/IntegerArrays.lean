import InclusionSupport.Closure

/-!
Uniform finite integer arrays with signed-binary cost. `PolynomialIntegerArray`
requires one machine to emit the entire encoded array on every input. It therefore
bounds both the number of entries and every entry's bit size. Efficient access by
itself does not grant efficient materialization: tabulation requires a polynomial
bound on the number of entries. Standard machine bridges are registered separately;
encoding identities, size consequences, algebra and public wrappers are proved.
-/

namespace InclusionBench.Support

open Machines Counting Transducers ProofSystems RealSyntax

/-- Most-significant-bit first, without leading zeros. Zero has empty magnitude. -/
def naturalBits (value : Nat) : Word :=
  if value = 0 then []
  else naturalBits (value / 2) ++ [value % 2 == 1]
termination_by value

theorem naturalBits_value (value : Nat) : binaryMagnitude (naturalBits value) = value := by
  rw [naturalBits]
  split
  · rename_i h
    subst value
    rfl
  · rename_i h
    have ih := naturalBits_value (value / 2)
    simp only [binaryMagnitude, List.foldl_append, List.foldl_cons, List.foldl_nil] at *
    rw [ih]
    have hm : value % 2 < 2 := Nat.mod_lt _ (by decide)
    by_cases bit : value % 2 = 1 <;> simp [bit] <;> omega
termination_by value

theorem naturalBits_magnitude_bound (value : Nat) : value < 2 ^ (naturalBits value).length := by
  rw [naturalBits]
  split
  · rename_i h
    subst value
    decide
  · rename_i h
    have ih := naturalBits_magnitude_bound (value / 2)
    simp only [List.length_append, List.length_cons, List.length_nil, Nat.pow_succ]
    omega
termination_by value

/-- One sign bit followed by the minimal magnitude; zero uses the positive sign. -/
def encodeInt (value : Int) : Word := (value < 0) :: naturalBits value.natAbs

@[simp] theorem decodeInt_encodeInt (value : Int) : decodeInteger (encodeInt value) = value := by
  cases value with
  | ofNat n =>
      have h : ¬ (n : Int) < 0 := by omega
      simp [encodeInt, decodeInteger, naturalBits_value, h]
  | negSucc n =>
      have h : Int.negSucc n < 0 := by omega
      simp only [encodeInt, h, decide_true, Int.natAbs_negSucc,
        decodeInteger, Bool.true_eq, if_true, naturalBits_value]
      omega

def integerBitSize (value : Int) : Nat := (encodeInt value).length

theorem integer_magnitude_bound (value : Int) : value.natAbs < 2 ^ integerBitSize value := by
  have h := naturalBits_magnitude_bound value.natAbs
  simp only [integerBitSize, encodeInt, List.length_cons, Nat.pow_succ]
  omega

/-- Each entry is a self-delimiting field; the empty array has empty encoding. -/
def encodeIntArray : List Int → Word
  | [] => []
  | value :: rest => encodeField (encodeInt value) ++ encodeIntArray rest

def integerArrayBitSize : List Int → Nat
  | [] => 0
  | value :: rest => 2 * integerBitSize value + 1 + integerArrayBitSize rest

@[simp] theorem encodeIntArray_length (values : List Int) :
    (encodeIntArray values).length = integerArrayBitSize values := by
  induction values with
  | nil => rfl
  | cons value rest ih => simp [encodeIntArray, integerArrayBitSize, encodeField_length, ih,
      integerBitSize]

theorem integerArray_length_le_size (values : List Int) : values.length ≤ integerArrayBitSize values := by
  induction values with
  | nil => simp [integerArrayBitSize]
  | cons value rest ih => simp only [List.length_cons, integerArrayBitSize]; omega

theorem integerArray_entry_le_size {values : List Int} {value : Int} (member : value ∈ values) :
    integerBitSize value ≤ integerArrayBitSize values := by
  induction values with
  | nil => simp at member
  | cons head rest ih =>
      simp only [List.mem_cons] at member
      simp only [integerArrayBitSize]
      cases member with
      | inl same => subst value; omega
      | inr inside => have h := ih inside; omega

theorem integerArray_size_le (values : List Int) (bits : Nat)
    (bounded : ∀ value ∈ values, integerBitSize value ≤ bits) :
    integerArrayBitSize values ≤ values.length * (2 * bits + 1) := by
  induction values with
  | nil => simp [integerArrayBitSize]
  | cons head rest ih =>
      have hb := bounded head (by simp)
      have hr := ih (fun value member => bounded value (by simp [member]))
      simp only [integerArrayBitSize, List.length_cons, Nat.add_mul, Nat.one_mul]
      omega

theorem encodeIntArray_injective {first second : List Int}
    (same : encodeIntArray first = encodeIntArray second) : first = second := by
  induction first generalizing second with
  | nil =>
      cases second with
      | nil => rfl
      | cons value rest =>
          have sizes := congrArg List.length same
          simp [encodeIntArray, encodeField_length] at sizes
          omega
  | cons head rest ih =>
      cases second with
      | nil =>
          have sizes := congrArg List.length same
          simp [encodeIntArray, encodeField_length] at sizes
      | cons other tail =>
          have decoded := congrArg decodeField same
          simp only [encodeIntArray, decodeField_encode_append, Option.some.injEq,
            Prod.mk.injEq] at decoded
          have heads := congrArg decodeInteger decoded.1
          simp only [decodeInt_encodeInt] at heads
          rw [heads, ih decoded.2]

/-- A single total polynomial-time machine emits the complete array. -/
def PolynomialIntegerArray (values : Word → List Int) : Prop :=
  PolynomialTimeComputable (fun input => encodeIntArray (values input))

/-- Both bounds hold uniformly on all inputs and all entries. -/
def IntegerArrayBounds (values : Word → List Int) (lengthBound bitBound : List Nat) : Prop :=
  ∀ input, (values input).length ≤ polynomialValue lengthBound input.length ∧
    ∀ value ∈ values input, integerBitSize value ≤ polynomialValue bitBound input.length

/-- Total polynomial-time computation of a natural, represented in binary. A
polynomial bit bound alone does NOT bound the natural's numeric value. -/
def PolynomialNatural (value : Word → Nat) : Prop := FP (fun input => (value input : Int))

/-- One uniform entry algorithm on the encoded pair (input, signed binary index).
Negative decoded indices denote zero; this makes the algorithm total on all words. -/
def PolynomialIntegerEntry (entry : Word → Nat → Int) : Prop :=
  FP (fun encoded => entry (firstWord encoded) (decodeInteger (secondWord encoded)).toNat)

/-- Bit-time computation on arbitrary signed binary integers, with one algorithm. -/
def PolynomialIntegerMap (operation : Int → Int) : Prop :=
  FP (fun encoded => operation (decodeInteger encoded))

def PolynomialIntegerBinary (operation : Int → Int → Int) : Prop :=
  FP (fun encoded => operation (decodeInteger (firstWord encoded))
    (decodeInteger (secondWord encoded)))

namespace Literature

axiom integer_normalize :
  PolynomialTimeComputable (fun encoded => encodeInt (decodeInteger encoded))

axiom integer_add : PolynomialIntegerBinary (· + ·)
axiom integer_mul : PolynomialIntegerBinary (· * ·)
axiom integer_neg : PolynomialIntegerMap Neg.neg

axiom integerArray_tabulate {count : Word → Nat} {entry : Word → Nat → Int}
    (hc : PolynomialNatural count) (he : PolynomialIntegerEntry entry)
    (bound : List Nat) (size : ∀ input, count input ≤ polynomialValue bound input.length) :
  PolynomialIntegerArray (fun input => (List.range (count input)).map (entry input))

axiom integerArray_access {values : Word → List Int} (hv : PolynomialIntegerArray values) :
  PolynomialIntegerEntry (fun input index => (values input).getD index 0)

axiom integerArray_length {values : Word → List Int} (hv : PolynomialIntegerArray values) :
  PolynomialNatural (fun input => (values input).length)

axiom integerArray_update {values : Word → List Int} {index : Word → Nat} {value : Word → Int}
    (hv : PolynomialIntegerArray values) (hi : PolynomialNatural index) (hx : FP value) :
  PolynomialIntegerArray (fun input => (values input).set (index input) (value input))

axiom integerArray_append {first second : Word → List Int}
    (hf : PolynomialIntegerArray first) (hs : PolynomialIntegerArray second) :
  PolynomialIntegerArray (fun input => first input ++ second input)

axiom integerArray_map {values : Word → List Int} {operation : Int → Int}
    (hv : PolynomialIntegerArray values) (ho : PolynomialIntegerMap operation) :
  PolynomialIntegerArray (fun input => (values input).map operation)

axiom integerArray_zipWith {first second : Word → List Int} {operation : Int → Int → Int}
    (hf : PolynomialIntegerArray first) (hs : PolynomialIntegerArray second)
    (ho : PolynomialIntegerBinary operation) :
  PolynomialIntegerArray (fun input => List.zipWith operation (first input) (second input))

axiom integerArray_sum {values : Word → List Int} (hv : PolynomialIntegerArray values) :
  FP (fun input => (values input).sum)

end Literature

theorem fp_iff_integer_encoding (value : Word → Int) :
    FP value ↔ PolynomialTimeComputable (fun input => encodeInt (value input)) := by
  constructor
  · rintro ⟨machine, runtime, correct⟩
    have output : PolynomialTimeComputable
        (fun input => machine.output input (polynomialValue runtime input.length)) :=
      ⟨machine, runtime, fun input => ⟨(correct input).1, rfl⟩⟩
    have composed := polytime_comp output Literature.integer_normalize
    have same : (fun input => encodeInt (decodeInteger
        (machine.output input (polynomialValue runtime input.length)))) =
        (fun input => encodeInt (value input)) := by
      funext input
      exact congrArg encodeInt (correct input).2
    exact same ▸ composed
  · rintro ⟨machine, runtime, correct⟩
    refine ⟨machine, runtime, fun input => ⟨(correct input).1, ?_⟩⟩
    change decodeInteger (machine.output input _) = value input
    rw [(correct input).2, decodeInt_encodeInt]

theorem fp_congr {first second : Word → Int} (hf : FP first)
    (same : ∀ input, first input = second input) : FP second := by
  have equality : first = second := funext same
  exact equality ▸ hf

theorem fp_precompose {value : Word → Int} {function : Word → Word}
    (hv : FP value) (hf : PolynomialTimeComputable function) : FP (fun input => value (function input)) :=
  (fp_iff_integer_encoding _).mpr (polytime_comp hf ((fp_iff_integer_encoding _).mp hv))

theorem fp_const (value : Int) : FP (fun _ => value) :=
  (fp_iff_integer_encoding _).mpr (polytime_const (encodeInt value))

theorem fp_integer_bit_bound {value : Word → Int} (hv : FP value) :
    ∃ bound : List Nat, ∀ input, integerBitSize (value input) ≤ polynomialValue bound input.length :=
  reduction_output_polynomial_length ((fp_iff_integer_encoding _).mp hv)

theorem fp_integer_map {operation : Int → Int} {value : Word → Int}
    (ho : PolynomialIntegerMap operation) (hv : FP value) : FP (fun input => operation (value input)) :=
  fp_congr (fp_precompose ho ((fp_iff_integer_encoding _).mp hv)) (by simp)

theorem fp_integer_binary {operation : Int → Int → Int} {first second : Word → Int}
    (ho : PolynomialIntegerBinary operation) (hf : FP first) (hs : FP second) :
    FP (fun input => operation (first input) (second input)) :=
  fp_congr (fp_precompose ho (polytime_pair
    ((fp_iff_integer_encoding _).mp hf) ((fp_iff_integer_encoding _).mp hs))) (by simp)

theorem fp_add {first second : Word → Int} (hf : FP first) (hs : FP second) :
    FP (fun input => first input + second input) := fp_integer_binary Literature.integer_add hf hs

theorem fp_mul {first second : Word → Int} (hf : FP first) (hs : FP second) :
    FP (fun input => first input * second input) := fp_integer_binary Literature.integer_mul hf hs

theorem fp_neg {value : Word → Int} (hv : FP value) : FP (fun input => -value input) :=
  fp_integer_map Literature.integer_neg hv

theorem fp_sub {first second : Word → Int} (hf : FP first) (hs : FP second) :
    FP (fun input => first input - second input) :=
  fp_congr (fp_add hf (fp_neg hs)) (fun _ => Int.sub_eq_add_neg.symm)

theorem polynomialPredicate_integer_eq {first second : Word → Int} (hf : FP first) (hs : FP second) :
    PolynomialPredicate (fun input => first input = second input) := by
  apply polynomialPredicate_congr (polynomialPredicate_eq
    ((fp_iff_integer_encoding _).mp hf) ((fp_iff_integer_encoding _).mp hs))
  intro input
  constructor
  · intro same
    have decoded := congrArg decodeInteger same
    simpa using decoded
  · exact congrArg encodeInt

theorem polynomialIntegerArray_congr {first second : Word → List Int}
    (hf : PolynomialIntegerArray first) (same : ∀ input, first input = second input) :
    PolynomialIntegerArray second := by
  have equality : first = second := funext same
  exact equality ▸ hf

theorem polynomialIntegerArray_bounds {values : Word → List Int} (hv : PolynomialIntegerArray values) :
    ∃ bound : List Nat, IntegerArrayBounds values bound bound := by
  obtain ⟨bound, output⟩ := reduction_output_polynomial_length hv
  refine ⟨bound, fun input => ⟨?_, ?_⟩⟩
  · exact Nat.le_trans (integerArray_length_le_size _) (by simpa using output input)
  · intro value member
    exact Nat.le_trans (integerArray_entry_le_size member) (by simpa using output input)

theorem polynomialIntegerArray_output_bound {values : Word → List Int}
    (hv : PolynomialIntegerArray values) :
    ∃ bound : List Nat, ∀ input, integerArrayBitSize (values input) ≤ polynomialValue bound input.length := by
  simpa using reduction_output_polynomial_length hv

theorem polynomialPredicate_integerArray_eq {first second : Word → List Int}
    (hf : PolynomialIntegerArray first) (hs : PolynomialIntegerArray second) :
    PolynomialPredicate (fun input => first input = second input) := by
  apply polynomialPredicate_congr (polynomialPredicate_eq hf hs)
  intro input
  exact ⟨encodeIntArray_injective, congrArg encodeIntArray⟩

theorem polynomialIntegerArray_precompose {values : Word → List Int} {function : Word → Word}
    (hv : PolynomialIntegerArray values) (hf : PolynomialTimeComputable function) :
    PolynomialIntegerArray (fun input => values (function input)) := polytime_comp hf hv

theorem polynomialIntegerArray_const (values : List Int) : PolynomialIntegerArray (fun _ => values) :=
  polytime_const (encodeIntArray values)

theorem polynomialIntegerArray_tabulate {count : Word → Nat} {entry : Word → Nat → Int}
    (hc : PolynomialNatural count) (he : PolynomialIntegerEntry entry)
    (bound : List Nat) (size : ∀ input, count input ≤ polynomialValue bound input.length) :
    PolynomialIntegerArray (fun input => (List.range (count input)).map (entry input)) :=
  Literature.integerArray_tabulate hc he bound size

theorem polynomialIntegerArray_access {values : Word → List Int} (hv : PolynomialIntegerArray values) :
    PolynomialIntegerEntry (fun input index => (values input).getD index 0) :=
  Literature.integerArray_access hv

theorem polynomialIntegerArray_length {values : Word → List Int} (hv : PolynomialIntegerArray values) :
    PolynomialNatural (fun input => (values input).length) := Literature.integerArray_length hv

theorem integerArray_tabulate_get (values : List Int) :
    (List.range values.length).map (fun index => values.getD index 0) = values := by
  apply List.ext_getElem
  · simp
  · intro index left right
    simp [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem right]

/-- The converse to efficient whole-array output needs an explicit polynomial
NUMBER bound. A bit bound on the length, or efficient entry access alone, does not suffice. -/
theorem polynomialIntegerArray_of_access {values : Word → List Int}
    (hl : PolynomialNatural (fun input => (values input).length))
    (he : PolynomialIntegerEntry (fun input index => (values input).getD index 0))
    (bound : List Nat) (size : ∀ input, (values input).length ≤ polynomialValue bound input.length) :
    PolynomialIntegerArray values :=
  polynomialIntegerArray_congr (polynomialIntegerArray_tabulate hl he bound size)
    (fun input => integerArray_tabulate_get (values input))

theorem polynomialIntegerArray_iff_access (values : Word → List Int) :
    PolynomialIntegerArray values ↔
      PolynomialNatural (fun input => (values input).length) ∧
      PolynomialIntegerEntry (fun input index => (values input).getD index 0) ∧
      ∃ bound : List Nat, ∀ input, (values input).length ≤ polynomialValue bound input.length := by
  constructor
  · intro hv
    obtain ⟨bound, bounded⟩ := polynomialIntegerArray_bounds hv
    exact ⟨polynomialIntegerArray_length hv, polynomialIntegerArray_access hv,
      bound, fun input => (bounded input).1⟩
  · rintro ⟨hl, he, bound, size⟩
    exact polynomialIntegerArray_of_access hl he bound size

theorem fp_integerEntry {entry : Word → Nat → Int} {index : Word → Nat}
    (he : PolynomialIntegerEntry entry) (hi : PolynomialNatural index) :
    FP (fun input => entry input (index input)) :=
  fp_congr (fp_precompose he (polytime_pair polytime_id ((fp_iff_integer_encoding _).mp hi))) (by simp)

theorem fp_integerArray_get {values : Word → List Int} {index : Word → Nat}
    (hv : PolynomialIntegerArray values) (hi : PolynomialNatural index) :
    FP (fun input => (values input).getD (index input) 0) :=
  fp_integerEntry (polynomialIntegerArray_access hv) hi

theorem polynomialIntegerEntry_input {value : Word → Int} (hv : FP value) :
    PolynomialIntegerEntry (fun input _ => value input) := fp_precompose hv polytime_first

theorem polynomialIntegerEntry_add {first second : Word → Nat → Int}
    (hf : PolynomialIntegerEntry first) (hs : PolynomialIntegerEntry second) :
    PolynomialIntegerEntry (fun input index => first input index + second input index) := fp_add hf hs

theorem polynomialIntegerEntry_mul {first second : Word → Nat → Int}
    (hf : PolynomialIntegerEntry first) (hs : PolynomialIntegerEntry second) :
    PolynomialIntegerEntry (fun input index => first input index * second input index) := fp_mul hf hs

theorem polynomialIntegerArray_replicate {count : Word → Nat} {value : Word → Int}
    (hc : PolynomialNatural count) (hv : FP value) (bound : List Nat)
    (size : ∀ input, count input ≤ polynomialValue bound input.length) :
    PolynomialIntegerArray (fun input => List.replicate (count input) (value input)) := by
  apply polynomialIntegerArray_congr
    (polynomialIntegerArray_tabulate hc (polynomialIntegerEntry_input hv) bound size)
  intro input
  have maps (indices : List Nat) : indices.map (fun _ => value input) =
      List.replicate indices.length (value input) := by
    induction indices with
    | nil => rfl
    | cons head rest ih => simp [ih, List.replicate_succ]
  simpa using maps (List.range (count input))

theorem polynomialIntegerArray_scale {values : Word → List Int} {scalar : Word → Int}
    (hv : PolynomialIntegerArray values) (hs : FP scalar) :
    PolynomialIntegerArray (fun input => (values input).map (fun value => scalar input * value)) := by
  obtain ⟨bound, bounded⟩ := polynomialIntegerArray_bounds hv
  have result := polynomialIntegerArray_tabulate (polynomialIntegerArray_length hv)
    (polynomialIntegerEntry_mul (polynomialIntegerEntry_input hs) (polynomialIntegerArray_access hv))
    bound (fun input => (bounded input).1)
  apply polynomialIntegerArray_congr result
  intro input
  have equality := congrArg (List.map (fun value => scalar input * value))
    (integerArray_tabulate_get (values input))
  simpa only [List.map_map, Function.comp_def] using equality

/-- An out-of-range update leaves the array unchanged, rather than extending it. -/
theorem polynomialIntegerArray_update {values : Word → List Int} {index : Word → Nat} {value : Word → Int}
    (hv : PolynomialIntegerArray values) (hi : PolynomialNatural index) (hx : FP value) :
    PolynomialIntegerArray (fun input => (values input).set (index input) (value input)) :=
  Literature.integerArray_update hv hi hx

theorem polynomialIntegerArray_append {first second : Word → List Int}
    (hf : PolynomialIntegerArray first) (hs : PolynomialIntegerArray second) :
    PolynomialIntegerArray (fun input => first input ++ second input) := Literature.integerArray_append hf hs

theorem polynomialIntegerArray_map {values : Word → List Int} {operation : Int → Int}
    (hv : PolynomialIntegerArray values) (ho : PolynomialIntegerMap operation) :
    PolynomialIntegerArray (fun input => (values input).map operation) := Literature.integerArray_map hv ho

/-- Like List.zipWith, this keeps exactly the smaller input length. -/
theorem polynomialIntegerArray_zipWith {first second : Word → List Int} {operation : Int → Int → Int}
    (hf : PolynomialIntegerArray first) (hs : PolynomialIntegerArray second)
    (ho : PolynomialIntegerBinary operation) :
    PolynomialIntegerArray (fun input => List.zipWith operation (first input) (second input)) :=
  Literature.integerArray_zipWith hf hs ho

theorem polynomialIntegerArray_neg {values : Word → List Int} (hv : PolynomialIntegerArray values) :
    PolynomialIntegerArray (fun input => (values input).map Neg.neg) :=
  polynomialIntegerArray_map hv Literature.integer_neg

theorem polynomialIntegerArray_add {first second : Word → List Int}
    (hf : PolynomialIntegerArray first) (hs : PolynomialIntegerArray second) :
    PolynomialIntegerArray (fun input => List.zipWith (· + ·) (first input) (second input)) :=
  polynomialIntegerArray_zipWith hf hs Literature.integer_add

theorem polynomialIntegerArray_mul {first second : Word → List Int}
    (hf : PolynomialIntegerArray first) (hs : PolynomialIntegerArray second) :
    PolynomialIntegerArray (fun input => List.zipWith (· * ·) (first input) (second input)) :=
  polynomialIntegerArray_zipWith hf hs Literature.integer_mul

theorem fp_integerArray_sum {values : Word → List Int} (hv : PolynomialIntegerArray values) :
    FP (fun input => (values input).sum) := Literature.integerArray_sum hv

/-- Dot product of the common prefix. Equal-length vectors give the usual dot product. -/
def integerDot (first second : List Int) : Int := (List.zipWith (· * ·) first second).sum

theorem fp_integerArray_dot {first second : Word → List Int}
    (hf : PolynomialIntegerArray first) (hs : PolynomialIntegerArray second) :
    FP (fun input => integerDot (first input) (second input)) :=
  fp_integerArray_sum (polynomialIntegerArray_mul hf hs)

theorem integerArray_sum_append (first second : List Int) :
    (first ++ second).sum = first.sum + second.sum := by
  induction first with
  | nil => simp
  | cons head rest ih => simp [ih, Int.add_assoc]

theorem integerDot_comm (first second : List Int) : integerDot first second = integerDot second first := by
  induction first generalizing second with
  | nil => cases second <;> rfl
  | cons head rest ih =>
      cases second with
      | nil => rfl
      | cons other tail =>
          simp only [integerDot, List.zipWith_cons_cons, List.sum_cons] at *
          rw [Int.mul_comm head other, ih]

@[simp] theorem integerArray_update_length (values : List Int) (index : Nat) (value : Int) :
    (values.set index value).length = values.length := List.length_set

theorem integerArray_update_outside (values : List Int) (index : Nat) (value : Int)
    (outside : values.length ≤ index) : values.set index value = values :=
  List.set_eq_of_length_le outside

theorem integerArray_read_update (values : List Int) (index : Nat) (value : Int)
    (inside : index < values.length) : (values.set index value).getD index 0 = value := by
  simp [List.getD_eq_getElem?_getD, List.getElem?_set, inside]

/-- A rectangular matrix stored row by row; its shape is checked by the kernel. -/
structure IntegerMatrix where
  rows : Nat
  columns : Nat
  entries : List Int
  shape : entries.length = rows * columns

def tabulateIntegerMatrix (rows columns : Nat) (entry : Nat → Nat → Int) : IntegerMatrix where
  rows := rows
  columns := columns
  entries := (List.range (rows * columns)).map (fun index => entry (index / columns) (index % columns))
  shape := by simp

/-- Row and column NUMBER bounds remain explicit even when the other dimension
is zero and the flat array is empty. -/
def PolynomialIntegerMatrix (matrix : Word → IntegerMatrix) : Prop :=
  PolynomialIntegerArray (fun input => (matrix input).entries) ∧
  PolynomialNatural (fun input => (matrix input).rows) ∧
  PolynomialNatural (fun input => (matrix input).columns) ∧
  ∃ rowBound columnBound : List Nat, ∀ input,
    (matrix input).rows ≤ polynomialValue rowBound input.length ∧
    (matrix input).columns ≤ polynomialValue columnBound input.length

theorem polynomialIntegerMatrix_tabulate {rows columns : Word → Nat} {entry : Word → Nat → Nat → Int}
    (hr : PolynomialNatural rows) (hc : PolynomialNatural columns)
    (he : PolynomialIntegerEntry (fun input index => entry input (index / columns input) (index % columns input)))
    (rowBound columnBound cellBound : List Nat)
    (dimensions : ∀ input, rows input ≤ polynomialValue rowBound input.length ∧
      columns input ≤ polynomialValue columnBound input.length)
    (cells : ∀ input, rows input * columns input ≤ polynomialValue cellBound input.length) :
    PolynomialIntegerMatrix (fun input => tabulateIntegerMatrix (rows input) (columns input) (entry input)) := by
  have total : PolynomialNatural (fun input => rows input * columns input) :=
    fp_congr (fp_mul hr hc) (by intro input; simp)
  exact ⟨polynomialIntegerArray_tabulate total he cellBound cells, hr, hc,
    rowBound, columnBound, dimensions⟩

theorem polynomialIntegerMatrix_entries {matrix : Word → IntegerMatrix}
    (hm : PolynomialIntegerMatrix matrix) : PolynomialIntegerArray (fun input => (matrix input).entries) := hm.1

theorem fp_integerMatrix_sum {matrix : Word → IntegerMatrix} (hm : PolynomialIntegerMatrix matrix) :
    FP (fun input => (matrix input).entries.sum) := fp_integerArray_sum hm.1

end InclusionBench.Support
