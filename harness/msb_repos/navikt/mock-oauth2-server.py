"""Multi-SWE-bench-definisjon for navikt/mock-oauth2-server (nortrebenk P2.2, forseglet).

Kilde for toolchain og testkommando: `.github/workflows/test-pr.yaml` (setup-java temurin 21, `./gradlew build`)
og `gradle/wrapper/gradle-wrapper.properties`. Ett Gradle-prosjekt; testene kjøres med `./gradlew test`.
"""
import _felles


class Spes(_felles.Spes):
    base_image = "eclipse-temurin@sha256:0a3f329821dcadf54b2a3033a15e2e9f007069a9db43d7f51897e6b80e726b07"  # eclipse-temurin:21-jdk, festet 2026-11-16
    oppsett = "ENV GRADLE_OPTS=\"-Dorg.gradle.daemon=false -Dorg.gradle.workers.max=2\""
    installer = "./gradlew --no-daemon -q dependencies > /dev/null || true"

    @staticmethod
    def warm(pr):
        return "./gradlew --no-daemon test --continue > /dev/null 2>&1 || true"

    @staticmethod
    def test_cmd(pr):
        return "./gradlew --no-daemon test --continue"


Instans = _felles.lag_instans("navikt", "mock-oauth2-server", Spes)
