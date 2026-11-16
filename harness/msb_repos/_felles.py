"""Felles Multi-SWE-bench-klasser for nortrebenk P2.2 (forseglede instansbilder).

Bygger på P1-versjonen. Endringer i P2.2:
- Base-imagene er festet med digest i hver repo-definisjon.
- Instansbildet er forseglet: repoet hentes i et eget byggesteg og sjekkes ut på base_sha. Deretter kopieres bare
  arbeidstreet (uten .git) inn i det endelige bildet, som får et nytt git-repo med én commit (ingen historikk, ingen
  remotes, ingen andre refs). Avhengighetene installeres etter forseglingen, slik at et bygg som leser git-historikk
  eller tagger, feiler synlig.
- Bildet kontrollerer selv at `git log --all` viser én commit og at `git remote -v` er tom.
- Kjøringene (B og C) har ingen `git fetch` og ingen `git clean -x`.
Alle images får `LABEL nortrebenk=p2`. Testresultater leses fra JUnit-XML og TRX som i P1.
"""
import re
import xml.etree.ElementTree as ET
from typing import Optional

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest

LABEL = "LABEL nortrebenk=p2"

DUMP = r"""
dump_rapporter() {
  for f in $(find . \( -path '*/node_modules' -prune \) -o \( -type f \( -path '*/build/test-results/*' -o -path '*/target/surefire-reports/*' -o -path '*/nortrebenk-junit/*' -o -name '*.trx' \) \( -name '*.xml' -o -name '*.trx' \) -print \) 2>/dev/null); do
    echo "<<<RAPPORT $f>>>"; cat "$f"; echo; echo "<<<SLUTT>>>"
  done
}
"""

RYDD = r"""
rydd_rapporter() {
  find . \( -path '*/node_modules' -prune \) -o \( -type d \( -path '*/build/test-results' -o -path '*/target/surefire-reports' -o -name 'nortrebenk-junit' -o -name 'TestResults' \) -print \) 2>/dev/null | xargs rm -rf
}
"""

GIT_ID = "GIT_AUTHOR_NAME=nortrebenk GIT_AUTHOR_EMAIL=nortrebenk GIT_COMMITTER_NAME=nortrebenk GIT_COMMITTER_EMAIL=nortrebenk"


class Spes:
    base_image: str = "ubuntu:24.04"
    oppsett: str = ""
    installer: str = "true"

    @staticmethod
    def warm(pr):
        return "true"

    @staticmethod
    def test_cmd(pr):
        return "true"


def _skript(spes, pr, patcher: str, reinstall: bool) -> str:
    return f"""#!/bin/bash
set -uo pipefail
{DUMP}
{RYDD}
cd /home/{pr.repo}
git apply --whitespace=nowarn {patcher} || {{ echo "NORTREBENK_PATCH_FEILET"; exit 0; }}
{spes.installer if reinstall else 'true'}
rydd_rapporter
{spes.test_cmd(pr)} ; echo "NORTREBENK_TEST_EXIT=$?"
dump_rapporter
"""


