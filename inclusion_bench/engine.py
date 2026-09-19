"""Signed relation closure. This computes consequences; it does not verify proofs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class InvalidEvidence(ValueError):
    pass


class Contradiction(InvalidEvidence):
    pass


@dataclass(frozen=True, order=True)
class Atom:
    relation: str
    left: str
    right: str

    def __post_init__(self):
        if self.relation not in {"inclusion", "separation", "independence"}:
            raise InvalidEvidence(f"Unknown relation: {self.relation}")

    @classmethod
    def read(cls, value: dict) -> Atom:
        return cls(value["relation"], value["left"], value["right"])

    def json(self) -> dict:
        return {"relation": self.relation, "left": self.left, "right": self.right}

    def opposite(self) -> Atom:
        if self.relation == "independence":
            raise InvalidEvidence("Independence is a metatheorem, not a negative fact")
        return Atom("separation" if self.relation == "inclusion" else "inclusion", self.left, self.right)

    @property
    def pair(self) -> tuple[str, str]:
        return self.left, self.right

    @property
    def key(self) -> str:
        return f"{self.relation}:{self.left}:{self.right}"


@dataclass(frozen=True)
class Rule:
    id: str
    premises: tuple[Atom, ...]
    conclusion: Atom
    source_ids: tuple[str, ...] = ()


class Closure:
    """A deterministic finite proof DAG, including every derivation's premises."""

    def __init__(self, class_ids: Iterable[str], rules: Iterable[Rule] = (), complements: dict | None = None):
        self.classes = tuple(sorted(class_ids))
        self.class_set = set(self.classes)
        self.rules = tuple(rules)
        self.complements = complements or {}
        self.proofs: dict[Atom, dict] = {}
        for rule in self.rules:
            for atom in (*rule.premises, rule.conclusion):
                self.validate_atom(atom)
                if atom.relation == "independence":
                    raise InvalidEvidence("Independence cannot occur in ordinary Horn rules")
        for a, b in self.complements.items():
            if a not in self.class_set or b not in self.class_set or self.complements.get(b) != a:
                raise InvalidEvidence("Complement map must be an involution on known classes")

    def validate_atom(self, atom: Atom):
        if atom.left not in self.class_set or atom.right not in self.class_set:
            raise InvalidEvidence(f"Unknown class in {atom.key}")

    def add(self, atom: Atom, reason: str, parents: Iterable[Atom] = (), source_ids: Iterable[str] = ()) -> bool:
        self.validate_atom(atom)
        if atom in self.proofs:
            return False
        incompatible = [Atom(r, atom.left, atom.right) for r in ("inclusion", "separation", "independence") if r != atom.relation]
        for other in incompatible:
            if other in self.proofs:
                raise Contradiction(f"Conflicting resolutions: {atom.key} and {other.key}")
        parents = tuple(parents)
        if any(parent not in self.proofs for parent in parents):
            raise InvalidEvidence("A derivation references an unknown premise")
        self.proofs[atom] = {"reason": reason, "parents": [p.key for p in parents], "source_ids": list(source_ids)}
        return True

    def saturate(self) -> Closure:
        for name in self.classes:
            self.add(Atom("inclusion", name, name), "reflexivity")
        changed = True
        while changed:
            changed = False
            inc = {(a.left, a.right): a for a in self.proofs if a.relation == "inclusion"}
            sep = [a for a in self.proofs if a.relation == "separation"]
            predecessors = {b: [] for b in self.classes}
            successors = {a: [] for a in self.classes}
            for (a, b), atom in inc.items():
                predecessors[b].append((a, atom))
                successors[a].append((b, atom))
            for middle in self.classes:
                for a, first in predecessors[middle]:
                    for c, second in successors[middle]:
                        changed |= self.add(Atom("inclusion", a, c), "transitivity", (first, second))
            # A ⊄ B, A ⊆ C, D ⊆ B imply C ⊄ D (one endpoint per step).
            for witness in sep:
                for c, bound in successors[witness.left]:
                    changed |= self.add(Atom("separation", c, witness.right), "separation-left", (witness, bound))
                for d, bound in predecessors[witness.right]:
                    changed |= self.add(Atom("separation", witness.left, d), "separation-right", (witness, bound))
            for atom in list(self.proofs):
                if atom.relation != "independence" and atom.left in self.complements and atom.right in self.complements:
                    dual = Atom(atom.relation, self.complements[atom.left], self.complements[atom.right])
                    changed |= self.add(dual, "complement", (atom,))
            for rule in self.rules:
                if all(a in self.proofs for a in rule.premises):
                    changed |= self.add(rule.conclusion, rule.id, rule.premises, rule.source_ids)
                # Classical contraposition: all other premises and ¬conclusion imply ¬premise.
                neg = rule.conclusion.opposite()
                if neg in self.proofs:
                    for i, premise in enumerate(rule.premises):
                        others = rule.premises[:i] + rule.premises[i + 1:]
                        if all(a in self.proofs for a in others):
                            changed |= self.add(premise.opposite(), rule.id + ":contrapositive", (*others, neg), rule.source_ids)
        return self

    def explanation(self, atom: Atom) -> dict:
        if atom not in self.proofs:
            raise InvalidEvidence(f"Not derived: {atom.key}")
        by_key = {a.key: a for a in self.proofs}
        visited: set[str] = set()
        ordered = []

        def visit(a: Atom):
            if a.key in visited:
                return
            visited.add(a.key)
            for parent in self.proofs[a]["parents"]:
                visit(by_key[parent])
            ordered.append({"id": a.key, **a.json(), **self.proofs[a]})

        visit(atom)
        return {"target": atom.key, "steps": ordered}
