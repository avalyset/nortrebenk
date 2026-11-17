# NTB-0006: Sealing

- Status: adopted 2026-11-16
- Changed 2026-11-16: web rule, web tools, agent image and key handling for local running.

## Context

The tasks are taken from public repos where the solution exists in later commits and on the web. Agents can look up the solution instead of deriving it.

## Decision

The instance image has the repo at base_sha without later git objects, without remotes and with one ref. The agent's network is limited to the model API and package registries; github.com is blocked. The dependencies are resolved in the image. If the agents run on Modal, the API key is stored as a Modal secret, as a separate key with a spending limit that is deleted after P3.

The agent's network is limited to the model API. The agent container sits on an internal Docker network with no route out. The only way out is a proxy that forwards only to the model API and adds the API key, so that the key never exists in the agent container. Package registries and github.com are not available. Tools that let the model API search or fetch on the web on the agent's behalf are turned off in the agent and rejected in the proxy. The agent image is built without the gold patch, test patch and run scripts, and it is checked before every run. The dependencies for base and for the state with the gold patch are resolved in the image, without source changes from the gold patch coming along. Tasks where the tests still cannot be run without network are marked and reported separately. The sentences about package registries and about Modal above no longer apply (NTB-0011).

## Alternatives considered

- Full network access. Argument against the decision: the agents get the same terms as in normal use. Rejected because the answer key is then one lookup away.
- No network access. Argument against the decision: strongest sealing. Rejected because the agents need the model API.
- Package registries open. Argument against the decision: the agent can add dependencies as a developer would. Rejected because a repo that is published as a package may have the solution in a newer package version, and because 19 of 21 tasks run the tests without network.

## Consequences

The image must be built with dependencies in advance. Network rules and key handling are documented in harness/.

## Sources

- Cursor, «Reward hacking is swamping model intelligence gains» (cursor.com/blog/reward-hacking-coding-benchmarks): «If the agent has access to repository history or the public web, it can sometimes look up the answer rather than derive it.»
- NIST CAISI, «Cheating On AI Agent Evaluations» (nist.gov/blogs/caissi-research-blog/cheating-ai-agent-evaluations): «Models cheating on coding benchmarks by looking up more recent code versions, disabling assertions, and adding test-specific logic.»
- «SWE-Lego: Pushing the Limits of Supervised Fine-tuning for Software Issue Resolving», arXiv:2601.01426: «the agent sometimes peeked at Git history or future commits, thereby cheating rather than faithfully resolving the issue.»
- The Modal documentation, «Networking and security» (modal.com/docs/guide/sandbox-networking): «By default, Sandboxes can make outbound connections to any public IP address.»
