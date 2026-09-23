import ProofExport

/- Run via tests/test_proofcodec.py with two separate depth arguments. -/

open Lean InclusionProofcheck

namespace ProofCodecTests

def check (condition : Bool) (message : String) : IO Unit :=
  unless condition do throw (IO.userError message)

def failed (value : Except ε α) : Bool := !value.isOk

def unwrap (value : Except String α) : IO α :=
  match value with
  | .ok result => pure result
  | .error message => throw (IO.userError message)

def theoremInfo (type value : Expr) : ConstantInfo :=
  .thmInfo {name := `Codec.example, levelParams := [`u], type, value}

def theoremValue (declaration : Declaration) : IO TheoremVal :=
  match declaration with
  | .thmDecl value => pure value
  | _ => throw (IO.userError "Expected a theorem declaration")

def roundtrip (type value : Expr) : IO Json := do
  let encoded ← unwrap (encodeDeclaration (theoremInfo type value))
  -- Exercise the actual serialized wire representation, too.
  let parsed ← unwrap (Json.parse encoded.compress)
  let result ← theoremValue (← unwrap (decodeDeclarationV2 parsed))
  check (result.name == `Codec.example && result.levelParams == [`u]) "Declaration names changed"
  check (Expr.equal result.type type) "Declaration type changed"
  check (Expr.equal result.value value) "Declaration body changed"
  return encoded

def testConstructors : IO Unit := do
  let level := Level.imax (.max (.succ .zero) (.param `u)) (.succ (.param `u))
  let type := Expr.sort level
  let constant := Expr.const (.num (.str .anonymous "Codec") 17) [level, .zero]
  let examples : List Expr := [
    .bvar 3, type, constant, .app constant type,
    .lam `x type (.bvar 0) .default,
    .forallE `x type (.bvar 0) .default,
    .letE `x type constant (.bvar 0) false,
    .lit (.natVal 123456789012345678901234567890),
    .lit (.strVal "quotes \" slash \\ newline\nλ"),
    .proj `Codec.Record 2 constant]
  for value in examples do
    let _ ← roundtrip type value
  -- Binder names are serialized, so alpha-equivalent nodes must not merge.
  let _ ← roundtrip type (.app (.lam `x type (.bvar 0) .default)
    (.lam `y type (.bvar 0) .default))
  pure ()

def testSharing : IO Unit := do
  let leaf := Expr.lit (.natVal 7)
  let mut doubled := leaf
  for _ in [:80] do
    doubled := .app doubled doubled
  let encoded ← unwrap (encodeDeclaration (theoremInfo doubled doubled))
  let nodes ← unwrap ((← unwrap (encoded.getObjVal? "expressions")).getArr?)
  check (nodes.size == 81) "A shared doubling DAG should have exactly 81 expression nodes"
  check (encoded.compress.utf8ByteSize < 10000) "A shared DAG expanded into a large JSON tree"
  IO.println s!"Shared doubling depth 80: {encoded.compress.utf8ByteSize} bytes, {nodes.size} expression nodes"
  let typeRoot ← unwrap (encoded.getObjValAs? Nat "type")
  let valueRoot ← unwrap (encoded.getObjValAs? Nat "value")
  check (typeRoot == valueRoot) "Type and value did not share the expression table"
  let result ← theoremValue (← unwrap (decodeDeclarationV2 encoded))
  -- Comparing the full expanded trees can itself cost exponential time.
  -- Walk one branch while confirming both edges reference the same subtree.
  let mut cursor := result.value
  for _ in [:80] do
    match cursor with
    | .app left right =>
        check (Expr.equal left right) "Shared child changed during decoding"
        cursor := left
    | _ => throw (IO.userError "Shared DAG lost an application node")
  check (Expr.equal cursor leaf) "Shared DAG lost its leaf"
  let separatelyBuilt := Expr.app (.lit (.natVal 19)) (.lit (.natVal 19))
  let separate ← unwrap (encodeDeclaration (theoremInfo separatelyBuilt separatelyBuilt))
  let separateNodes ← unwrap ((← unwrap (separate.getObjVal? "expressions")).getArr?)
  check (separateNodes.size == 2) "Structurally equal subexpressions were not deduplicated"
  let level := Level.max (.succ (.param `u)) (.succ (.param `u))
  let levelEncoded ← roundtrip (.sort level) (.sort level)
  let levelNodes ← unwrap ((← unwrap (levelEncoded.getObjVal? "universes")).getArr?)
  check (levelNodes.size == 3) "Shared universes were not deduplicated"
  let nameNodes ← unwrap ((← unwrap (levelEncoded.getObjVal? "names")).getArr?)
  check (nameNodes.size == 4) "Shared names were not deduplicated"

