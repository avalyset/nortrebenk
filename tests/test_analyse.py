"""Tester for analysis/analyse.py med oppdiktede kjøringsfiler der svaret er regnet for hånd.

    python -m unittest discover -s tests
"""
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "analysis"))
import analyse as an  # noqa: E402

S, O = "claude-sonnet-5-5", "claude-opus-5-5"


def kj(p, oppg, arm, løst, kost=0.1, tid=10.0, status="gjennomfort", variant="pr_tekst"):
    return {"pass": p, "nummer": 0, "oppgave": oppg, "tekstvariant": variant, "arm": arm, "status": status,
            "loest": løst, "total_cost_usd": kost, "veggtid_s": tid}


def sett_rad(oid, repo):
    org, r, pr = oid.split("__")
    return {"id": "nortrebenk__" + oid, "org": org, "repo": f"{org}/{r}", "pr": int(pr), "utfall_p23": "består",
            "tekstsprak": "norsk", "agentmarkor": "nei"}


class Hånd(unittest.TestCase):
    def setUp(self):
        self.d = pathlib.Path(tempfile.mkdtemp())
        (self.d / "data/kvalitet").mkdir(parents=True)
        ider = {"a__x__1": "a/x", "a__x__2": "a/x", "b__y__3": "b/y", "b__y__4": "b/y"}
        (self.d / "data/sett_v1.jsonl").write_text("".join(json.dumps(sett_rad(i, r)) + "\n" for i, r in ider.items()))
        tider = iter([10, 20, 30, 40, 50, 60, 70])
        rader = [
            # Sonnet, PR-tekst: oppgaveskår 0,5 / 1 / 0 / 1
            kj(1, "a__x__1", S, True, tid=next(tider)), kj(2, "a__x__1", S, False, tid=next(tider)),
            kj(1, "a__x__2", S, True, tid=next(tider)), kj(2, "a__x__2", S, True, tid=next(tider)),
            kj(1, "b__y__3", S, False, tid=next(tider)), kj(2, "b__y__3", S, False, tid=next(tider)),
            kj(1, "b__y__4", S, True, tid=next(tider)),
            # Opus, PR-tekst: 1 / 1 / 0,5 / 0
            kj(1, "a__x__1", O, True), kj(2, "a__x__1", O, True), kj(1, "a__x__2", O, True),
            kj(1, "b__y__3", O, True), kj(2, "b__y__3", O, False), kj(1, "b__y__4", O, False),
            # Forkastet forsøk og manglende kjøring (telles for seg)
            kj(1, "b__y__4", O, False, kost=0.05, status="forkastet"),
            {"pass": 2, "nummer": 9, "oppgave": "b__y__4", "tekstvariant": "pr_tekst", "arm": O, "status": "manglende", "grunn": "test"},
            # Ufullstendig pass 3: skal ikke telle i hovedtallene
            kj(3, "a__x__1", S, False), kj(3, "a__x__2", S, False),
        ]
        (self.d / "k.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rader))
        (self.d / "p.jsonl").write_text("".join(json.dumps(x) + "\n" for x in
                                                ({"pass": 1, "fullfort": True}, {"pass": 2, "fullfort": True}, {"pass": 3, "fullfort": False})))
        self.r = an.analyse(self.d / "k.jsonl", self.d / "p.jsonl", self.d / "data")

    def test_løst_andel_og_standardfeil(self):
        s = self.r["hovedtall"]["per_arm_og_variant"][f"{S}|pr_tekst"]
        self.assertAlmostEqual(s["loest_andel"], 0.625)          # (0,5 + 1 + 0 + 1) / 4
        self.assertAlmostEqual(s["se_per_oppgave"], 0.2394, places=4)   # sqrt(0,6875 / 3 / 4), likning (1)
        self.assertAlmostEqual(s["se_klynget_repo"], 0.1488, places=4)  # sqrt(0,0572917 - 0,5625/16), likning (4)
        self.assertEqual(s["intervall_per_oppgave"], [round(0.625 - 1.96 * 0.2393567, 4), round(0.625 + 1.96 * 0.2393567, 4)])

    def test_kostnad_per_løste_og_veggtid(self):
        s = self.r["hovedtall"]["per_arm_og_variant"][f"{S}|pr_tekst"]
        self.assertAlmostEqual(s["kostnad_per_loste_usd"], 0.175)    # 7 × 0,1 / 4
        self.assertEqual(s["veggtid_s"], {"median": 40, "q1": 25.0, "q3": 55.0})

    def test_parvis(self):
        p = self.r["hovedtall"]["parvise_differanser"]["opus_minus_sonnet|pr_tekst"]
        self.assertAlmostEqual(p["differanse"], 0.0)                 # 0,5 + 0 + 0,5 - 1
        self.assertAlmostEqual(p["se_per_oppgave"], 0.3536, places=4)    # sqrt(1,5 / 3 / 4), likning (7)
        self.assertAlmostEqual(p["se_klynget_repo"], 0.1768, places=4)   # sqrt(0,5^2 + 0,5^2) / 4, likning (8)
        self.assertEqual(p["merknad"], "beskrivende")

    def test_for_seg(self):
        f = self.r["for_seg"]
        self.assertEqual(f["forkastede_forsok"], {"antall": 1, "kostnad_usd": 0.05})
        self.assertEqual(len(f["manglende_kjoringer"]), 1)
        self.assertEqual(f["ufullstendige_pass"], [3])
        self.assertEqual(self.r["fullforte_pass"], [1, 2])

    def test_grense_om_få_klynger(self):
        self.assertTrue(any("klynger" in g for g in self.r["grenser"]))

    def test_inndeling_og_flagg(self):
        (self.d / "data/kvalitet/uavhengig_utvidet.jsonl").write_text(
            json.dumps({"id": "nortrebenk__b__y__3", "stemmer_for_utelukkelse": "ja"}) + "\n")
        r = an.analyse(self.d / "k.jsonl", self.d / "p.jsonl", self.d / "data")
        self.assertIn("ja", r["inndelt"]["flagget_uavhengig"])
        self.assertIn("a/x", r["inndelt"]["repo"])
        self.assertIsNotNone(r.get("hovedmaal_uten_flaggede"))


class Formler(unittest.TestCase):
    def test_klynget_lik_naiv_når_hver_oppgave_er_egen_klynge(self):
        s = [0.0, 1.0, 0.5, 0.25]
        self.assertAlmostEqual(an.se_klynget(s, [1, 2, 3, 4]), an.se_clt(s))

    def test_bernoulli(self):
        s = [1.0, 0.0, 1.0, 1.0]  # likning (1) med 1/(n-1): sqrt(0,75/3/4)
        self.assertAlmostEqual(an.se_clt(s), (0.75 / 3 / 4) ** 0.5)


if __name__ == "__main__":
    unittest.main()
