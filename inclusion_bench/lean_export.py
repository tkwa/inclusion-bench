"""Render a real closure trace as a conditional Lean theorem.

Only cited leaves, cited rules and complement equalities become hypotheses.
Structural inference steps are proved, not passed in as assumptions.
"""

from .engine import Atom, InvalidEvidence


def proposition(atom: Atom) -> str:
    if atom.relation == "independence":
        raise InvalidEvidence("ZFC metatheorems use the separate Lean independence interface")
    kind = "Includes" if atom.relation == "inclusion" else "NonIncludes"
    return f"{kind} (model .{atom.left}) (model .{atom.right})"


def export_theorem(benchmark, closure, target: Atom, theorem_name="exportedConsequence") -> str:
    if not theorem_name.isidentifier() or not theorem_name.isascii():
        raise InvalidEvidence("The theorem name must be an ASCII identifier")
    steps = closure.explanation(target)["steps"]
    rule_by_id = {r.id: r for r in benchmark.rules}
    hypotheses = []
    assumptions = {}
    rule_names = {}
    complement_names = {}
    for step in steps:
        reason = step["reason"]
        atom = Atom.read(step)
        if reason.startswith("baseline:") or reason == "submission":
            name = f"leaf{len(assumptions)}"
            assumptions[step["id"]] = name
            hypotheses.append(f"    ({name} : {proposition(atom)})")
        elif reason == "complement":
            original = next(s for s in steps if s["id"] == step["parents"][0])
            for name in (original["left"], original["right"]):
                if name not in complement_names:
                    hn = f"dual{len(complement_names)}"
                    complement_names[name] = hn
                    hypotheses.append(f"    ({hn} : model .{benchmark.complements[name]} = coClass (model .{name}))")
        elif reason.removesuffix(":contrapositive") in rule_by_id:
            rid = reason.removesuffix(":contrapositive")
            if rid not in rule_names:
                rule = rule_by_id[rid]
                name = f"citedRule{len(rule_names)}"
                rule_names[rid] = name
                chain = " → ".join(f"({proposition(p)})" for p in (*rule.premises, rule.conclusion))
                hypotheses.append(f"    ({name} : {chain})")

    lines = ["import InclusionBench.Catalog", "", "namespace InclusionBench", "",
             f"-- Dataset SHA-256: {benchmark.digest}",
             "-- This theorem is conditional on its visible hypotheses.",
             "-- It verifies inference, not the submitted result or the historical literature.",
             f"theorem {theorem_name} (model : Interpretation ClassId)", *hypotheses,
             f"    : {proposition(target)} := by", "  classical"]
    names = {}
    atoms = {s["id"]: Atom.read(s) for s in steps}
    for i, step in enumerate(steps):
        name = f"step{i}"
        atom = atoms[step["id"]]
        names[step["id"]] = name
        parents = [names[p] for p in step["parents"]]
        reason = step["reason"]
        intro = f"  have {name} : {proposition(atom)} := "
        if step["id"] in assumptions:
            lines.append(intro + assumptions[step["id"]])
        elif reason == "reflexivity":
            lines.append(intro + "includes_refl _")
        elif reason == "transitivity":
            lines.append(intro + f"includes_trans {parents[0]} {parents[1]}")
        elif reason == "separation-left":
            lines.append(intro + f"nonincludes_expand {parents[0]} {parents[1]} (includes_refl _)")
        elif reason == "separation-right":
            lines.append(intro + f"nonincludes_expand {parents[0]} (includes_refl _) {parents[1]}")
        elif reason == "complement":
            original = atoms[step["parents"][0]]
            theorem = "includes_complement" if atom.relation == "inclusion" else "nonincludes_complement"
            transport = "includes_cast" if atom.relation == "inclusion" else "nonincludes_cast"
            lines.append(intro + f"{transport} ({theorem} {parents[0]}) {complement_names[original.left]} {complement_names[original.right]}")
        elif reason in rule_by_id:
            lines.append(intro + " ".join([rule_names[reason], *parents]))
        elif reason.endswith(":contrapositive"):
            rid = reason.removesuffix(":contrapositive")
            rule = rule_by_id[rid]
            missing = atom.opposite()
            args = ["missingPremise" if p == missing else names[p.key] for p in rule.premises]
            application = " ".join([rule_names[rid], *args])
            negative_conclusion = names[rule.conclusion.opposite().key]
            lines += [intro + "by", "    intro missingPremise" if atom.relation == "separation" else "    apply Classical.byContradiction\n    intro missingPremise"]
            contradiction = f"{negative_conclusion} ({application})" if rule.conclusion.relation == "inclusion" else f"({application}) {negative_conclusion}"
            lines.append("    exact " + contradiction)
        else:
            raise InvalidEvidence(f"No Lean export handler for {reason}")
    lines += [f"  exact {names[target.key]}", "", f"#print axioms {theorem_name}", "", "end InclusionBench", ""]
    return "\n".join(lines)
