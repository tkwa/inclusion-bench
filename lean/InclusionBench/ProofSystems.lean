import InclusionBench.Counting
import InclusionBench.Randomized

/-!
# Classical proof systems with concrete verifiers

A verifier is an actual finite-control deterministic machine that halts on
every binary input within an explicitly given polynomial time bound. Inputs,
randomness, and witnesses are transmitted by an injective, self-delimiting
three-field encoding. Witness and random lengths are explicit finite
polynomials; no arbitrary length function can act as hidden advice.

MA chooses a witness before counting random strings. AM counts those random
strings for which some witness makes the verifier accept. The exhaustive
witness search in this count describes the event; it is not an algorithm
required of Arthur. NP/poly alone permits arbitrary advice indexed by input
length. Equivalence with textbook presentations and their nontrivial
containment theorems remain proof obligations.
-/

namespace InclusionBench.ProofSystems

open Machines
open Counting (polynomialValue)
open Randomized (coinStrings coinStrings_length)

theorem mem_coinStrings_iff (word : Word) (n : Nat) :
    word ∈ coinStrings n ↔ word.length = n := by
  induction n generalizing word with
  | zero => simp [coinStrings]
  | succ n ih =>
      cases word with
      | nil => simp [coinStrings]
      | cons bit remaining => cases bit <;> simp [coinStrings, ih]

/-- A false marker introduces one data bit; a true marker ends the field. -/
def encodeField : Word → Word
  | [] => [true]
  | bit :: remaining => false :: bit :: encodeField remaining

def decodeField : Word → Option (Word × Word)
  | [] => none
  | true :: remaining => some ([], remaining)
  | false :: [] => none
  | false :: bit :: remaining =>
      match decodeField remaining with
      | none => none
      | some (field, suffix) => some (bit :: field, suffix)

theorem decodeField_encode_append (field suffix : Word) :
    decodeField (encodeField field ++ suffix) = some (field, suffix) := by
  induction field with
  | nil => rfl
  | cons bit remaining ih => simp [encodeField, decodeField, ih]

theorem decodeField_encode (field : Word) :
    decodeField (encodeField field) = some (field, []) := by
  simpa using decodeField_encode_append field []

def encodeTriple (first second third : Word) : Word :=
  encodeField first ++ (encodeField second ++ encodeField third)

def decodeTriple (encoded : Word) : Option (Word × Word × Word) :=
  match decodeField encoded with
  | none => none
  | some (first, rest) =>
      match decodeField rest with
      | none => none
      | some (second, rest) =>
          match decodeField rest with
          | some (third, []) => some (first, second, third)
          | _ => none

theorem decodeTriple_encode (first second third : Word) :
    decodeTriple (encodeTriple first second third) = some (first, second, third) := by
  simp [encodeTriple, decodeTriple, decodeField_encode_append, decodeField_encode]

theorem encodeTriple_injective {a b c x y z : Word}
    (same : encodeTriple a b c = encodeTriple x y z) :
    a = x ∧ b = y ∧ c = z := by
  have decoded := congrArg decodeTriple same
  simp only [decodeTriple_encode, Option.some.injEq, Prod.mk.injEq] at decoded
  exact decoded

theorem encodeField_length (field : Word) :
    (encodeField field).length = 2 * field.length + 1 := by
  induction field with
  | nil => rfl
  | cons bit remaining ih => simp only [encodeField, List.length_cons, ih]; omega

theorem encodeTriple_length (first second third : Word) :
    (encodeTriple first second third).length =
      2 * (first.length + second.length + third.length) + 3 := by
  simp only [encodeTriple, List.length_append, encodeField_length]
  omega

/-- Halting is required at the polynomial horizon on every encoded or
malformed binary word. `DMachine.after` keeps terminal configurations fixed. -/
structure Verifier where
  machine : DMachine
  runtime : List Nat
  halts : ∀ word, machine.haltsAt word (polynomialValue runtime word.length)

def Verifier.result (verifier : Verifier) (word : Word) : Bool :=
  verifier.machine.accept
    (verifier.machine.after word (polynomialValue verifier.runtime word.length)).state

def Verifier.acceptsTriple (verifier : Verifier) (input coins witness : Word) : Bool :=
  verifier.result (encodeTriple input coins witness)

/-- A witness is fixed before the random strings are counted. -/
def maAcceptCount (verifier : Verifier) (input witness : Word) (randomBits : Nat) : Nat :=
  (coinStrings randomBits).countP (fun coins => verifier.acceptsTriple input coins witness)

/-- Merlin may choose a different witness after seeing each random string. -/
def amAcceptCount (verifier : Verifier) (input : Word)
    (randomBits witnessBits : Nat) : Nat :=
  (coinStrings randomBits).countP (fun coins =>
    (coinStrings witnessBits).any (fun witness => verifier.acceptsTriple input coins witness))

def MA : ComplexityClass :=
  fun L => ∃ verifier : Verifier, ∃ witnessLength randomLength : List Nat,
    ∀ input,
      (L input → ∃ witness : Word,
        witness.length = polynomialValue witnessLength input.length ∧
        2 * 2 ^ polynomialValue randomLength input.length ≤
          3 * maAcceptCount verifier input witness (polynomialValue randomLength input.length)) ∧
      (¬ L input → ∀ witness : Word,
        witness.length = polynomialValue witnessLength input.length →
        3 * maAcceptCount verifier input witness (polynomialValue randomLength input.length) ≤
          2 ^ polynomialValue randomLength input.length)

def coMA : ComplexityClass := coClass MA

def AM : ComplexityClass :=
  fun L => ∃ verifier : Verifier, ∃ witnessLength randomLength : List Nat,
    ∀ input,
      (L input → 2 * 2 ^ polynomialValue randomLength input.length ≤
        3 * amAcceptCount verifier input (polynomialValue randomLength input.length)
          (polynomialValue witnessLength input.length)) ∧
      (¬ L input → 3 * amAcceptCount verifier input (polynomialValue randomLength input.length)
          (polynomialValue witnessLength input.length) ≤
        2 ^ polynomialValue randomLength input.length)

def coAM : ComplexityClass := coClass AM

/-- The advice function is intentionally unrestricted except for its explicit
polynomial length bound. Its value depends on input length, not the input. -/
def NPpoly : ComplexityClass :=
  fun L => ∃ verifier : Verifier, ∃ witnessLength adviceLength : List Nat,
    ∃ advice : Nat → Word,
      (∀ n, (advice n).length ≤ polynomialValue adviceLength n) ∧
      ∀ input, L input ↔ ∃ witness : Word,
        witness.length = polynomialValue witnessLength input.length ∧
        verifier.acceptsTriple input (advice input.length) witness = true

theorem ma_count_le_random_strings (verifier : Verifier) (input witness : Word)
    (randomBits : Nat) : maAcceptCount verifier input witness randomBits ≤ 2 ^ randomBits := by
  exact Nat.le_trans List.countP_le_length (Nat.le_of_eq (coinStrings_length randomBits))

theorem am_count_le_random_strings (verifier : Verifier) (input : Word)
    (randomBits witnessBits : Nat) :
    amAcceptCount verifier input randomBits witnessBits ≤ 2 ^ randomBits := by
  exact Nat.le_trans List.countP_le_length (Nat.le_of_eq (coinStrings_length randomBits))

theorem coMA_definition (L : Language) : coMA L ↔ MA (complementLanguage L) := Iff.rfl

theorem coAM_definition (L : Language) : coAM L ↔ AM (complementLanguage L) := Iff.rfl

end InclusionBench.ProofSystems
