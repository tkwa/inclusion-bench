import Lean

/- A data-only bridge. The verifier never imports a submitted .olean file.
Names, levels and expressions are reconstructed with safe Lean constructors. -/
namespace InclusionProofcheck
open Lean

def array (xs : List Json) : Json := Json.arr xs.toArray
def tag (value : String) : Json := Json.str value
def nat (value : Nat) : Json := toJson value

def encodeName : Name → Json
  | .anonymous => array [tag "a"]
  | .str parent value => array [tag "s", encodeName parent, tag value]
  | .num parent value => array [tag "n", encodeName parent, nat value]

def requireSome {α : Type} (value : Option α) (message : String) : Except String α :=
  match value with | some value => .ok value | none => .error message

def item (json : Json) (index : Nat) : Except String Json := do
  let xs ← json.getArr?
  requireSome xs[index]? s!"Missing array item {index}"

partial def decodeName (json : Json) : Except String Name := do
  match ← (← item json 0).getStr? with
  | "a" => return .anonymous
  | "s" => return .str (← decodeName (← item json 1)) (← (← item json 2).getStr?)
  | "n" => return .num (← decodeName (← item json 1)) (← (← item json 2).getNat?)
  | _ => throw "Invalid name tag"

def encodeLevel : Level → Json
  | .zero => array [tag "z"]
  | .succ l => array [tag "s", encodeLevel l]
  | .max a b => array [tag "m", encodeLevel a, encodeLevel b]
  | .imax a b => array [tag "i", encodeLevel a, encodeLevel b]
  | .param name => array [tag "p", encodeName name]
  | .mvar _ => array [tag "invalid"]

partial def decodeLevel (json : Json) : Except String Level := do
  match ← (← item json 0).getStr? with
  | "z" => return .zero
  | "s" => return .succ (← decodeLevel (← item json 1))
  | "m" => return .max (← decodeLevel (← item json 1)) (← decodeLevel (← item json 2))
  | "i" => return .imax (← decodeLevel (← item json 1)) (← decodeLevel (← item json 2))
  | "p" => return .param (← decodeName (← item json 1))
  | _ => throw "Invalid or unresolved universe"

partial def encodeExpr : Expr → Json
  | .bvar index => array [tag "b", nat index]
  | .sort level => array [tag "s", encodeLevel level]
  | .const name levels => array [tag "c", encodeName name, array (levels.map encodeLevel)]
  | .app function argument => array [tag "a", encodeExpr function, encodeExpr argument]
  | .lam name type body _ => array [tag "l", encodeName name, encodeExpr type, encodeExpr body]
  | .forallE name type body _ => array [tag "f", encodeName name, encodeExpr type, encodeExpr body]
  | .letE name type value body _ =>
      array [tag "e", encodeName name, encodeExpr type, encodeExpr value, encodeExpr body]
  | .lit (.natVal value) => array [tag "n", nat value]
  | .lit (.strVal value) => array [tag "t", tag value]
  | .mdata _ body => encodeExpr body
  | .proj type index body => array [tag "p", encodeName type, nat index, encodeExpr body]
  | .fvar _ | .mvar _ => array [tag "invalid"]

partial def decodeExpr (json : Json) : Except String Expr := do
  match ← (← item json 0).getStr? with
  | "b" => return .bvar (← (← item json 1).getNat?)
  | "s" => return .sort (← decodeLevel (← item json 1))
  | "c" =>
      let name ← decodeName (← item json 1)
      let levels ← (← (← item json 2).getArr?).toList.mapM decodeLevel
      return .const name levels
  | "a" => return .app (← decodeExpr (← item json 1)) (← decodeExpr (← item json 2))
  | "l" => return .lam (← decodeName (← item json 1)) (← decodeExpr (← item json 2)) (← decodeExpr (← item json 3)) .default
  | "f" => return .forallE (← decodeName (← item json 1)) (← decodeExpr (← item json 2)) (← decodeExpr (← item json 3)) .default
  | "e" => return .letE (← decodeName (← item json 1)) (← decodeExpr (← item json 2)) (← decodeExpr (← item json 3)) (← decodeExpr (← item json 4)) false
  | "n" => return .lit (.natVal (← (← item json 1).getNat?))
  | "t" => return .lit (.strVal (← (← item json 1).getStr?))
  | "p" => return .proj (← decodeName (← item json 1)) (← (← item json 2).getNat?) (← decodeExpr (← item json 3))
  | _ => throw "Invalid or unresolved expression"

