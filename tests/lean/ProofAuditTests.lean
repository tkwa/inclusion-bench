import ProofAudit

open Lean InclusionProofcheck

namespace ProofAuditTests

def check (condition : Bool) (message : String) : IO Unit :=
  unless condition do throw (IO.userError message)

def unwrap (value : Except String α) : IO α :=
  match value with
  | .ok result => pure result
  | .error message => throw (IO.userError message)

def definition (name : Name) (value : Expr) : ConstantInfo :=
  .defnInfo {
    name, levelParams := [], type := .sort .zero, value := value,
    hints := .regular 0, safety := .safe}

def literature (type : Expr) : ConstantInfo :=
  .axiomInfo {name := `Literature.fact, levelParams := [], type, isUnsafe := false}

def theoremInfo (type value : Expr) : ConstantInfo :=
  .thmInfo {name := `Submission.result_1, levelParams := [], type, value}

def manifest (name : String := "Literature.fact") : Json :=
  Json.mkObj [("requests", array [Json.mkObj [("name", tag name)]])]

def encode (infos : List ConstantInfo) : IO (Array Json) := do
  return (← unwrap (infos.mapM encodeExportDeclaration)).toArray

def runCase (declarations : Array Json) (request? : Option Json := none)
    (version : Nat := 3) : IO Json := do
  IO.FS.writeFile "audit-payload.json" <| (Json.mkObj [
    ("schema_version", nat version), ("declarations", .arr declarations)]).compress
  IO.FS.writeFile "audit-targets.json" <| (array [Json.mkObj [
    ("theorem", tag "Submission.result_1"),
    ("expected", tag "InclusionBench.TrustedBaseline.expected_0")]]).compress
  if let some request := request? then
    IO.FS.writeFile "audit-literature.json" request.compress
    runAudit "audit-payload.json" "audit-targets.json" (some "audit-literature.json")
  else
    runAudit "audit-payload.json" "audit-targets.json"

def rejected (action : IO Json) (expected : String) : IO Unit := do
  let error? ← try
    let _ ← action
    pure none
  catch error => pure (some error.toString)
  match error? with
  | none => throw (IO.userError s!"Audit unexpectedly succeeded; expected {expected}")
  | some error => check ((error.splitOn expected).length > 1) s!"Wrong audit rejection: {error}"

def records (report : Json) : IO (Array Json) := do
  unwrap ((← unwrap (report.getObjVal? "literature_dependencies")).getArr?)

def checkConditional (report : Json) : IO Unit := do
  check ((← unwrap (report.getObjValAs? String "status")) == "needs_literature_review")
    "A literature assumption was reported as finally verified"
  check ((← unwrap (report.getObjValAs? String "kernel_status")) == "verified")
    "Conditional report did not record successful kernel replay"

