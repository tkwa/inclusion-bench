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

def encodeDeclaration (info : ConstantInfo) : Except String Json := do
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

end InclusionProofcheck
