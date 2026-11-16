"""Multi-SWE-bench-definisjon for Altinn/altinn-access-management-frontend (nortrebenk P2.2, forseglet).

Kilde: `.github/workflows/template-build-and-test-frontend.yml` (node-version lts/*, `yarn --immutable`,
`yarn vitest`) og `package.json` (packageManager yarn@4.18.1, vitest ^4.1.5). Backend (dotnet) og Playwright
kjøres ikke; alle kandidatene har testfiler under src/. Vitest kjøres med JUnit-rapport.
"""
import _felles


class Spes(_felles.Spes):
    base_image = "node@sha256:9d266751ca3d7fdbe651c878ffd5ad0a42fed49a18c283509267c97f025b7496"  # node:24, festet 2026-11-16
    oppsett = "RUN corepack enable"
    installer = "yarn --immutable"

    @staticmethod
    def warm(pr):
        return "true"

    @staticmethod
    def test_cmd(pr):
        return "yarn vitest run --reporter=default --reporter=junit --outputFile.junit=nortrebenk-junit/junit.xml"


Instans = _felles.lag_instans("Altinn", "altinn-access-management-frontend", Spes)
