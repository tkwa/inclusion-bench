import InclusionBench.LogspaceClasses
import InclusionBench.CountingHierarchy
import InclusionBench.AlternatingLogtime
import InclusionBench.RealSyntax

/-!
# Independent classical semantic checks

These invariants and counterexample probes test resource accounting, branch
weights, random-access addresses, oracle words and finite real syntax. They
do not assert textbook model equivalence or resolve any candidate class pair.
-/

namespace InclusionBench.IndependentClassicalReview
open Machines Randomized

/-- Erasing cells cannot erase the charged visited interval. -/
theorem footprint_never_decreases (tape : WorkTape) (symbol : WorkSymbol)
    (direction : Direction) :
    tape.footprint ≤ (tape.writeMove symbol direction).footprint := by
  cases direction <;> cases tape with
  | mk left head right =>
      cases left <;> cases right <;>
        simp [WorkTape.footprint, WorkTape.writeMove] <;> omega

/-- One step discovers at most one new work cell. -/
theorem footprint_step_upper (tape : WorkTape) (symbol : WorkSymbol)
    (direction : Direction) :
    (tape.writeMove symbol direction).footprint ≤ tape.footprint + 1 := by
  cases direction <;> cases tape with
  | mk left head right =>
      cases left <;> cases right <;>
        simp [WorkTape.footprint, WorkTape.writeMove] <;> omega

def action4 (target : Fin 4) : Action 3 :=
  { nextState := target, write := none, inputMove := .stay, workMove := .stay }

/-- First coin accepts immediately on false; true tosses a second coin.
Exactly three of four padded two-bit tapes accept, not two of three paths. -/
def unequalDepthFair : FairMachine :=
  { states := 3
    transition := fun state _ _ =>
      if state.val = 0 then some (action4 1, action4 2)
      else if state.val = 2 then some (action4 1, action4 3)
      else none
    answer := fun state => if state.val = 1 then some true else some false }

theorem unequal_depth_fair_count : unequalDepthFair.acceptCount [] 2 = 3 := rfl

theorem unequal_depth_total_mass :
    unequalDepthFair.acceptCount [] 2 + unequalDepthFair.rejectCount [] 2 = 4 := rfl

def oneCoinTie : FairMachine :=
  { states := 3
    transition := fun state _ _ =>
      if state.val = 0 then some (action4 1, action4 3) else none
    answer := fun state => if state.val = 1 then some true else some false }

theorem majority_tie_rejected :
    ¬ (2 ^ 1 < 2 * oneCoinTie.acceptCount [] 1) := by decide

/-- Counting early terminal paths once differs intentionally from padding
fair-coin strings, and does not multiply the count at a later horizon. -/
theorem nondeterministic_halted_multiplicity :
    Counting.acceptingPaths Counting.duplicateBranchMachine [] 2 = 2 := rfl

/-- Changing the index head does not shift address-bit significance. -/
theorem address_after_head_movement :
    (({ cells := [true, false, true], position := 1 } : AlternatingLogtime.IndexTape).writeMove false .right).address = 5 := rfl

theorem high_address_bit_is_binary :
    (({ cells := [], position := 4 } : AlternatingLogtime.IndexTape).writeMove true .stay).address = 16 := rfl

/-- A true answer flag does not accept a nonterminal computation at zero fuel. -/
theorem nonterminal_flag_does_not_accept :
    ({ states := 0, tapes := 0,
       transition := fun _ _ _ _ =>
         [{ nextState := 0, workWrite := Fin.elim0, workMove := Fin.elim0,
            indexWrite := false, indexMove := .stay }],
       universal := fun _ => true, accept := fun _ => true } : AlternatingLogtime.Machine).evaluateFrom [] 0 {} = false := rfl

/-- Blank query cells are omitted in a deterministic, explicit order. -/
theorem query_encoding_holes :
    ({ machine := {}, queryTape :=
        { left := [some false, none, some true], head := none,
          right := [some true, none, some false] } } : Oracles.OracleConfiguration 0).queryWord = [true, false, true, false] := rfl

/-- Out-of-range variables are invalid even in a well-typed program. -/
theorem variable_count_enforced :
    ({ variableCount := 1,
       program := [.variable 1, .natural [], .equalTerms] } : RealSyntax.Instance).valid = false := rfl

theorem malformed_coefficient_digit : RealSyntax.decodeInstruction (1,[0,2,1]) = none := rfl

theorem malformed_typed_stack :
    RealSyntax.assemble [.verum, .natural [true], .equalTerms] = none := rfl

theorem unused_stack_rejected : RealSyntax.assemble [.verum,.verum] = none := rfl

theorem leading_coefficient_zero_preserves_value :
    Transducers.binaryMagnitude [false,true,false] = 2 := rfl

end InclusionBench.IndependentClassicalReview