class NtbForseglet(Image):
    def __init__(self, pr: PullRequest, config: Config, spes, reinstall: bool):
        self._pr, self._config, self.spes, self.reinstall = pr, config, spes, reinstall

    @property
    def pr(self):
        return self._pr

    @property
    def config(self):
        return self._config

    def image_prefix(self) -> str:
        return "nortrebenk-p2"

    def dependency(self) -> str:
        return self.spes.base_image

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        pr, s = self.pr, self.spes
        return [
            File(".", "fix.patch", pr.fix_patch),
            File(".", "test.patch", pr.test_patch),
            File(".", "prepare.sh", f"""#!/bin/bash
set -e
cd /home/{pr.repo}
{s.installer}
{s.warm(pr)}
"""),
            File(".", "run-B.sh", _skript(s, pr, "/home/test.patch", self.reinstall)),
            File(".", "run-C.sh", _skript(s, pr, "/home/test.patch /home/fix.patch", self.reinstall)),
        ]

    def dockerfile(self) -> str:
        pr = self.pr
        kopi = "".join(f"COPY {f.name} /home/\n" for f in self.files())
        return f"""FROM {self.dependency()} AS kilde
RUN (command -v git >/dev/null || (apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*))
RUN git clone -q https://github.com/{pr.org}/{pr.repo}.git /src && cd /src && git checkout -q {pr.base.sha} && rm -rf /src/.git

FROM {self.dependency()}
{LABEL}
WORKDIR /home/
ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN (command -v git >/dev/null || (apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*))
{self.spes.oppsett}
COPY --from=kilde /src /home/{pr.repo}
WORKDIR /home/{pr.repo}
RUN git init -q && git add -A && {GIT_ID} git commit -q -m "base" && git gc -q --prune=now
{kopi}
RUN bash /home/prepare.sh
RUN test "$(git log --all --oneline | wc -l | tr -d ' ')" = "1" && test -z "$(git remote -v)" && test "$(git for-each-ref | wc -l | tr -d ' ')" = "1" && echo FORSEGLET > /home/forsegling.txt
"""


def parse_rapporter(logg: str) -> TestResult:
    status = {}
    for m in re.finditer(r"<<<RAPPORT (\S+)>>>\n(.*?)\n<<<SLUTT>>>", logg, re.S):
        tekst = m.group(2).strip()
        if not tekst:
            continue
        try:
            rot = ET.fromstring(tekst)
        except ET.ParseError:
            continue
        tag = lambda e: e.tag.split("}")[-1]
        if tag(rot) == "TestRun":
            for e in rot.iter():
                if tag(e) == "UnitTestResult":
                    navn, utfall = e.get("testName"), e.get("outcome")
                    st = "PASS" if utfall == "Passed" else ("SKIP" if utfall in ("NotExecuted", "Inconclusive") else "FAIL")
                    status[navn] = _verst(status.get(navn), st)
            continue
        for tc in rot.iter():
            if tag(tc) != "testcase":
                continue
            navn = f"{tc.get('classname', '')}::{tc.get('name', '')}"
            barn = {tag(c) for c in tc}
            st = "FAIL" if barn & {"failure", "error"} else ("SKIP" if "skipped" in barn else "PASS")
            status[navn] = _verst(status.get(navn), st)
    p = {k for k, v in status.items() if v == "PASS"}
    f = {k for k, v in status.items() if v == "FAIL"}
    s = {k for k, v in status.items() if v == "SKIP"}
    return TestResult(passed_count=len(p), failed_count=len(f), skipped_count=len(s),
                      passed_tests=p, failed_tests=f, skipped_tests=s)


def _verst(a: Optional[str], b: str) -> str:
    orden = {"FAIL": 3, "SKIP": 2, "PASS": 1, None: 0}
    return a if orden[a] >= orden[b] else b


def lag_instans(org: str, repo: str, spes):
    @Instance.register(org, repo)
    class NtbInstance(Instance):
        def __init__(self, pr: PullRequest, config: Config, *args, reinstall: bool = False, **kwargs):
            super().__init__()
            self._pr, self._config, self.reinstall = pr, config, reinstall

        @property
        def pr(self):
            return self._pr

        def dependency(self) -> Optional[Image]:
            return NtbForseglet(self.pr, self._config, spes, self.reinstall)

        def run(self, run_cmd: str = "") -> str:
            return run_cmd or "bash /home/run-B.sh"

        def test_patch_run(self, test_patch_run_cmd: str = "") -> str:
            return test_patch_run_cmd or "bash /home/run-B.sh"

        def fix_patch_run(self, fix_patch_run_cmd: str = "") -> str:
            return fix_patch_run_cmd or "bash /home/run-C.sh"

        def parse_log(self, test_log: str) -> TestResult:
            return parse_rapporter(test_log)

    return NtbInstance
