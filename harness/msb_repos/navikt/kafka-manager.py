"""Multi-SWE-bench-definisjon for navikt/kafka-manager (nortrebenk P2.2, forseglet).

Kilde: `.github/workflows/main.yml` (setup-java temurin 25, `./gradlew :api:check` og `./gradlew :web-app:check`),
`api/build.gradle.kts` (jvmToolchain 25) og `web-app/build.gradle.kts` (gradle-node-plugin, node 24.22.2,
pnpm 12.15.0, `testFrontend` = `pnpm run test` = `vitest run`).

Bare delen PR-en berører kjøres: `:api:test` når testpatchen har filer under api/, og vitest i web-app/ når den har
filer under web-app/. Vitest kjøres med pnpm og node som Gradle-pluginen selv laster ned, og med JUnit-rapport.
"""
import re

import _felles

WEB = (
    "./gradlew --no-daemon -q :web-app:pnpmInstall && ( cd web-app && "
    "NODE_BIN=$(dirname $(find build/nodejs -type f -name node -path '*/bin/*' | head -1)) && "
    "PNPM_BIN=$(dirname $(find build/pnpm -name pnpm -path '*/bin/*' | head -1)) && "
    "PATH=$PNPM_BIN:$NODE_BIN:$PATH pnpm exec vitest run --reporter=default --reporter=junit "
    "--outputFile.junit=nortrebenk-junit/junit.xml )"
)


def deler(pr):
    filer = re.findall(r"^diff --git a/(\S+)", pr.test_patch, re.M)
    return {"api": any(f.startswith("api/") for f in filer), "web": any(f.startswith("web-app/") for f in filer)}


class Spes(_felles.Spes):
    base_image = "eclipse-temurin@sha256:b8705e936964c228dfce359e63dbf08f6c69cb380ed1d576b1f6b1064f15567d"  # eclipse-temurin:25-jdk, festet 2026-11-16
    oppsett = "ENV GRADLE_OPTS=\"-Dorg.gradle.daemon=false -Dorg.gradle.workers.max=2\""
    installer = "./gradlew --no-daemon -q :api:dependencies > /dev/null 2>&1 || true; ./gradlew --no-daemon -q :web-app:pnpmInstall > /dev/null 2>&1 || true"

    @staticmethod
    def warm(pr):
        return "./gradlew --no-daemon :api:test --continue > /dev/null 2>&1 || true"

    @staticmethod
    def test_cmd(pr):
        d = deler(pr)
        cmd = []
        if d["api"]:
            cmd.append("./gradlew --no-daemon :api:test --continue")
        if d["web"]:
            cmd.append(WEB)
        return " ; ".join(cmd) or "true"


Instans = _felles.lag_instans("navikt", "kafka-manager", Spes)
