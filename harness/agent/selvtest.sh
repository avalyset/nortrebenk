#!/bin/bash
# Selvtest for agentbildet (NTB-0006), uten modellkall. Kjøres som root i en fersk container fra agentbildet, på det
# interne nettet ntb-agent, før hver agentkjøring:
#   docker run --rm --user root --network ntb-agent <agentbilde> bash -c "$(cat selvtest.sh)" selvtest <repo> <b64-linje>...
# Argumentene etter repoet er de tre lengste tilføyde linjene i gullpatchen (minst 30 tegn), base64-kodet. De sendes
# bare til denne kortlivede containeren, aldri til agentens container eller inn i bildet.
REPO="$1"; shift
FEIL=0
sjekk() { local navn="$1"; shift; if "$@"; then echo "OK   $navn"; else echo "FEIL $navn"; FEIL=1; fi; }

ingen_kjente_filer() {
  local treff
  treff=$(find / -xdev \( -path /proc -o -path /sys -o -path /dev \) -prune -o \
    \( -name fix.patch -o -name test.patch -o -name run-B.sh -o -name run-C.sh \) -print 2>/dev/null)
  [ -z "$treff" ] || { echo "     funnet: $treff"; return 1; }
}
ingen_gull_linjer() {
  local b linje
  for b in "$@"; do
    linje=$(printf '%s' "$b" | base64 -d)
    if grep -rqF --binary-files=text -- "$linje" /home /root /tmp 2>/dev/null; then echo "     gullinje funnet"; return 1; fi
  done
}
nett_sperret() {
  local h
  for h in github.com registry.npmjs.org repo.maven.apache.org; do
    if command -v curl >/dev/null; then
      if curl -sS -m 10 -o /dev/null "https://$h" 2>/dev/null; then echo "     nådde $h"; return 1; fi
    else
      if timeout 10 bash -c "exec 3<>/dev/tcp/$h/443" 2>/dev/null; then echo "     nådde $h"; return 1; fi
    fi
  done
}
ingen_nokkel() { ! env | grep -q "sk-ant" && ! su agent -c env | grep -q "sk-ant"; }
git_forseglet() {
  cd "/home/$REPO" || return 1
  [ "$(su agent -c 'git log --all --oneline' | wc -l | tr -d ' ')" = "1" ] && [ -z "$(su agent -c 'git remote -v')" ] \
    && [ "$(su agent -c 'git for-each-ref' | wc -l | tr -d ' ')" = "1" ]
}

sjekk "ingen fix.patch, test.patch, run-B.sh eller run-C.sh i filsystemet" ingen_kjente_filer
sjekk "de tre lengste tilføyde gullinjene finnes ikke under /home, /root eller /tmp" ingen_gull_linjer "$@"
sjekk "github.com, registry.npmjs.org og repo.maven.apache.org kan ikke nås" nett_sperret
sjekk "miljøet inneholder ikke sk-ant" ingen_nokkel
sjekk "git: én commit, ingen remotes, én ref" git_forseglet
echo "SELVTEST $([ $FEIL = 0 ] && echo BESTATT || echo FEILET)"
