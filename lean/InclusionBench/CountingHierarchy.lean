import InclusionBench.Counting
import InclusionBench.Oracles

/-!
# Oracle counting and the counting hierarchy

A query addresses one fixed language, independent of input length. Its bits
are written by the finite oracle machine in `Oracles.lean`; an oracle answer
is one Boolean, not the binary output of a counting function. Nondeterministic
paths retain their multiplicities, and every branch halts in polynomial time.

`PSharpP` is defined operationally as P^PP. Its standard equality with P^#P
uses polynomially many adaptive threshold queries; it does not identify one
#P query with one PP query. The function class #P is not an endpoint of the
language-class matrix. `CH` is the union over *fixed finite* hierarchy levels,
not a level that may grow with input length.
-/

namespace InclusionBench.CountingHierarchy

open Machines Counting Oracles

noncomputable def acceptingPathsFrom (machine : NOracleMachine) (oracle : Language)
    (word : Word) : Nat → OracleConfiguration machine.states → Nat
  | 0, config =>
      match machine.successors oracle word config with
      | [] => if machine.accept config.machine.state then 1 else 0
      | _ :: _ => 0
  | fuel + 1, config =>
      match machine.successors oracle word config with
      | [] => if machine.accept config.machine.state then 1 else 0
      | first :: rest =>
          acceptingPathsFrom machine oracle word fuel first +
            (rest.map (acceptingPathsFrom machine oracle word fuel)).sum

noncomputable def acceptingPaths (machine : NOracleMachine) (oracle : Language)
    (word : Word) (fuel : Nat) : Nat := acceptingPathsFrom machine oracle word fuel {}

def allBranchesHaltWithin (machine : NOracleMachine) (oracle : Language)
    (bound : Nat → Nat) : Prop :=
  ∀ word config, machine.reachable oracle word (bound word.length) config →
    machine.successors oracle word config = []

def SharpPWith (oracle : Language) (f : Word → Nat) : Prop :=
  ∃ machine : NOracleMachine, ∃ bound : Nat → Nat,
    polynomialBound bound ∧ allBranchesHaltWithin machine oracle bound ∧
    ∀ word, f word = acceptingPaths machine oracle word (bound word.length)

def GapPWith (oracle : Language) (g : Word → Int) : Prop :=
  ∃ positive negative : Word → Nat,
    SharpPWith oracle positive ∧ SharpPWith oracle negative ∧
    ∀ word, g word = (positive word : Int) - (negative word : Int)

def PPWith (oracle : Language) : ComplexityClass :=
  fun L => ∃ gap : Word → Int, GapPWith oracle gap ∧
    ∀ word, L word ↔ 0 < gap word

def PPOracle (oracleClass : ComplexityClass) : ComplexityClass :=
  fun L => ∃ oracle : Language, oracleClass oracle ∧ PPWith oracle L

/-- Decision problems solvable with polynomially many adaptive queries to
one PP language. The catalog label P^#P uses the standard P^#P=P^PP bridge. -/
def PSharpP : ComplexityClass := POracle PP

def countingLevel : Nat → ComplexityClass
  | 0 => polynomialTime
  | 1 => PP
  | level + 2 => PPOracle (countingLevel (level + 1))

def CH : ComplexityClass := fun L => ∃ level : Nat, countingLevel level L

theorem ppOracle_monotone {small large : ComplexityClass}
    (included : Includes small large) : Includes (PPOracle small) (PPOracle large) := by
  intro L ⟨oracle, member, decides⟩
  exact ⟨oracle, included oracle member, decides⟩

theorem pp_in_ch : Includes PP CH := fun _ member => ⟨1, member⟩

theorem p_in_ch : Includes polynomialTime CH := fun _ member => ⟨0, member⟩

theorem second_level_is_pp_oracle_pp : countingLevel 2 = PPOracle PP := rfl

theorem level_in_ch (level : Nat) : Includes (countingLevel level) CH :=
  fun _ member => ⟨level, member⟩

theorem gapPWith_negation {oracle : Language} {g : Word → Int}
    (hg : GapPWith oracle g) : GapPWith oracle (fun word => -g word) := by
  obtain ⟨positive, negative, hp, hn, value⟩ := hg
  refine ⟨negative, positive, hn, hp, ?_⟩
  intro word
  change -g word = _
  rw [value word]
  omega

theorem halted_branch_count (machine : NOracleMachine) (oracle : Language)
    (word : Word) (config : OracleConfiguration machine.states)
    (halted : machine.successors oracle word config = []) (fuel : Nat) :
    acceptingPathsFrom machine oracle word fuel config =
      if machine.accept config.machine.state then 1 else 0 := by
  cases fuel <;> simp [acceptingPathsFrom, halted]

/-- Duplicated nondeterministic actions count twice even with an oracle.
This example performs no query, so its count is oracle-independent. -/
def duplicateBranchMachine : NOracleMachine :=
  { states := 1
    transition := fun state _ _ _ =>
      if state.val = 0 then
        let action : OracleAction 1 := .compute
          { nextState := 1, write := none, inputMove := .stay, workMove := .stay }
          none .stay
        [action, action]
      else []
    accept := fun state => state.val == 1 }

theorem duplicate_branches_count_two (oracle : Language) :
    acceptingPaths duplicateBranchMachine oracle [] 1 = 2 := by
  rfl

end InclusionBench.CountingHierarchy
