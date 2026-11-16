"""Multi-SWE-bench-definisjon for navikt/pensjonssimulator (nortrebenk P2.2, forseglet).

Kilde: `.github/workflows/build.yaml` (setup-java temurin 25, `mvn -B package --file pom.xml`) og `pom.xml`
(java.version 25, maven-surefire-plugin 3.6.1). Ett Maven-prosjekt; end-to-end-test/ (Gradle) kjøres ikke.
Testene kjøres med `mvn -B test`, og feilende tester stopper ikke bygget (`maven.test.failure.ignore`).
"""
import _felles


class Spes(_felles.Spes):
    base_image = "maven@sha256:a4734fd7909a9c2beddcacfa1229bd308a349f000bea1ec8db3287c8a16ca2a3"  # maven:3-eclipse-temurin-25, festet 2026-11-16
    oppsett = "ENV MAVEN_OPTS=\"-Xmx1536m\""
    installer = "mvn -B -q dependency:resolve dependency:resolve-plugins > /dev/null 2>&1 || true"

    @staticmethod
    def warm(pr):
        return "mvn -B -q test -Dmaven.test.failure.ignore=true > /dev/null 2>&1 || true"

    @staticmethod
    def test_cmd(pr):
        return "mvn -B test -Dmaven.test.failure.ignore=true -DtrimStackTrace=true"


Instans = _felles.lag_instans("navikt", "pensjonssimulator", Spes)
