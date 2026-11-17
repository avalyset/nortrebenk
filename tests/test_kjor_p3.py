"""Tester for reglene i harness/agent/kjor_p3.py (NTB-0014). Ingen Docker og ingen modellkall.

    python -m unittest discover -s tests
"""
import collections
import json
import pathlib
import types
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "harness/agent"))
import kjor_p3 as k  # noqa: E402
import takregel  # noqa: E402

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

    def test_kjøringsfeil_uten_tak(self):
        self.assertTrue(k.infrastrukturfeil({"subtype": "error_during_execution", "is_error": False,
                                             "budsjettak_slo_inn": False, "tidstak_slo_inn": False}))
        self.assertFalse(k.infrastrukturfeil({"subtype": "error_during_execution", "is_error": True,
                                              "budsjettak_slo_inn": False, "tidstak_slo_inn": True}))

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


class Takregel(unittest.TestCase):
    """1a og 1b (NTB-0014, endret 17.11.2026)."""
    def test_tak_gir_ikke_løst(self):
        self.assertFalse(takregel.loest(True, True, False))
        self.assertFalse(takregel.loest(True, False, True))
        self.assertTrue(takregel.loest(True, False, False))
        self.assertFalse(takregel.loest(False, False, False))

    def test_hvilket_tak(self):
        self.assertEqual(takregel.tak_slo_inn("error_max_budget_usd", "1\n", 30.0, 2400), (True, False))
        self.assertEqual(takregel.tak_slo_inn(None, "124\n", 30.0, 25), (False, True))
        self.assertEqual(takregel.tak_slo_inn(None, "", 2400.3, 2400), (False, True))
        self.assertEqual(takregel.tak_slo_inn("success", "0\n", 59.3, 2400), (False, False))

    def test_kostnad_ved_tidstak(self):
        self.assertEqual(takregel.kostnad(None, True, "1.50"), (1.5, True))
        self.assertEqual(takregel.kostnad(0.31, True, "1.50"), (0.31, False))
        self.assertEqual(takregel.kostnad(None, False, "1.50"), (None, False))


class Terskel(unittest.TestCase):
    """1f: bare utvidet krever 1,5 × utvidet-delen av det dyreste fullførte passet."""
    def test_utvidet_del_av_dyreste_pass(self):
        fullført = [{"kost": 12.0, "kost_utvidet": 4.0, "type": "fullt"}, {"kost": 10.0, "kost_utvidet": 7.0, "type": "fullt"}]
        self.assertEqual(k.neste_pass(30.0, 24.0, fullført), "utvidet")  # igjen 6 = 1,5 × 4; 1,5 × 7 = 10,5 ville stoppet
        self.assertIsNone(k.neste_pass(30.0, 24.01, fullført))


class Diskport(unittest.TestCase):
    """1g: under 6 GiB etter opprydding stopper ikke kjøreren; oppgavens kjøringer blir manglende."""
    def setUp(self):
        self.lagret = (k.ledig_gib, k.rydd_egne)
        k.ledig_gib = lambda sti=None: 5.9
        k.rydd_egne = lambda: None

    def tearDown(self):
        k.ledig_gib, k.rydd_egne = self.lagret

    def test_diskport_gir_ikke_ok(self):
        self.assertEqual(k.diskport(), (False, 5.9))

    def test_forberedelse_returnerer_grunn(self):
        bygget = []
        falsk = types.SimpleNamespace(bygg_instans=lambda oid: bygget.append(oid) or (True, "x"))
        ok, steg = k.forberedelse(falsk, "a__b__1", False)
        self.assertFalse(ok); self.assertEqual(steg["grunn"], "under 6 GiB ledig"); self.assertEqual(bygget, [])

    def test_kontroll_modus_fortsetter(self):
        lagret = (k.forbered_oppgaver, k.ka, k.slett_bilder)
        k.forbered_oppgaver = lambda ut: None; k.ka = lambda ut, v="pr_tekst": None; k.slett_bilder = lambda kk, oid: None
        try:
            with tempfile.TemporaryDirectory() as d:
                fil = pathlib.Path(d) / "kontroll.jsonl"
                rader = k.kontroll_modus(["a__b__1", "a__b__2"], fil, pathlib.Path(d))
                self.assertEqual([r["grunn"] for r in rader], ["under 6 GiB ledig"] * 2)
                self.assertEqual(len(fil.read_text().splitlines()), 2)
        finally:
            k.forbered_oppgaver, k.ka, k.slett_bilder = lagret

    def test_kjor_løkke_fører_manglende(self):
        kall = []
        with Løkke(self, kjør=lambda oid, arm, tak: kall.append(oid), forberedelse=k.forberedelse) as l:
            k.kjør_løkke(l.ut, ["a__b__1", "a__b__2"], 50.0, ("pr_tekst",), 1)
            self.assertEqual(kall, [])
            rader = l.rader()
            self.assertEqual(len(rader), 4)
            self.assertTrue(all(r["status"] == "manglende" and r["grunn"] == "under 6 GiB ledig" for r in rader))
            self.assertTrue(l.pass_rader()[0]["fullfort"])


