import itertools
import unittest

from inclusion_bench.engine import Atom, Closure, Contradiction, InvalidEvidence, Rule


def inc(a, b):
    return Atom("inclusion", a, b)


def sep(a, b):
    return Atom("separation", a, b)


class ClosureTests(unittest.TestCase):
    def test_separation_propagates_outward_not_inward(self):
        c = Closure(["A", "B", "C", "D"])
        for a in [sep("A", "B"), inc("A", "C"), inc("D", "B")]:
            c.add(a, "assumed")
        c.saturate()
        self.assertIn(sep("C", "D"), c.proofs)
        self.assertNotIn(sep("D", "C"), c.proofs)

    def test_multi_premise_contraposition(self):
        rule = Rule("collapse", (inc("A", "B"), inc("B", "C")), inc("D", "E"))
        c = Closure("ABCDE", [rule])
        c.add(inc("A", "B"), "assumed")
        c.add(sep("D", "E"), "assumed")
        c.saturate()
        self.assertIn(sep("B", "C"), c.proofs)

    def test_independence_is_not_a_negative_edge(self):
        c = Closure("ABC")
        c.add(Atom("independence", "A", "B"), "assumed-metatheorem")
        c.add(inc("B", "C"), "assumed")
        c.saturate()
        self.assertNotIn(Atom("independence", "A", "C"), c.proofs)
        self.assertNotIn(sep("A", "B"), c.proofs)

    def test_incompatible_resolution_rejected(self):
        c = Closure("AB")
        c.add(inc("A", "B"), "assumed")
        with self.assertRaises(Contradiction):
            c.add(sep("A", "B"), "assumed")
        with self.assertRaises(Contradiction):
            c.add(Atom("independence", "A", "B"), "assumed")

    def test_reflexive_separation_rejected(self):
        c = Closure(["A"])
        c.add(sep("A", "A"), "assumed")
        with self.assertRaises(Contradiction):
            c.saturate()

    def test_unknown_classes_and_relations_rejected(self):
        c = Closure(["P", "NP"])
        with self.assertRaises(InvalidEvidence):
            c.add(inc("P", "NPP"), "typo")
        with self.assertRaises(InvalidEvidence):
            Atom("strict", "P", "NP")

    def test_independence_forbidden_in_horn_rules(self):
        with self.assertRaises(InvalidEvidence):
            Closure("AB", [Rule("bad", (), Atom("independence", "A", "B"))])

    def test_bad_complement_map_rejected(self):
        with self.assertRaises(InvalidEvidence):
            Closure("ABC", complements={"A": "B", "B": "C"})

    def test_complement_preserves_direction_and_sign(self):
        c = Closure("ABab", complements={"A": "a", "a": "A", "B": "b", "b": "B"})
        c.add(sep("A", "B"), "assumed")
        c.saturate()
        self.assertIn(sep("a", "b"), c.proofs)
        self.assertNotIn(sep("b", "a"), c.proofs)

    def test_generic_closure_sound_in_every_small_set_model(self):
        # 64 independently specified interpretations; seed subsets, not all truths.
        sets = [set(), {0}, {1}, {0, 1}]
        for values in itertools.product(sets, repeat=3):
            model = dict(zip("ABC", values))
            truths = [inc(a, b) if model[a] <= model[b] else sep(a, b) for a in "ABC" for b in "ABC"]
            for offset in range(3):
                c = Closure("ABC")
                for atom in truths[offset::3]:
                    c.add(atom, "finite-model")
                c.saturate()
                for atom in c.proofs:
                    self.assertEqual(model[atom.left] <= model[atom.right], atom.relation == "inclusion")

    def test_explanation_is_topologically_ordered(self):
        c = Closure("ABC")
        c.add(inc("A", "B"), "first")
        c.add(inc("B", "C"), "second")
        c.saturate()
        seen = set()
        for step in c.explanation(inc("A", "C"))["steps"]:
            self.assertTrue(set(step["parents"]) <= seen)
            seen.add(step["id"])


if __name__ == "__main__":
    unittest.main()
