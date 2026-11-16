"""Avhengighetscacher fra gulltilstanden (NTB-0006, NTB-0014).

For oppgaver med feltet `bygg` i data/sett_v1.jsonl (kafka-manager #330 og #336) må avhengighetene for tilstanden
med gullpatch ligge i den lokale cachen, ellers kan testene ikke kjøres uten nett. Bygget er flyttet hit fra
p24/scripts/b4_nett.py (P2.4, data/p24_nett.jsonl):

- Et eget byggesteg («gull») tar utgangspunkt i det ferdige bildet, legger på testpatch og gullpatch, kjører
  repo-definisjonens installasjon og oppvarming, og slettes etterpå. Bare cachemappene fra `bygg.cacher_fra_gulltilstand`
  kopieres videre til det endelige bildet. Repoet og alt annet kommer fra bildet uten gullpatch.
- `bygg.ekstra_miljo` (for #330: `ENV npm_config_prefer_offline=true`) legges til i det endelige bildet.

Instansbildet kjører som root, så cachene ligger under /root. Agentbildet kjører som brukeren `agent`, så de samme
cachene ligger under /home/agent. Oppgaver uten `bygg` bygges som før.
"""

GULL_KATALOG = "ntb_gull"


def _cache_kopier(cacher, rot_fra="/root/", rot_til="/root/", chown=None):
    ut = []
    for c in cacher:
        sti = rot_til + c[len(rot_fra):] if c.startswith(rot_fra) else c
        ut.append(f"COPY --from=gull{' --chown=' + chown if chown else ''} {sti} {sti}\n")
    return "".join(ut), [rot_til + c[len(rot_fra):] if c.startswith(rot_fra) else c for c in cacher]


def instans_dockerfile(img, bygg):
    """Dockerfile for instansbildet (harness/msb_repos/_felles.py, uendret) med cachene fra gulltilstanden."""
    import _felles
    d = img.dockerfile()
    deler = d.split(f"\nFROM {img.dependency()}\n{_felles.LABEL}\n", 1)
    assert len(deler) == 2, "uventet form på instansbildets Dockerfile"
    d = deler[0] + f"\nFROM {img.dependency()} AS inst\n{_felles.LABEL}\n" + deler[1]
    kopier, stier = _cache_kopier(bygg["cacher_fra_gulltilstand"])
    varm = img.spes.warm(img.pr)
    return d + f"""
FROM inst AS gull
WORKDIR /home/{img.pr.repo}
RUN git apply --whitespace=nowarn /home/test.patch /home/fix.patch && ({img.spes.installer}) && ({varm}); mkdir -p {' '.join(stier)}

FROM inst
WORKDIR /home/{img.pr.repo}
{kopier}{(bygg.get('ekstra_miljo') or '') + chr(10) if bygg.get('ekstra_miljo') else ''}"""


def agent_tillegg(repo, spes, pr, bygg):
    """Tillegg til agentbildets Dockerfile. Forutsetter at agentbildets siste steg heter `agentinst`.
    Gullpatchen og testpatchen ligger i byggekonteksten under ntb_gull/ og kopieres bare inn i steget «gull»."""
    kopier, stier = _cache_kopier(bygg["cacher_fra_gulltilstand"], "/root/", "/home/agent/", "agent:agent")
    return f"""
FROM agentinst AS gull
USER agent
WORKDIR /home/{repo}
COPY --chown=agent:agent {GULL_KATALOG}/ /tmp/{GULL_KATALOG}/
RUN git apply --whitespace=nowarn /tmp/{GULL_KATALOG}/test.patch /tmp/{GULL_KATALOG}/fix.patch && ({spes.installer}) && ({spes.warm(pr)}); mkdir -p {' '.join(stier)}

FROM agentinst
{kopier}{(bygg.get('ekstra_miljo') or '') + chr(10) if bygg.get('ekstra_miljo') else ''}USER agent
WORKDIR /home/{repo}
"""