class Selvtestfeil(Exception):
    pass


def kjøring(kost=0.1, loest=True, **kw):
    return {"kjoring": "x", "total_cost_usd": kost, "subtype": "success", "is_error": False, "budsjettak_slo_inn": False,
            "tidstak_slo_inn": False, "loest": loest, **kw}


class Løkke:
    """Kjører kjor_p3.kjør_løkke med en falsk kjor_agent: ingen Docker og ingen modellkall."""
    def __init__(self, tc, kjør, forberedelse=None):
        self.tc, self.kjør, self.forb = tc, kjør, forberedelse

    def __enter__(self):
        self.d = tempfile.TemporaryDirectory(); self.ut = pathlib.Path(self.d.name)
        self.lagret = (k.ka, k.forberedelse, k.slett_bilder)
        modul = types.SimpleNamespace(nett=lambda: None, kjør=self.kjør, Selvtestfeil=Selvtestfeil)
        k.ka = lambda ut, v="pr_tekst": modul
        k.forberedelse = self.forb or (lambda kk, oid, t: (True, {}))
        k.slett_bilder = lambda kk, oid: None
        return self

    def __exit__(self, *a):
        k.ka, k.forberedelse, k.slett_bilder = self.lagret
        self.d.cleanup()

    def rader(self):
        return k.jl_om(self.ut / "p3_kjoringer.jsonl")

    def pass_rader(self):
        return k.jl_om(self.ut / "p3_pass.jsonl")


class Løkkeregler(unittest.TestCase):
    IDER = ["a__b__1", "a__b__2"]

    def test_selvtestfeil_to_ganger_gir_manglende_og_neste_oppgave(self):
        kall = []
        første = k.oppgaverekkefølge(self.IDER, 1)[0][0]
        def kjør(oid, arm, tak):
            kall.append(oid)
            if oid == første:
                raise Selvtestfeil()
            return kjøring()
        with Løkke(self, kjør) as l:
            k.kjør_løkke(l.ut, self.IDER, 50.0, ("pr_tekst",), 1)
            r = l.rader()
            self.assertEqual(kall.count(første), 2)  # selvtesten prøves én gang til
            mangl = [x for x in r if x["oppgave"] == første]
            self.assertEqual(len(mangl), 2)
            self.assertTrue(all(x["status"] == "manglende" and x["grunn"] == "selvtest feilet før kjøring" for x in mangl))
            self.assertEqual(sum(1 for x in r if x["status"] == "gjennomfort"), 2)
            self.assertTrue(l.pass_rader()[0]["fullfort"])

    def test_selvtestfeil_én_gang_kjører_videre(self):
        n = collections.Counter()
        def kjør(oid, arm, tak):
            n[(oid, arm)] += 1
            if n[(oid, arm)] == 1:
                raise Selvtestfeil()
            return kjøring()
        with Løkke(self, kjør) as l:
            k.kjør_løkke(l.ut, self.IDER, 50.0, ("pr_tekst",), 1)
            self.assertEqual(sum(1 for x in l.rader() if x["status"] == "gjennomfort"), 4)

    def test_budsjett_sjekkes_før_omkjøring(self):
        # B = 3,5: første forsøk kan starte i begge armer (tak 1,50 og 3,00); det forkastes og koster 2,1; omkjøringen
        # ville gitt 2,1 + taket > 3,5 og startes ikke. Passet er stoppet av budsjettet.
        def kjør(oid, arm, tak):
            return kjøring(kost=2.1, subtype=None, is_error=None)  # ingen resultatlinje, intet tak: infrastrukturfeil
        with Løkke(self, kjør) as l:
            k.FØRSTE_PASS_MIN, lagret = 0.0, k.FØRSTE_PASS_MIN
            try:
                k.kjør_løkke(l.ut, self.IDER, 3.5, ("pr_tekst",), 1)
            finally:
                k.FØRSTE_PASS_MIN = lagret
            r = l.rader()
            self.assertEqual([x["status"] for x in r], ["forkastet"])
            self.assertFalse(l.pass_rader()[0]["fullfort"])

    def test_infrastrukturfeil_tre_ganger(self):
        with Løkke(self, lambda oid, arm, tak: kjøring(kost=0.01, subtype=None)) as l:
            k.kjør_løkke(l.ut, self.IDER, 50.0, ("pr_tekst",), 1)
            r = l.rader()
            self.assertEqual(sum(1 for x in r if x["status"] == "forkastet"), 12)
            self.assertEqual(sum(1 for x in r if x["status"] == "manglende"), 4)
            self.assertTrue(l.pass_rader()[0]["fullfort"])


