"""Multi-SWE-bench-definisjon for Altinn/altinn-support-dashboard (nortrebenk P2.2, forseglet).

Kilde: `.github/workflows/frontend-ci.yml` (node-version 24, `npm ci` og `npm test` = `vitest` i
frontend/altinn-support-dashboard.client) og `.github/workflows/backend-ci.yml` (dotnet-version 10.x,
`dotnet test` i backend/test/altinn-support-dashboard.backend.Tests). E2E (Playwright) kjøres ikke.
Bare delen PR-en berører kjøres: vitest med JUnit-rapport for frontend/, dotnet test med TRX for backend/.
"""
import re

import _felles

FE = "frontend/altinn-support-dashboard.client"
BE = "backend/test/altinn-support-dashboard.backend.Tests"


def deler(pr):
    filer = re.findall(r"^diff --git a/(\S+)", pr.test_patch, re.M)
    return {"fe": any(f.startswith("frontend/") for f in filer), "be": any(f.startswith("backend/") for f in filer)}


class Spes(_felles.Spes):
    base_image = "mcr.microsoft.com/dotnet/sdk@sha256:fe0fd4e93bd2fbb47c883b7a6369e5c8d3db8bf01cdc5981f6ee35fbdf3ff4fb"  # mcr.microsoft.com/dotnet/sdk:10.0, festet 2026-11-16
    oppsett = ("COPY --from=node@sha256:9d266751ca3d7fdbe651c878ffd5ad0a42fed49a18c283509267c97f025b7496 /usr/local/bin/node /usr/local/bin/node\n"
               "COPY --from=node@sha256:9d266751ca3d7fdbe651c878ffd5ad0a42fed49a18c283509267c97f025b7496 /usr/local/lib/node_modules /usr/local/lib/node_modules\n"
               "RUN ln -sf ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && "
               "ln -sf ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx && node --version && npm --version")
    installer = f"( cd {FE} && npm ci --no-audit --no-fund ) && dotnet restore {BE}"

    @staticmethod
    def warm(pr):
        return f"dotnet build {BE} --no-restore > /dev/null 2>&1 || true"

    @staticmethod
    def test_cmd(pr):
        d = deler(pr)
        cmd = []
        if d["fe"]:
            cmd.append(f"( cd {FE} && npx vitest run --reporter=default --reporter=junit --outputFile.junit=nortrebenk-junit/junit.xml )")
        if d["be"]:
            cmd.append(f"( cd {BE} && dotnet test --logger 'trx;LogFileName=nortrebenk.trx' --results-directory TestResults )")
        return " ; ".join(cmd) or "true"


Instans = _felles.lag_instans("Altinn", "altinn-support-dashboard", Spes)
