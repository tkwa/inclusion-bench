import InclusionBench.UniformCircuits

/-!
# Binary syntax for existential real feasibility

An input specifies a finite variable count and a typed postfix program for
an integer arithmetic / Boolean formula. Integer magnitudes are *binary bit
strings*, not unary magnitudes. Addition, multiplication and negation build
terms; equality, strict inequality and Boolean operations build formulas.
The program must finish with exactly one formula on its typed stack.

Records use unary tags, record lengths and variable indices, and binary
coefficient bits. This costs only polynomial overhead over an ordinary
finite-variable formula encoding: the variable count itself is explicit,
and coefficients retain linear bit length. No real-valued coefficient,
unencoded polynomial, or arbitrary predicate appears in the input syntax.
Real semantics are supplied by `InclusionQuantum.RealFeasibility`.
-/

namespace InclusionBench.RealSyntax

inductive Term where
  | variable (index : Nat)
  | natural (magnitude : Word)
  | negation (term : Term)
  | addition (left right : Term)
  | multiplication (left right : Term)
  deriving DecidableEq, Repr

inductive Formula where
  | falsum
  | verum
  | equality (left right : Term)
  | lessThan (left right : Term)
  | negation (formula : Formula)
  | conjunction (left right : Formula)
  | disjunction (left right : Formula)
  deriving DecidableEq, Repr

inductive Instruction where
  | variable (index : Nat)
  | natural (magnitude : Word)
  | negateTerm | addTerms | multiplyTerms
  | falsum | verum | equalTerms | lessTerms
  | negateFormula | andFormulas | orFormulas
  deriving DecidableEq, Repr

inductive StackEntry where
  | term (value : Term)
  | formula (value : Formula)
  deriving DecidableEq, Repr

abbrev Stack := List StackEntry

def applyInstruction : Instruction → Stack → Option Stack
  | .variable index, stack => some (.term (.variable index) :: stack)
  | .natural magnitude, stack => some (.term (.natural magnitude) :: stack)
  | .negateTerm, .term term :: stack => some (.term (.negation term) :: stack)
  | .addTerms, .term right :: .term left :: stack => some (.term (.addition left right) :: stack)
  | .multiplyTerms, .term right :: .term left :: stack =>
      some (.term (.multiplication left right) :: stack)
  | .falsum, stack => some (.formula .falsum :: stack)
  | .verum, stack => some (.formula .verum :: stack)
  | .equalTerms, .term right :: .term left :: stack => some (.formula (.equality left right) :: stack)
  | .lessTerms, .term right :: .term left :: stack => some (.formula (.lessThan left right) :: stack)
  | .negateFormula, .formula formula :: stack => some (.formula (.negation formula) :: stack)
  | .andFormulas, .formula right :: .formula left :: stack =>
      some (.formula (.conjunction left right) :: stack)
  | .orFormulas, .formula right :: .formula left :: stack =>
      some (.formula (.disjunction left right) :: stack)
  | _, _ => none

def runProgram : List Instruction → Stack → Option Stack
  | [], stack => some stack
  | instruction :: rest, stack =>
      (applyInstruction instruction stack).bind (runProgram rest)

def assemble (program : List Instruction) : Option Formula :=
  match runProgram program [] with
  | some [.formula formula] => some formula
  | _ => none

/-- A fully finite input object. All variables in the program must have
indices strictly below `variableCount`; validity is checked separately. -/
structure Instance where
  variableCount : Nat
  program : List Instruction
  deriving DecidableEq, Repr

def Instance.valid (inputObject : Instance) : Bool :=
  inputObject.program.all fun instruction => match instruction with
    | .variable index => index < inputObject.variableCount
    | _ => true

/-- All coefficient data are individual binary digits; only an index, never
an entire integer magnitude, is stored as a natural-valued payload field. -/
def instructionRecord : Instruction → Nat × List Nat
  | .variable index => (0, [index])
  | .natural magnitude => (1, magnitude.map (fun bit => if bit then 1 else 0))
  | .negateTerm => (2, [])
  | .addTerms => (3, [])
  | .multiplyTerms => (4, [])
  | .falsum => (5, [])
  | .verum => (6, [])
  | .equalTerms => (7, [])
  | .lessTerms => (8, [])
  | .negateFormula => (9, [])
  | .andFormulas => (10, [])
  | .orFormulas => (11, [])

def decodeBit : Nat → Option Bool
  | 0 => some false
  | 1 => some true
  | _ => none

def decodeInstruction : Nat × List Nat → Option Instruction
  | (0, [index]) => some (.variable index)
  | (1, payload) => (payload.mapM decodeBit).map Instruction.natural
  | (2, []) => some .negateTerm
  | (3, []) => some .addTerms
  | (4, []) => some .multiplyTerms
  | (5, []) => some .falsum
  | (6, []) => some .verum
  | (7, []) => some .equalTerms
  | (8, []) => some .lessTerms
  | (9, []) => some .negateFormula
  | (10, []) => some .andFormulas
  | (11, []) => some .orFormulas
  | _ => none

def encodeRecords : List (Nat × List Nat) → List Nat
  | [] => []
  | (tag, payload) :: rest => tag :: payload.length :: (payload ++ encodeRecords rest)

def decodeRecords : List Nat → Option (List (Nat × List Nat))
  | [] => some []
  | tag :: size :: rest =>
      if size ≤ rest.length then
        (decodeRecords (rest.drop size)).map (fun records => (tag, rest.take size) :: records)
      else none
  | [_] => none
termination_by fields => fields.length

def serialize (inputObject : Instance) : Word :=
  UniformCircuits.encodeNaturals
    (inputObject.variableCount :: encodeRecords (inputObject.program.map instructionRecord))

