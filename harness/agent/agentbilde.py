"""Agentbilde for nortrebenk (NTB-0006, NTB-0007).

Bygges fra samme oppskrift som instansbildet i harness/msb_repos/_felles.py (samme festede base-image, samme oppsett,
installasjon og oppvarming fra repo-definisjonen), men:
- uten gullpatch, testpatch og kjøreskript (fix.patch, test.patch, run-B.sh, run-C.sh);
- repoet, git-forseglingen og avhengighetscachen eies av brukeren `agent`, og installasjon og oppvarming kjøres som
  den brukeren, slik at cachen ikke kopieres i et nytt lag. Claude Code nekter --dangerously-skip-permissions som root
  (code.claude.com/docs/en/permission-modes), og dokumentasjonen har ingen bryter vi kan sette for å tillate det;
- Claude Code er lagt inn som selvstendig binærfil (/usr/local/bin/claude), lastet ned fra Anthropics utgivelser og
  kontrollert mot sha256 i versjonens manifest. Den bruker ikke repoets node eller npm.
- Miljøet peker Claude Code mot mellomtjeneren og har en plassholder som nøkkel. Bryterne for telemetri,
  feilrapportering, oppdatering og annen ikke-nødvendig trafikk er satt.
Grunnlinjen for `git status` etter oppvarmingen lagres i /etc/ntb/grunnlinje_status.txt, slik at filer oppvarmingen
lager og git ikke ignorerer, kan holdes utenfor agentens patch.
"""
import _felles

CC_VERSJON = "2.1.325"  # gjeldende versjon 16.11.2026 (downloads.claude.ai/claude-code-releases/latest)
CC_SHA256 = {"linux-arm64": "7b6e484b1989a5a14a4b354709ccc8672518a3ec5b9ccd7981fc6254327fde67"}  # fra manifest.json
CC_URL = "https://downloads.claude.ai/claude-code-releases"
MELLOMTJENER = "http://ntb-mellomtjener:8080"
MILJØ = {
    "ANTHROPIC_BASE_URL": MELLOMTJENER,
    "ANTHROPIC_API_KEY": "ntb-plassholder",
    "DISABLE_TELEMETRY": "1",
    "DO_NOT_TRACK": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "DISABLE_AUTOUPDATER": "1",
    "DISABLE_UPDATES": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_DISABLE_FEATURE_FLAGS": "1",
    "DISABLE_FEEDBACK_COMMAND": "1",
}
GIT_INST = ("RUN (command -v git >/dev/null || (apt-get update && apt-get install -y --no-install-recommends git "
            "ca-certificates && rm -rf /var/lib/apt/lists/*))")


def agent_dockerfile(org, repo, sha, spes, plattform="linux-arm64"):
    miljø = " ".join(f'{k}="{v}"' for k, v in MILJØ.items())
    return f"""FROM {spes.base_image} AS kilde
{GIT_INST}
RUN git clone -q https://github.com/{org}/{repo}.git /src && cd /src && git checkout -q {sha} && rm -rf /src/.git

FROM {spes.base_image} AS cc
RUN (command -v curl >/dev/null || (apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*))
RUN curl -fsSL {CC_URL}/{CC_VERSJON}/{plattform}/claude -o /claude && echo "{CC_SHA256[plattform]}  /claude" | sha256sum -c - && chmod 755 /claude

FROM {spes.base_image}
LABEL nortrebenk=p2 nortrebenk.bilde=agent
WORKDIR /home/
ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC LANG=C.UTF-8 LC_ALL=C.UTF-8
{GIT_INST}
{spes.oppsett}
RUN useradd -m -u 10001 -s /bin/bash agent
COPY --from=kilde --chown=agent:agent /src /home/{repo}
COPY --chown=agent:agent forbered.sh /opt/ntb/forbered.sh
USER agent
ENV HOME=/home/agent
WORKDIR /home/{repo}
RUN git init -q && git add -A && {_felles.GIT_ID} git commit -q -m "base" && git gc -q --prune=now
RUN bash /opt/ntb/forbered.sh
USER root
RUN rm -rf /opt/ntb && mkdir -p /etc/ntb && cd /home/{repo} && su agent -c "git status --porcelain --untracked-files=all" > /etc/ntb/grunnlinje_status.txt \\
 && test "$(su agent -c 'git log --all --oneline' | wc -l | tr -d ' ')" = "1" && test -z "$(su agent -c 'git remote -v')" \\
 && test "$(su agent -c 'git for-each-ref' | wc -l | tr -d ' ')" = "1" && echo FORSEGLET > /etc/ntb/forsegling.txt
COPY --from=cc /claude /usr/local/bin/claude
ENV {miljø}
USER agent
WORKDIR /home/{repo}
"""


def forbered(repo, spes, pr):
    return f"""#!/bin/bash
set -e
cd /home/{repo}
{spes.installer}
{spes.warm(pr)}
"""
