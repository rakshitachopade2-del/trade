# Trade: private stock-options research assistant

Owner: Rakshit. Repository: https://github.com/rakshitachopade2-del/trade
Decision date: 31 October 2026. Display timezone: Asia/Kolkata.

## User's objective

Reduce the preparation and cognitive load of researching Indian stocks with listed options. Produce an evidence-backed shortlist and concise explanations before and during the session. The user makes the final decision and enters every order manually in the broker interface.

Research should combine price structure, Nifty/sector/peer relationships, company results and fundamentals, relevant news, contract execution conditions, and the user's eventual risk constraints. No win-rate target has been established; improvement must be measured, including costs and human reaction delay. A research screen is not a demonstrated trading edge.

## Settled constraints

- The tradable universe is stocks with listed options, with dated eligibility. Indices provide context initially; index strategies are a separate future experiment.
- Zerodha is the user's existing broker. Test the value and coverage of data access before buying it. No subscription or account connection is activated by this repo.
- Keep existing ChatGPT/Claude/Gemini subscriptions. No plan upgrade, paid inference, custom model training, or many-agent runtime is required for milestone 1.
- Earnings, financial comparisons and valuation matter as research inputs. A good company result does not guarantee a profitable call or supply a stop-loss floor. Missing consensus is not zero surprise.
- Compute deterministic features in code. LLMs can later extract and explain sourced evidence, with a separate adapter and measured quality.
- The app stores state independently of any chat. Work chat, local Codex and terminal sessions use repository documents for continuity.
- React + TypeScript, separate CSS modules, no Framer Motion. Python/FastAPI for numerical work. Start on a local computer; choose durable storage and hosting when real data requirements are demonstrated.
- Broker credentials, account data, trade exports and purchased data stay out of the public repository. This is a public code repository, not a public research-feed deployment.

## Stages

1. Engineering replay: fixed synthetic fixtures, strict validation, information-availability clock, transparent screening, evidence gaps. This proves software behavior only.
2. Real data trial: verify current stock-options universe, exact broker fields/coverage/authentication/permissions; validate a small licensed dataset. Add financial filings with source passages and first-seen timestamps. No evidence is invented to make a dashboard look complete.
3. Defined experiment: freeze a numerical setup, cost/fill/delay assumptions, exclusions, evaluation intervals and an experiment ledger. Underlying price outcomes remain distinct from options P&L.
4. Live collection and morning briefing: durable jobs, freshness, reconnect/backfill behavior and forward opportunity records. A running computer/server is required.
5. AI evidence integration: compare extraction accuracy, time saved, decision consistency, and prospective incremental value against the same numerical baseline.

## Unknowns that do not block milestone 1

Available capital, affordable loss limits, daily attention window, actual options buying/selling style, holding period, past trade export, data licensing/retention rights, exact historical option coverage, and model integration eligibility. Leave account-specific values unset. Do not fabricate defaults that look like personal risk advice.

## Relationship to prior research

The research report `AI_Trading_Research_and_Build_Plan.pdf` was reviewed while creating this specification. Later user decisions narrow the first scope to options-listed stocks, Zerodha-first evaluation, subscription-conscious AI and a local VS Code workflow. This brief records those decisions; vendor prices and integration availability must be rechecked when used.