def encodeDeclarationV1 (info : ConstantInfo) : Except String Json := do
  if info.isUnsafe then throw s!"Unsafe declaration is unsupported: {info.name}"
  let kind ← match info with
    | .thmInfo _ => pure "theorem"
    | .defnInfo value =>
        if value.safety == .safe then pure "definition" else throw "Partial/unsafe definition"
    | .opaqueInfo _ => pure "opaque"
    | .axiomInfo _ => throw s!"New axiom is forbidden: {info.name}"
    | _ => throw s!"New inductive/constructor/recursor is unsupported: {info.name}"
  let value ← requireSome (info.value? (allowOpaque := true)) "Missing declaration body"
  return Json.mkObj [
    ("kind", tag kind), ("name", encodeName info.name),
    ("levels", array (info.levelParams.map encodeName)),
    ("type", encodeExpr info.type), ("value", encodeExpr value)]

def decodeDeclaration (json : Json) : Except String Declaration := do
  let kind ← json.getObjValAs? String "kind"
  let name ← decodeName (← json.getObjVal? "name")
  let levels ← (← (← json.getObjVal? "levels").getArr?).toList.mapM decodeName
  let type ← decodeExpr (← json.getObjVal? "type")
  let value ← decodeExpr (← json.getObjVal? "value")
  match kind with
  | "theorem" => return .thmDecl {name, levelParams := levels, type, value}
  | "definition" | "opaque" => return .defnDecl {
      name, levelParams := levels, type, value, hints := .regular 0, safety := .safe}
  | _ => throw "Only checked theorem and definition bodies are accepted"

/- Version 2 stores a declaration-local DAG. Children are interned before their
parents, and the type and value share the same tables. Source-expression
memoization happens before recursion so sharing is never expanded into a tree. -/
structure EncodeState where
  names : Array Json := #[]
  nameIds : Std.HashMap Name Nat := {}
  universes : Array Json := #[]
  universeIds : Std.HashMap Level Nat := {}
  expressions : Array Json := #[]
  expressionIds : ExprStructMap Nat := {}

abbrev EncodeM := StateT EncodeState (Except String)

partial def internName (name : Name) : EncodeM Nat := do
  if let some index := (← get).nameIds[name]? then return index
  let node ← match name with
    | .anonymous => pure (array [tag "a"])
    | .str parent value => do pure (array [tag "s", nat (← internName parent), tag value])
    | .num parent value => do pure (array [tag "n", nat (← internName parent), nat value])
  let index := (← get).names.size
  modify fun s => { s with names := s.names.push node, nameIds := s.nameIds.insert name index }
  return index

partial def internLevel (level : Level) : EncodeM Nat := do
  if let some index := (← get).universeIds[level]? then return index
  let node ← match level with
    | .zero => pure (array [tag "z"])
    | .succ l => do pure (array [tag "s", nat (← internLevel l)])
    | .max a b => do pure (array [tag "m", nat (← internLevel a), nat (← internLevel b)])
    | .imax a b => do pure (array [tag "i", nat (← internLevel a), nat (← internLevel b)])
    | .param name => do pure (array [tag "p", nat (← internName name)])
    | .mvar _ => throw "Unresolved universe"
  let index := (← get).universes.size
  modify fun s => { s with
    universes := s.universes.push node
    universeIds := s.universeIds.insert level index }
  return index

partial def internExpr (expr : Expr) : EncodeM Nat := do
  if let some index := (← get).expressionIds[ExprStructEq.mk expr]? then return index
  -- Metadata has no kernel meaning; remember its alias as well as the body.
  if let .mdata _ body := expr then
    let index ← internExpr body
    modify fun s => { s with expressionIds := s.expressionIds.insert ⟨expr⟩ index }
    return index
  let node ← match expr with
    | .bvar index => pure (array [tag "b", nat index])
    | .sort level => do pure (array [tag "s", nat (← internLevel level)])
    | .const name levels => do
        let name ← internName name
        let levels ← levels.mapM internLevel
        pure (array [tag "c", nat name, array (levels.map nat)])
    | .app function argument => do
        pure (array [tag "a", nat (← internExpr function), nat (← internExpr argument)])
    | .lam name type body _ => do
        pure (array [tag "l", nat (← internName name), nat (← internExpr type), nat (← internExpr body)])
    | .forallE name type body _ => do
        pure (array [tag "f", nat (← internName name), nat (← internExpr type), nat (← internExpr body)])
    | .letE name type value body _ => do
        pure (array [tag "e", nat (← internName name), nat (← internExpr type),
          nat (← internExpr value), nat (← internExpr body)])
    | .lit (.natVal value) => pure (array [tag "n", nat value])
    | .lit (.strVal value) => pure (array [tag "t", tag value])
    | .proj type index body => do
        pure (array [tag "p", nat (← internName type), nat index, nat (← internExpr body)])
    | .fvar _ | .mvar _ | .mdata .. => throw "Invalid or unresolved expression"
  let index := (← get).expressions.size
  modify fun s => { s with
    expressions := s.expressions.push node
    expressionIds := s.expressionIds.insert ⟨expr⟩ index }
  return index