def run : IO Unit := do
  let trueType := mkConst ``True
  let normal ← encode [theoremInfo trueType (mkConst ``True.intro)]
  let normalReport ← runCase normal
  check ((← unwrap (normalReport.getObjValAs? String "status")) == "verified")
    "An unconditional theorem requires literature review"
  check (← records normalReport |>.map Array.isEmpty) "Unconditional theorem has literature records"

  let base := definition `Submission.base trueType
  let predicate := definition `Submission.predicate (mkConst `Submission.base)
  let assumption := literature (mkConst `Submission.predicate)
  let conditional ← encode [base, predicate, assumption,
    theoremInfo (mkConst `Submission.predicate) (mkConst `Literature.fact)]
  let report ← runCase conditional (some (manifest))
  checkConditional report
  let dependencies ← records report
  check (dependencies.size == 1) "Wrong number of reconstructed literature declarations"
  let record := dependencies[0]!
  check ((← unwrap (record.getObjValAs? String "name")) == "Literature.fact") "Wrong reported axiom"
  check ((← unwrap (record.getObjVal? "declaration")).compress == conditional[2]!.compress)
    "Reported declaration differs from the kernel-reconstructed payload"
  let context ← unwrap ((← unwrap (record.getObjVal? "context")).getArr?)
  check (context.map Json.compress == #[conditional[0]!.compress, conditional[1]!.compress])
    "Literature context omitted a definition or changed dependency order"
  check (!(← unwrap (record.getObjValAs? String "statement")).isEmpty)
    "The actual reconstructed statement was not printed"

  rejected (runCase conditional) "Unrequested literature axiom"
  rejected (runCase conditional (some (manifest "Literature.other"))) "Unrequested literature axiom"
  rejected (runCase conditional (some (manifest "Other.fact"))) "Invalid literature request name"
  rejected (runCase conditional (some (manifest)) 2) "New axiom is forbidden"
  let names ← unwrap ((← unwrap (conditional[2]!.getObjVal? "names")).getArr?)
  let arbitrary := conditional[2]!.setObjVal! "name" (nat names.size) |>.setObjVal! "names"
    (.arr (names.push (array [tag "s", nat 0, tag "ArbitraryAxiom"])))
  rejected (runCase #[conditional[0]!, conditional[1]!, arbitrary]
    (some (manifest))) "New axiom is forbidden"

  let malformed ← encode [literature (mkNatLit 0)]
  rejected (runCase malformed (some (manifest))) "Kernel rejected declaration"
  let wrongProof ← encode [theoremInfo (mkConst ``False) (mkConst ``True.intro)]
  rejected (runCase wrongProof) "Kernel rejected declaration"
  let reserved ← encode [definition `InclusionBench.TrustedBaseline.forged trueType]
  rejected (runCase reserved) "Reserved baseline namespace"

  -- The exact axiom syntax is unchanged when a local predicate changes.
  -- Its context must change, even if the target uses an unrelated valid proof.
  let changed ← encode [definition `Submission.base (mkConst ``False), predicate,
    assumption, theoremInfo trueType (mkConst ``True.intro)]
  let changedReport ← runCase changed (some (manifest))
  checkConditional changedReport
  let changedRecord := (← records changedReport)[0]!
  check ((← unwrap (changedRecord.getObjVal? "declaration")).compress ==
    (← unwrap (record.getObjVal? "declaration")).compress) "Context test changed the axiom itself"
  check ((← unwrap (changedRecord.getObjVal? "context")).compress !=
    (← unwrap (record.getObjVal? "context")).compress) "A changed local definition escaped context binding"
  let novelProof ← encode [base, predicate, assumption,
    theoremInfo trueType (mkConst ``True.intro)]
  let novelRecord := (← records (← runCase novelProof (some (manifest))))[0]!
  check ((← unwrap (novelRecord.getObjVal? "context")).compress ==
    (← unwrap (record.getObjVal? "context")).compress) "Novel proof bodies contaminated literature context"

  -- Independent context branches have a stable order even when the input
  -- declaration array uses a different valid topological ordering.
  let first := definition `Submission.a trueType
  let last := definition `Submission.z trueType
  let pair := literature (mkApp2 (mkConst ``And) (mkConst `Submission.a) (mkConst `Submission.z))
  let ordered ← encode [first, last, pair, theoremInfo trueType (mkConst ``True.intro)]
  let reordered ← encode [last, first, pair, theoremInfo trueType (mkConst ``True.intro)]
  let orderedRecord := (← records (← runCase ordered (some (manifest))))[0]!
  let reorderedRecord := (← records (← runCase reordered (some (manifest))))[0]!
  check ((← unwrap (orderedRecord.getObjVal? "context")).compress ==
    (← unwrap (reorderedRecord.getObjVal? "context")).compress) "Context order depends on payload order"

  -- Literature axioms can themselves have literature-dependent types.
  -- Both axioms must be reported, and the type dependency must be bound.
  let carrier : ConstantInfo := .axiomInfo {
    name := `Literature.Carrier, levelParams := [], type := .sort (.succ .zero), isUnsafe := false}
  let inhabited := literature (mkApp (mkConst ``Nonempty [.succ .zero]) (mkConst `Literature.Carrier))
  let nested ← encode [carrier, inhabited, theoremInfo trueType (mkConst ``True.intro)]
  let nestedManifest := Json.mkObj [("requests", array [
    Json.mkObj [("name", tag "Literature.Carrier")], Json.mkObj [("name", tag "Literature.fact")]])]
  let nestedReport ← runCase nested (some nestedManifest)
  checkConditional nestedReport
  let nestedRecords ← records nestedReport
  check (nestedRecords.size == 2) "An axiom in another axiom's type escaped reporting"
  let nestedContext ← unwrap ((← unwrap (nestedRecords[1]!.getObjVal? "context")).getArr?)
  check (nestedContext.map Json.compress == #[nested[0]!.compress])
    "An axiom in a literature statement's type escaped context binding"
  IO.println "ProofAudit tests passed"

end ProofAuditTests

#eval ProofAuditTests.run