def testBoundedCompression : IO Unit := do
  -- Keep the legacy fixture shallow: its size grows exponentially.
  let mut doubled := Expr.lit (.natVal 7)
  for _ in [:18] do
    doubled := .app doubled doubled
  let info := theoremInfo doubled doubled
  let legacy ← unwrap (encodeDeclarationV1 info)
  let modern ← unwrap (encodeDeclaration info)
  let oldSize := legacy.compress.utf8ByteSize
  let newSize := modern.compress.utf8ByteSize
  check (newSize * 100 < oldSize) "DAG encoding did not remove repeated tree expansion"
  IO.println s!"Shared doubling depth 18: v1 {oldSize} bytes, v2 {newSize} bytes"

def doubledExpr (depth : Nat) : Expr := Id.run do
  let mut value := Expr.lit (.natVal 7)
  for _ in [:depth] do
    value := .app value value
  return value

def doubledLevel (depth : Nat) : Level := Id.run do
  let mut value := Level.param `u
  for _ in [:depth] do
    value := .max value value
  return value

def testIndependentDags (arguments : List String) : IO Unit := do
  let [leftText, rightText] := arguments
    | throw (IO.userError "Expected two independently supplied DAG depths: 80 80")
  let leftDepth := leftText.toNat!
  let rightDepth := rightText.toNat!
  check (leftDepth == 80 && rightDepth == 80) "Expected DAG depths 80 80"
  -- Parse distinct command-line inputs so compiler CSE cannot turn these two
  -- independent allocations into one shared object and hide slow equality.
  let expressionInfo := theoremInfo (doubledExpr leftDepth) (doubledExpr rightDepth)
  let expressions ← unwrap (encodeDeclaration expressionInfo)
  let nodes ← unwrap ((← unwrap (expressions.getObjVal? "expressions")).getArr?)
  check (nodes.size == 81) "Independent equal expression DAGs did not merge"
  check ((← unwrap (expressions.getObjValAs? Nat "type")) ==
    (← unwrap (expressions.getObjValAs? Nat "value"))) "Independent expression roots differ"
  let levelInfo := theoremInfo (.sort (doubledLevel leftDepth)) (.sort (doubledLevel rightDepth))
  let levels ← unwrap (encodeDeclaration levelInfo)
  let universeNodes ← unwrap ((← unwrap (levels.getObjVal? "universes")).getArr?)
  let expressionNodes ← unwrap ((← unwrap (levels.getObjVal? "expressions")).getArr?)
  check (universeNodes.size == 81 && expressionNodes.size == 1)
    "Independent equal universe DAGs did not merge"

def testMetadataAndLegacy : IO Unit := do
  let body := Expr.lam `x (.sort .zero) (.bvar 0) .default
  let withMetadata := Expr.mdata {} (.app body (.mdata {} body))
  let normalized := Expr.app body body
  let encoded ← unwrap (encodeDeclaration (theoremInfo (.sort .zero) withMetadata))
  let result ← theoremValue (← unwrap (decodeDeclarationV2 encoded))
  check (Expr.equal result.value normalized) "Metadata was not stripped"
  let legacy ← unwrap (encodeDeclarationV1 (theoremInfo (.sort .zero) withMetadata))
  let oldResult ← theoremValue (← unwrap (decodeDeclaration legacy))
  check (Expr.equal oldResult.value normalized) "Legacy v1 roundtrip changed"
  check (Expr.equal oldResult.type result.type && oldResult.name == result.name)
    "The v1 and v2 declaration decoders disagree"