class Gjenopptak(unittest.TestCase):
    """1h."""
    IDER = ["a__b__1", "a__b__2"]

    def rad(self, x, status, kost=0.1, forsok=1):
        return {**x, "forsok": forsok, "status": status, "total_cost_usd": kost}

    def test_halvferdig_pass(self):
        plan = k.plan(self.IDER, (1,), ("pr_tekst",))
        rader = [self.rad(plan[0], "gjennomfort", 0.2), self.rad(plan[1], "forkastet", 0.05), self.rad(plan[2], "manglende", None)]
        st = k.gjenopptak(rader, [], self.IDER, 50.0, ("pr_tekst",), 1)
        self.assertEqual(st["pass"], 1); self.assertEqual(st["type"], "fullt")
        self.assertAlmostEqual(st["brukt"], 0.25)
        self.assertEqual(st["gjenstaende"], [plan[1], plan[3]])
        self.assertEqual(st["forkastet"][k.nøkkel(plan[1])], 1)

    def test_ferdig_pass_gir_ingenting_å_kjøre(self):
        plan = k.plan(self.IDER, (1,), ("pr_tekst",))
        rader = [self.rad(x, "gjennomfort", 0.1) for x in plan]
        st = k.gjenopptak(rader, [{"pass": 1, "type": "fullt", "fullfort": True, "kost": 0.4, "kost_utvidet": 0.0}],
                          self.IDER, 50.0, ("pr_tekst",), 1)
        self.assertIsNone(st["type"]); self.assertEqual(st["gjenstaende"], [])
        self.assertAlmostEqual(st["brukt"], 0.4)

    def test_neste_pass_etter_ferdig_pass(self):
        plan = k.plan(self.IDER, (1,))
        rader = [self.rad(x, "gjennomfort", 0.1) for x in plan]
        st = k.gjenopptak(rader, [{"pass": 1, "type": "fullt", "fullfort": True, "kost": 0.8, "kost_utvidet": 0.4}],
                          self.IDER, 50.0)
        self.assertEqual(st["pass"], 2); self.assertEqual(st["type"], "fullt"); self.assertEqual(len(st["gjenstaende"]), 8)

    def test_pass_stoppet_av_budsjett_nekter(self):
        with self.assertRaises(k.Sperre):
            k.gjenopptak([], [{"pass": 1, "type": "fullt", "fullfort": False, "kost": 1.0, "kost_utvidet": 0.5}], self.IDER, 50.0)

    def test_type_avgjøres_med_brukt_før_passet(self):
        # Pass 2 startet som fullt (igjen 20 ≥ 1,5 × 12); kjøringer i pass 2 endrer ikke typen ved omstart.
        p1 = [{"pass": 1, "type": "fullt", "fullfort": True, "kost": 12.0, "kost_utvidet": 6.0}]
        rader = [{"pass": 1, "oppgave": "x", "tekstvariant": "pr_tekst", "arm": "a", "status": "gjennomfort", "total_cost_usd": 12.0},
                 {**k.plan(self.IDER, (2,))[0], "status": "gjennomfort", "total_cost_usd": 5.0}]
        st = k.gjenopptak(rader, p1, self.IDER, 32.0)
        self.assertEqual(st["type"], "fullt"); self.assertAlmostEqual(st["brukt"], 17.0)

    def test_omstart_hopper_over_og_bruker_B_fra_start(self):
        kall = []
        with Løkke(self, lambda oid, arm, tak: kall.append((oid, arm)) or kjøring()) as l:
            plan = k.plan(self.IDER, (1,), ("pr_tekst",))
            (l.ut / "p3_kjoringer.jsonl").write_text(json.dumps(self.rad(plan[0], "gjennomfort", 0.3)) + "\n")
            B = k.start_budsjett(l.ut, 60.0)
            self.assertEqual(B, 55.0)
            self.assertEqual(k.start_budsjett(l.ut, 999.0), 55.0)
            k.kjør_løkke(l.ut, self.IDER, B, ("pr_tekst",), 1)
            self.assertEqual(len(kall), 3)
            self.assertNotIn((plan[0]["oppgave"], plan[0]["arm"]), kall)
            n = len(l.rader())
            k.kjør_løkke(l.ut, self.IDER, B, ("pr_tekst",), 1)  # andre start: ingenting igjen
            self.assertEqual(len(l.rader()), n); self.assertEqual(len(kall), 3)


class Prove(unittest.TestCase):
    """1i: prove nekter oppgaver i settet."""
    def test_nekter_oppgave_i_settet(self):
        r = k.jl(k.ROT / "data/sett_v1.jsonl")[0]
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "sett.jsonl"; f.write_text(json.dumps(r) + "\n")
            with self.assertRaises(k.Sperre):
                k.prøve(60.0, pathlib.Path(d), f, f)
            self.assertFalse((pathlib.Path(d) / "p3_start.json").exists())


if __name__ == "__main__":
    unittest.main()