def encodeDeclaration (info : ConstantInfo) : Except String Json := do
  -- Canonicalize separately allocated equal DAGs before hash-map equality.
  -- In particular, Level equality can otherwise rewalk an exponential tree.
  let info := Lean.ShareCommon.shareCommon info
  if info.isUnsafe then throw s!"Unsafe declaration is unsupported: {info.name}"
  let kind ← match info with
    | .thmInfo _ => pure "theorem"
    | .defnInfo value =>
        if value.safety == .safe then pure "definition" else throw "Partial/unsafe definition"
    | .opaqueInfo _ => pure "opaque"
    | .axiomInfo _ => throw s!"New axiom is forbidden: {info.name}"
    | _ => throw s!"New inductive/constructor/recursor is unsupported: {info.name}"
  let value ← requireSome (info.value? (allowOpaque := true)) "Missing declaration body"
  let (roots, tables) ← (do
    let name ← internName info.name
    let levels ← info.levelParams.mapM internName
    let type ← internExpr info.type
    let value ← internExpr value
    pure (name, levels, type, value) : EncodeM (Nat × List Nat × Nat × Nat)).run {}
  let (name, levels, type, value) := roots
  return Json.mkObj [
    ("kind", tag kind), ("name", nat name), ("levels", array (levels.map nat)),
    ("type", nat type), ("value", nat value), ("names", .arr tables.names),
    ("universes", .arr tables.universes), ("expressions", .arr tables.expressions)]