/-- The final equality check rejects malformed unary suffixes and any
noncanonical record spelling. It is decidable on the finite binary word. -/
def deserialize (word : Word) : Option Instance := do
  let variableCount :: fields := UniformCircuits.decodeNaturals word | none
  let records ← decodeRecords fields
  let program ← records.mapM decodeInstruction
  let inputObject : Instance := ⟨variableCount, program⟩
  if serialize inputObject = word then some inputObject else none

theorem decode_binary_digits (bits : Word) :
    (bits.map (fun bit => if bit then 1 else 0)).mapM decodeBit = some bits := by
  induction bits with
  | nil => rfl
  | cons bit bits ih => cases bit <;> simp [decodeBit, ih]

theorem decode_instruction_record (instruction : Instruction) :
    decodeInstruction (instructionRecord instruction) = some instruction := by
  cases instruction <;> simp [instructionRecord, decodeInstruction, decode_binary_digits]

theorem decode_records_encode (records : List (Nat × List Nat)) :
    decodeRecords (encodeRecords records) = some records := by
  induction records with
  | nil => simp [decodeRecords, encodeRecords]
  | cons record records ih =>
      obtain ⟨tag, payload⟩ := record
      simp [encodeRecords, decodeRecords, List.length_append, ih]

theorem decode_program_records (program : List Instruction) :
    (program.map instructionRecord).mapM decodeInstruction = some program := by
  induction program with
  | nil => rfl
  | cons instruction program ih => simp [decode_instruction_record, ih]

theorem deserialize_serialize (inputObject : Instance) :
    deserialize (serialize inputObject) = some inputObject := by
  cases inputObject with
  | mk variableCount program =>
      simp [deserialize, serialize, UniformCircuits.decode_encode_naturals,
        decode_records_encode, decode_program_records]

theorem serialize_injective {left right : Instance}
    (same : serialize left = serialize right) : left = right := by
  have h := congrArg deserialize same
  simpa only [deserialize_serialize, Option.some.injEq] using h

/-- Postfix compilation realizes every finite arithmetic term and Boolean
formula; the input grammar is not restricted to a special satisfiability fragment. -/
def Term.program : Term → List Instruction
  | .variable index => [.variable index]
  | .natural magnitude => [.natural magnitude]
  | .negation term => term.program ++ [.negateTerm]
  | .addition left right => left.program ++ right.program ++ [.addTerms]
  | .multiplication left right => left.program ++ right.program ++ [.multiplyTerms]

def Formula.program : Formula → List Instruction
  | .falsum => [.falsum]
  | .verum => [.verum]
  | .equality left right => left.program ++ right.program ++ [.equalTerms]
  | .lessThan left right => left.program ++ right.program ++ [.lessTerms]
  | .negation formula => formula.program ++ [.negateFormula]
  | .conjunction left right => left.program ++ right.program ++ [.andFormulas]
  | .disjunction left right => left.program ++ right.program ++ [.orFormulas]

theorem runProgram_append (first second : List Instruction) (stack : Stack) :
    runProgram (first ++ second) stack = (runProgram first stack).bind (runProgram second) := by
  induction first generalizing stack with
  | nil => rfl
  | cons instruction first ih =>
      cases h : applyInstruction instruction stack <;> simp [runProgram, h, ih]

theorem run_term_program (term : Term) (stack : Stack) :
    runProgram term.program stack = some (.term term :: stack) := by
  induction term generalizing stack <;>
    simp [Term.program, runProgram_append, runProgram, applyInstruction, *]

theorem run_formula_program (formula : Formula) (stack : Stack) :
    runProgram formula.program stack = some (.formula formula :: stack) := by
  induction formula generalizing stack <;>
    simp [Formula.program, runProgram_append, run_term_program, runProgram, applyInstruction, *]

theorem assemble_formula_program (formula : Formula) :
    assemble formula.program = some formula := by
  simp [assemble, run_formula_program]

/-- No real witness is encoded here. The input is simply the equation x²=2. -/
def squareTwo : Instance :=
  { variableCount := 1
    program := [.variable 0, .variable 0, .multiplyTerms, .natural [true, false], .equalTerms] }

theorem squareTwo_valid : squareTwo.valid = true := rfl

theorem squareTwo_assembles :
    assemble squareTwo.program = some (.equality (.multiplication (.variable 0) (.variable 0))
      (.natural [true, false])) := rfl

theorem malformed_stack_rejected : assemble [.addTerms] = none := rfl

/-- A total word-valued function computed by one concrete polynomial-time
write-only output transducer. The finite runtime polynomial is uniform. -/
def PolynomialTimeComputable (reduction : Word → Word) : Prop :=
  ∃ machine : Transducers.Transducer, ∃ runtime : List Nat, ∀ word,
    machine.haltsAt word (Counting.polynomialValue runtime word.length) ∧
    machine.output word (Counting.polynomialValue runtime word.length) = reduction word

def PolynomialManyOne (source target : Language) : Prop :=
  ∃ reduction : Word → Word, PolynomialTimeComputable reduction ∧
    ∀ word, source word ↔ target (reduction word)

theorem reduction_output_polynomial_length {reduction : Word → Word}
    (computable : PolynomialTimeComputable reduction) :
    ∃ runtime : List Nat, ∀ word,
      (reduction word).length ≤ Counting.polynomialValue runtime word.length := by
  obtain ⟨machine, runtime, computes⟩ := computable
  refine ⟨runtime, ?_⟩
  intro word
  rw [← (computes word).2]
  exact Transducers.output_length_le_time machine word _

end InclusionBench.RealSyntax