def testKernelReplay : IO Unit := do
  let env ← importModules #[{module := `Init}] {}
  let info : ConstantInfo := .thmInfo {
    name := `Codec.valid, levelParams := [], type := mkConst ``True, value := mkConst ``True.intro}
  let encoded ← unwrap (encodeDeclaration info)
  let decoded ← unwrap (decodeDeclarationV2 encoded)
  match env.addDeclCore 1000000 decoded none true with
  | .ok _ => pure ()
  | .error _ => throw (IO.userError "Kernel rejected a valid theorem after DAG roundtrip")
  let forged : ConstantInfo := .thmInfo {
    name := `Codec.forged, levelParams := [], type := mkConst ``False, value := mkConst ``True.intro}
  let encoded ← unwrap (encodeDeclaration forged)
  let decoded ← unwrap (decodeDeclarationV2 encoded)
  match env.addDeclCore 1000000 decoded none true with
  | .error _ => pure ()
  | .ok _ => throw (IO.userError "Kernel accepted a forged theorem after DAG roundtrip")

def testUnresolvedExport : IO Unit := do
  for value in [Expr.fvar ⟨`local⟩, Expr.mvar ⟨`pending⟩, Expr.sort (.mvar ⟨`universe⟩)] do
    match encodeDeclaration (theoremInfo (.sort .zero) value) with
    | .error _ => pure ()
    | .ok _ => throw (IO.userError "Exported an unresolved expression or universe")

def dag (names := array [array [tag "a"]])
    (universes := array [array [tag "z"]])
    (expressions := array [array [tag "n", nat 0]])
    (name := nat 0) (levels := array []) (type := nat 0) (value := nat 0)
    (kind := tag "theorem") : Json :=
  Json.mkObj [("kind", kind), ("names", names), ("universes", universes),
    ("expressions", expressions), ("name", name), ("levels", levels),
    ("type", type), ("value", value)]

def rejected (label : String) (payload : Json) : IO Unit :=
  match decodeDeclarationV2 payload with
  | .error _ => pure ()
  | .ok _ => throw (IO.userError s!"Accepted malformed payload: {label}")

def testInvalidReferences : IO Unit := do
  let _ ← unwrap (decodeDeclarationV2 (dag))
  let badNameNodes := [
    array [tag "s", nat 0, tag "self"],
    array [tag "n", nat 1, nat 2],
    array [tag "s", tag "0", tag "wrong type"],
    array [tag "s", nat 999, tag "outside table"]]
  for node in badNameNodes do
    rejected "name reference" (dag (names := array [node]))
  rejected "name forward reference" (dag (names := array [
    array [tag "s", nat 1, tag "later"], array [tag "a"]]))
  for node in [array [tag "s", nat 0], array [tag "m", nat 0, nat 1],
      array [tag "i", nat 4, nat 0], array [tag "p", nat 1],
      array [tag "s", tag "0"]] do
    rejected "universe reference" (dag (universes := array [node]))
  rejected "universe forward reference" (dag (universes := array [
    array [tag "s", nat 1], array [tag "z"]]))
  for node in [array [tag "a", nat 0, nat 0],
      array [tag "l", nat 0, nat 1, nat 0],
      array [tag "f", nat 0, nat 0, nat 1],
      array [tag "e", nat 0, nat 0, nat 0, nat 0],
      array [tag "p", nat 0, nat 0, nat 0],
      array [tag "s", nat 1], array [tag "c", nat 1, array []],
      array [tag "c", nat 0, array [nat 1]],
      array [tag "a", tag "0", nat 0]] do
    rejected "expression reference" (dag (expressions := array [node]))
  rejected "expression forward reference" (dag (expressions := array [
    array [tag "a", nat 1, nat 1], array [tag "n", nat 0]]))
  rejected "two-node expression cycle" (dag (expressions := array [
    array [tag "a", nat 1, nat 1], array [tag "a", nat 0, nat 0]]))
  rejected "declaration name reference" (dag (name := nat 1))
  rejected "declaration level name reference" (dag (levels := array [nat 1]))
  rejected "declaration type reference" (dag (type := nat 1))
  rejected "declaration value reference" (dag (value := nat 1))
  rejected "string root reference" (dag (type := tag "0"))
  rejected "negative root reference" (dag (type := toJson (-1 : Int)))
  rejected "huge root reference" (dag (value := nat 123456789012345678901234567890))

def testInvalidShapes : IO Unit := do
  for node in [array [], array [tag "a", nat 0], array [tag "s", nat 0],
      array [tag "n", nat 0, tag "wrong"], array [tag "unknown"], tag "a"] do
    rejected "name tag, arity, or value" (dag (names := array [node]))
  for node in [array [], array [tag "z", nat 0], array [tag "s"],
      array [tag "p"], array [tag "unknown"], tag "z"] do
    rejected "universe tag or arity" (dag (universes := array [node]))
  for node in [array [], array [tag "n"], array [tag "n", nat 0, nat 1],
      array [tag "t", nat 0], array [tag "b", tag "0"],
      array [tag "c", nat 0, nat 0], array [tag "unknown"], tag "n"] do
    rejected "expression tag, arity, or value" (dag (expressions := array [node]))
  rejected "names table shape" (dag (names := tag "not an array"))
  rejected "universes table shape" (dag (universes := tag "not an array"))
  rejected "expressions table shape" (dag (expressions := tag "not an array"))
  rejected "level roots shape" (dag (levels := nat 0))
  rejected "forbidden declaration kind" (dag (kind := tag "axiom"))
  rejected "invalid unreachable node" (dag (expressions := array [
    array [tag "n", nat 0], array [tag "invalid"]]))

def testLiteratureCodec : IO Unit := do
  let info : ConstantInfo := .axiomInfo {
    name := `Literature.example, levelParams := [`u], type := mkConst ``True, isUnsafe := false}
  check (encodeDeclaration info |> failed) "Default encoder accepted a literature axiom"
  check (encodeDeclarationV1 info |> failed) "Legacy encoder accepted a literature axiom"
  let encoded ← unwrap (encodeExportDeclaration info)
  check (failed (encoded.getObjVal? "value")) "Axiom wire payload contains a body"
  check (decodeDeclarationV2 encoded |> failed) "Version 2 accepted a literature axiom"
  let decoded ← unwrap (decodeDeclarationV3 (← unwrap (Json.parse encoded.compress)))
  let .axiomDecl value := decoded | throw (IO.userError "Version 3 lost the axiom kind")
  check (value.name == info.name && value.levelParams == [`u] &&
    Expr.equal value.type info.type && !value.isUnsafe) "Literature declaration changed"
  check (decodeDeclarationV3 (encoded.setObjVal! "value" (nat 0)) |> failed)
    "Accepted an axiom with a body"
  for name in [`Unauthorized, `Literature, `LiteratureForgery.example,
      Name.str .anonymous "Literature.example", `InclusionBench.TrustedBaseline.fake] do
    let forbidden : ConstantInfo := .axiomInfo {
      name, levelParams := [], type := mkConst ``True, isUnsafe := false}
    check (encodeExportDeclaration forbidden |> failed)
      s!"Exported an axiom outside the structured Literature namespace: {name}"
  -- Change only the declaration name; every table reference remains valid.
  let names ← unwrap ((← unwrap (encoded.getObjVal? "names")).getArr?)
  let forged := encoded.setObjVal! "name" (nat names.size) |>.setObjVal! "names"
    (.arr (names.push (array [tag "s", nat 0, tag "Unauthorized"])))
  check (decodeDeclarationV3 forged |> failed) "Decoded an unauthorized axiom namespace"
  let unsafeInfo : ConstantInfo := .axiomInfo {
    name := `Literature.unsafeExample, levelParams := [], type := mkConst ``True, isUnsafe := true}
  check (encodeExportDeclaration unsafeInfo |> failed) "Exported an unsafe literature axiom"
  let env ← importModules #[{module := `Init}] {}
  match env.addDeclCore 1000000 decoded none true with
  | .ok _ => pure ()
  | .error _ => throw (IO.userError "Kernel rejected a well-typed literature declaration")
  let invalid : ConstantInfo := .axiomInfo {
    name := `Literature.invalid, levelParams := [], type := mkNatLit 0, isUnsafe := false}
  let invalid ← unwrap (decodeDeclarationV3 (← unwrap (encodeExportDeclaration invalid)))
  match env.addDeclCore 1000000 invalid none true with
  | .error _ => pure ()
  | .ok _ => throw (IO.userError "Kernel accepted a literature declaration with a non-type")

def addTestDeclaration (env : Environment) (declaration : Declaration) : IO Environment := do
  match env.addDeclCore 1000000 declaration none true with
  | .ok next => return next
  | .error _ => throw (IO.userError "Failed to construct exporter test environment")

def testTargetClosure : IO Unit := do
  let mut env ← importModules #[{module := `Init}] {}
  env ← addTestDeclaration env (.axiomDecl {
    name := `Literature.used, levelParams := [], type := mkConst ``True, isUnsafe := false})
  env ← addTestDeclaration env (.axiomDecl {
    name := `UnusedForbidden, levelParams := [], type := mkConst ``False, isUnsafe := false})
  env ← addTestDeclaration env (.defnDecl {
    name := `unusedTactic, levelParams := [], type := mkConst ``Nat, value := mkNatLit 0,
    hints := .regular 0, safety := .unsafe})
  env ← addTestDeclaration env (.thmDecl {
    name := `Submission.result_1, levelParams := [], type := mkConst ``True,
    value := mkConst `Literature.used})
  let payload ← unwrap (exportDeclarationRoots env #[`Submission.result_1, `Submission.result_1])
  check ((← unwrap (payload.getObjValAs? Nat "schema_version")) == 3) "Wrong export version"
  let declarations ← unwrap ((← unwrap (payload.getObjVal? "declarations")).getArr?)
  check (declarations.size == 2) "Target closure included unrelated declarations or duplicate roots"
  let .axiomDecl dependency ← unwrap (decodeDeclarationV3 declarations[0]!)
    | throw (IO.userError "Dependency did not precede the target")
  check (dependency.name == `Literature.used) "Wrong literature dependency"
  let .thmDecl target ← unwrap (decodeDeclarationV3 declarations[1]!)
    | throw (IO.userError "Target was not exported")
  check (target.name == `Submission.result_1) "Wrong target"
  check (exportDeclarationRoots env #[`UnusedForbidden] |> failed)
    "Exported an arbitrary requested axiom"
  check (exportDeclarationRoots env #[`missingTarget] |> failed)
    "Exported a missing target"

end ProofCodecTests

def main (arguments : List String) : IO Unit := do
  ProofCodecTests.testConstructors
  ProofCodecTests.testSharing
  ProofCodecTests.testBoundedCompression
  ProofCodecTests.testIndependentDags arguments
  ProofCodecTests.testMetadataAndLegacy
  ProofCodecTests.testKernelReplay
  ProofCodecTests.testUnresolvedExport
  ProofCodecTests.testInvalidReferences
  ProofCodecTests.testInvalidShapes
  ProofCodecTests.testLiteratureCodec
  ProofCodecTests.testTargetClosure
  IO.println "ProofCodec tests passed"