/-- Literature declarations are proposals for separate human review, never
automatically trusted proof evidence. Test the structured namespace, not a
string prefix that could also match `LiteratureForgery` or an escaped name. -/
def isLiteratureName (name : Name) : Bool :=
  (`Literature).isPrefixOf name && name != `Literature

/-- Version 3 extends the exporter only. Ordinary callers of
`encodeDeclaration` still cannot export any new axiom. -/
def encodeExportDeclaration (info : ConstantInfo) : Except String Json := do
  let .axiomInfo value := info | encodeDeclaration info
  if value.isUnsafe then throw s!"Unsafe declaration is unsupported: {value.name}"
  unless isLiteratureName value.name do throw s!"New axiom is forbidden: {value.name}"
  let value := Lean.ShareCommon.shareCommon value
  let (roots, tables) ← (do
    let name ← internName value.name
    let levels ← value.levelParams.mapM internName
    let type ← internExpr value.type
    pure (name, levels, type) : EncodeM (Nat × List Nat × Nat)).run {}
  let (name, levels, type) := roots
  return Json.mkObj [
    ("kind", tag "axiom"), ("name", nat name), ("levels", array (levels.map nat)),
    ("type", nat type), ("names", .arr tables.names),
    ("universes", .arr tables.universes), ("expressions", .arr tables.expressions)]

/-- References can only access nodes already constructed. In particular, no
self/forward references or cycles can be decoded, even in unused nodes. -/
def reference (table : Array α) (json : Json) (label : String) : Except String α := do
  let index ← json.getNat?
  requireSome table[index]? s!"Invalid {label} reference {index}"

def nodeTag (node : Json) : Except String String := do
  (← item node 0).getStr?

def arity (node : Json) (size : Nat) : Except String Unit := do
  unless (← node.getArr?).size == size do throw "Invalid node arity"

def decodeNameNode (names : Array Name) (node : Json) : Except String Name := do
  match ← nodeTag node with
  | "a" => arity node 1; return .anonymous
  | "s" =>
      arity node 3
      return .str (← reference names (← item node 1) "name") (← (← item node 2).getStr?)
  | "n" =>
      arity node 3
      return .num (← reference names (← item node 1) "name") (← (← item node 2).getNat?)
  | _ => throw "Invalid name tag"

def decodeLevelNode (names : Array Name) (levels : Array Level) (node : Json) : Except String Level := do
  match ← nodeTag node with
  | "z" => arity node 1; return .zero
  | "s" =>
      arity node 2
      return .succ (← reference levels (← item node 1) "universe")
  | "m" | "i" =>
      arity node 3
      let a ← reference levels (← item node 1) "universe"
      let b ← reference levels (← item node 2) "universe"
      return if (← nodeTag node) == "m" then .max a b else .imax a b
  | "p" =>
      arity node 2
      return .param (← reference names (← item node 1) "name")
  | _ => throw "Invalid or unresolved universe"

def decodeExprNode (names : Array Name) (levels : Array Level) (exprs : Array Expr)
    (node : Json) : Except String Expr := do
  match ← nodeTag node with
  | "b" => arity node 2; return .bvar (← (← item node 1).getNat?)
  | "s" => arity node 2; return .sort (← reference levels (← item node 1) "universe")
  | "c" =>
      arity node 3
      let name ← reference names (← item node 1) "name"
      let levels ← (← (← item node 2).getArr?).toList.mapM fun j => reference levels j "universe"
      return .const name levels
  | "a" =>
      arity node 3
      return .app (← reference exprs (← item node 1) "expression")
        (← reference exprs (← item node 2) "expression")
  | "l" | "f" =>
      arity node 4
      let name ← reference names (← item node 1) "name"
      let type ← reference exprs (← item node 2) "expression"
      let body ← reference exprs (← item node 3) "expression"
      return if (← nodeTag node) == "l" then .lam name type body .default
        else .forallE name type body .default
  | "e" =>
      arity node 5
      return .letE (← reference names (← item node 1) "name")
        (← reference exprs (← item node 2) "expression")
        (← reference exprs (← item node 3) "expression")
        (← reference exprs (← item node 4) "expression") false
  | "n" => arity node 2; return .lit (.natVal (← (← item node 1).getNat?))
  | "t" => arity node 2; return .lit (.strVal (← (← item node 1).getStr?))
  | "p" =>
      arity node 4
      return .proj (← reference names (← item node 1) "name") (← (← item node 2).getNat?)
        (← reference exprs (← item node 3) "expression")
  | _ => throw "Invalid or unresolved expression"

private def decodeDeclarationDAG (json : Json) (allowLiterature : Bool) : Except String Declaration := do
  let kind ← json.getObjValAs? String "kind"
  let mut names := #[]
  for node in ← (← json.getObjVal? "names").getArr? do
    names := names.push (← decodeNameNode names node)
  let mut universes := #[]
  for node in ← (← json.getObjVal? "universes").getArr? do
    universes := universes.push (← decodeLevelNode names universes node)
  let mut expressions := #[]
  for node in ← (← json.getObjVal? "expressions").getArr? do
    expressions := expressions.push (← decodeExprNode names universes expressions node)
  let name ← reference names (← json.getObjVal? "name") "name"
  let levels ← (← (← json.getObjVal? "levels").getArr?).toList.mapM fun j => reference names j "name"
  let type ← reference expressions (← json.getObjVal? "type") "expression"
  if kind == "axiom" then
    unless allowLiterature && isLiteratureName name do
      throw s!"New axiom is forbidden: {name}"
    if (json.getObjVal? "value").isOk then throw "Literature axioms must not contain a body"
    return .axiomDecl {name, levelParams := levels, type, isUnsafe := false}
  let value ← reference expressions (← json.getObjVal? "value") "expression"
  match kind with
  | "theorem" => return .thmDecl {name, levelParams := levels, type, value}
  | "definition" | "opaque" => return .defnDecl {
      name, levelParams := levels, type, value, hints := .regular 0, safety := .safe}
  | _ => throw "Only checked theorem and definition bodies are accepted"

def decodeDeclarationV2 (json : Json) : Except String Declaration :=
  decodeDeclarationDAG json false

/-- Decoding is not authorization: ProofAudit additionally requires an exact
request-manifest match and reports literature-dependent results as conditional. -/
def decodeDeclarationV3 (json : Json) : Except String Declaration :=
  decodeDeclarationDAG json true

end InclusionProofcheck
