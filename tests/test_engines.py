import copy, datetime as dt, shutil, tempfile, unittest
from pathlib import Path
from earthlike import ROOT, assets, fans, memory, personas, tracker
from earthlike.canon import load_characters


class Sandbox(unittest.TestCase):
    """Run against a throwaway copy of the repo so tests never touch real memory/votes."""
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for d in ("canon", "storyboard"):
            shutil.copytree(ROOT / d, self.tmp / d)
        (self.tmp / "memory").mkdir()
        self.root = self.tmp
    def tearDown(self): shutil.rmtree(self.tmp)


class TrackerTests(Sandbox):
    def test_repo_tracker_is_valid(self):
        self.assertEqual(tracker.validate(tracker.load(), set(load_characters())), [])

    def test_validation_catches_problems(self):
        d = tracker.load(); d["beats"][2]["requires"] = ["nope"]; d["beats"][3]["characters"] = ["ghost"]
        d["beats"][0]["requires"] = ["ch02"]; d["beats"][1]["requires"] = ["ch01"]  # cycle
        errs = "\n".join(tracker.validate(d, set(load_characters())))
        self.assertIn("unknown beat", errs); self.assertIn("unknown character", errs); self.assertIn("cycle", errs)

    def test_release_respects_date(self):
        d = tracker.load(); b = d["beats"][0]; b["status"] = "released"; b["release_date"] = "2030-01-01"
        self.assertIn("ch01", tracker.released_ids(d, dt.date(2030, 1, 1)))
        self.assertNotIn("ch01", tracker.released_ids(d, dt.date(2029, 12, 31)))


class GateTests(Sandbox):
    def _release(self, beat):
        d = tracker.load(self.root)
        for b in d["beats"]:
            if b["id"] == beat: b["status"], b["release_date"] = "released", "2020-01-01"
        tracker.save(d, self.root)

    def test_unreleased_memory_and_facts_hidden(self):
        memory.add("emma-baptiste", "Found the orchard of identical trees", beat="ch12", root=self.root)
        memory.add("emma-baptiste", "Rich kissed my cheek after the talk", beat="ch01", root=self.root)
        memory.add("emma-baptiste", "I secretly doubt the data", public=False, root=self.root)
        p = personas.build_system_prompt("emma-baptiste", "orchard Rich doubt", root=self.root)
        self.assertNotIn("orchard", p.lower().split("rules")[0]); self.assertNotIn("doubt the data", p)
        self.assertIn("none yet", p)
        self._release("ch01")
        p = personas.build_system_prompt("emma-baptiste", "Rich cheek", root=self.root)
        self.assertIn("Rich kissed", p); self.assertIn("terra-found", p); self.assertNotIn("terra-was-seeded", p)

    def test_proposed_backstory_not_in_prompt(self):
        p = personas.build_system_prompt("emma-baptiste", root=self.root)
        self.assertNotIn("Louisiana", p)  # proposed text stays private until the author approves it
        self.assertIn("AI", p)  # disclosure present


class FanTests(Sandbox):
    def test_one_vote_per_fan_and_ledger(self):
        self.assertTrue(fans.cast_vote("B2", "fan1", "rich", self.root))
        self.assertFalse(fans.cast_vote("B2", "fan1", "sam", self.root))
        fans.cast_vote("B2", "fan2", "sam", self.root); fans.cast_vote("B2", "fan3", "sam", self.root)
        with self.assertRaises(ValueError): fans.cast_vote("B2", "fan4", "bogus", self.root)
        e = fans.close_branch("B2", self.root)
        self.assertEqual(e["winner"], "sam"); self.assertEqual(e["author_review"], "pending")

    def test_tie_goes_to_first_option(self):
        fans.cast_vote("B2", "a", "sam", self.root); fans.cast_vote("B2", "b", "rich", self.root)
        self.assertEqual(fans.close_branch("B2", self.root)["winner"], "rich")


class AssetTests(Sandbox):
    def test_asset_prompt(self):
        s = assets.build("portrait", "rich-baptiste", "hopeful", root=self.root)
        self.assertIn("mocha", s["prompt"]); self.assertEqual(s["status"], "needs-review")


if __name__ == "__main__":
    unittest.main()
