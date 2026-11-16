"""Tester for reglene i harness/agent/kjor_p3.py (NTB-0014). Ingen Docker og ingen modellkall.

    python -m unittest discover -s tests
"""
import collections
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "harness/agent"))
import kjor_p3 as k  # noqa: E402

IDER = [f"org__repo{i % 5}__{100 + i}" for i in range(21)]


class Rekkefølge(unittest.TestCase):
    def test_samme_frø_gir_samme_plan(self):
        self.assertEqual(k.plan(IDER), k.plan(list(reversed(IDER))))

    def test_pass_har_ulik_rekkefølge(self):
        p = k.plan(IDER)
        r = [[x["oppgave"] for x in p if x["pass"] == n][::4] for n in (1, 2, 3)]
        self.assertNotEqual(r[0], r[1]); self.assertNotEqual(r[1], r[2])

    def test_fire_kjøringer_per_oppgave_og_pass(self):
        p = k.plan(IDER)
        self.assertEqual(len(p), 3 * 84)
        c = collections.Counter((x["pass"], x["oppgave"]) for x in p)
        self.assertTrue(all(v == 4 for v in c.values()))
        komb = collections.Counter((x["pass"], x["oppgave"], x["tekstvariant"], x["arm"]) for x in p)
        self.assertTrue(all(v == 1 for v in komb.values()))

    def test_oppgavens_kjøringer_ligger_samlet(self):
        p = [x for x in k.plan(IDER) if x["pass"] == 1]
        for i in range(0, 84, 4):
            self.assertEqual(len({x["oppgave"] for x in p[i:i + 4]}), 1)

    def test_frøet_er_20261116_pluss_pass(self):
        import random
        rng = random.Random(20261116 + 2); ider = sorted(IDER); rng.shuffle(ider)
        self.assertEqual(k.oppgaverekkefølge(IDER, 2)[0], ider)

    def test_bare_utvidet_følger_samme_rekkefølge(self):
        full = [x for x in k.plan(IDER, (1,)) if x["tekstvariant"] == "utvidet"]
        utv = k.plan(IDER, (1,), ("utvidet",))
        self.assertEqual([(x["oppgave"], x["arm"]) for x in full], [(x["oppgave"], x["arm"]) for x in utv])


class Budsjett(unittest.TestCase):
    def test_budsjett_er_saldo_minus_5(self):
        self.assertAlmostEqual(k.budsjett(70.0), 65.0)

    def test_første_pass_krever_28_29(self):
        self.assertEqual(k.neste_pass(28.29, 0, []), "fullt")
        self.assertIsNone(k.neste_pass(28.28, 0, []))

    def test_nytt_fullt_pass_krever_1_5_ganger_dyreste(self):
        fullført = [{"kost": 10.0, "kost_utvidet": 5.0, "type": "fullt"}, {"kost": 12.0, "kost_utvidet": 6.0, "type": "fullt"}]
        self.assertEqual(k.neste_pass(60.0, 42.0, fullført), "fullt")  # igjen 18 = 1,5 × 12
        self.assertEqual(k.neste_pass(60.0, 42.01, fullført), "utvidet")  # igjen 17,99 < 18, men ≥ 1,5 × 6

    def test_bare_utvidet_og_stopp(self):
        fullført = [{"kost": 12.0, "kost_utvidet": 6.0, "type": "fullt"}]
        self.assertEqual(k.neste_pass(40.0, 31.0, fullført), "utvidet")  # igjen 9 = 1,5 × 6
        self.assertIsNone(k.neste_pass(40.0, 31.01, fullført))

    def test_høyst_tre_pass(self):
        fullført = [{"kost": 1.0, "kost_utvidet": 0.5, "type": "fullt"}] * 3
        self.assertIsNone(k.neste_pass(1000.0, 3.0, fullført))

    def test_kjøring_startes_ikke_over_budsjett(self):
        self.assertTrue(k.kan_starte_kjøring(10.0, 7.0, "claude-opus-5-5"))
        self.assertFalse(k.kan_starte_kjøring(10.0, 7.01, "claude-opus-5-5"))
        self.assertTrue(k.kan_starte_kjøring(10.0, 8.5, "claude-sonnet-5-5"))
        self.assertFalse(k.kan_starte_kjøring(10.0, 8.51, "claude-sonnet-5-5"))


class Infrastrukturfeil(unittest.TestCase):
    def test_ingen_resultatlinje_uten_tak(self):
        self.assertTrue(k.infrastrukturfeil({"subtype": None, "budsjettak_slo_inn": False, "tidstak_slo_inn": False}))
        self.assertTrue(k.infrastrukturfeil(None))

    def test_tidstak_er_ikke_infrastrukturfeil(self):
        self.assertFalse(k.infrastrukturfeil({"subtype": None, "budsjettak_slo_inn": False, "tidstak_slo_inn": True}))

    def test_budsjettak_er_ikke_infrastrukturfeil(self):
        self.assertFalse(k.infrastrukturfeil({"subtype": "error_max_budget_usd", "is_error": True,
                                              "budsjettak_slo_inn": True, "tidstak_slo_inn": False}))

    def test_api_feil(self):
        self.assertTrue(k.infrastrukturfeil({"subtype": "success", "is_error": True, "resultat_tekst": "API Error: 529 overloaded",
                                             "budsjettak_slo_inn": False, "tidstak_slo_inn": False}))

    def test_vanlig_kjøring(self):
        self.assertFalse(k.infrastrukturfeil({"subtype": "success", "is_error": False, "budsjettak_slo_inn": False,
                                              "tidstak_slo_inn": False, "loest": False}))


class Fullført(unittest.TestCase):
    def test_fullført_med_manglende(self):
        self.assertTrue(k.pass_fullført([1, 2, 3], {1: "gjennomfort", 2: "manglende", 3: "gjennomfort"}))

    def test_ikke_fullført_når_noe_mangler_utfall(self):
        self.assertFalse(k.pass_fullført([1, 2, 3], {1: "gjennomfort", 2: "gjennomfort"}))
        self.assertFalse(k.pass_fullført([1, 2], {1: "gjennomfort", 2: "forkastet"}))


class Sperre(unittest.TestCase):
    def test_sperre_uten_prereg_doi(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(k.Sperre):
                k.sperre(d)
            (pathlib.Path(d) / "PREREG_DOI.txt").write_text("10.5281/zenodo.0\n")
            k.sperre(d)

    def test_kjor_modus_nekter_i_repoet_nå(self):
        if (k.ROT / "PREREG_DOI.txt").exists():
            self.skipTest("PREREG_DOI.txt finnes")
        with self.assertRaises(k.Sperre):
            k.kjør_p3(100.0, pathlib.Path(tempfile.mkdtemp()))


if __name__ == "__main__":
    unittest.main()
