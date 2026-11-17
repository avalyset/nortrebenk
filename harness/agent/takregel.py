"""Regler for takene i en agentkjøring (NTB-0014, endret 17.11.2026). Rene funksjoner, brukt av kjor_agent.kjør() og
testet i tests/test_kjor_p3.py uten Docker."""


def tak_slo_inn(subtype, utgangskode, veggtid_s, tidsgrense):
    """(budsjettak, tidstak). Budsjettaket: resultatlinjens subtype nevner budget. Tidstaket: timeout ga utgangskode 124,
    eller veggtiden nådde tidsgrensen."""
    return bool(subtype and "budget" in str(subtype)), "124" in (utgangskode or "") or veggtid_s >= tidsgrense


def kostnad(total_cost_usd, tidstak, budsjett_usd):
    """(kostnad, kostnad_satt_til_tak). Stoppet tidstaket kjøringen før Claude Code oppga kostnad, føres budsjettaket."""
    if tidstak and total_cost_usd is None:
        return float(budsjett_usd), True
    return total_cost_usd, False


def loest(loest_for_takregel, budsjettak, tidstak):
    """En kjøring der et tak slo inn, er ikke løst uansett hva testene gir."""
    return bool(loest_for_takregel) and not (budsjettak or tidstak)
