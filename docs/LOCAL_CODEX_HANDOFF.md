# Continue in local Codex

Open the intended repository in VS Code, then paste the following into Codex. This document is the explicit context handoff; a new local conversation is not assumed to know the Work chat.

---

Continue the Trade research project. First read AGENTS.md and docs/PROJECT_BRIEF.md, docs/MILESTONE_1.md, docs/API_CONTRACT.md, docs/STATUS.md and README.md.

Inspect the actual workspace, Git status, branch and remotes before editing. The intended remote is https://github.com/rakshitachopade2-del/trade.git. If this is just an empty folder, clone into it only when empty; if it contains files, preserve them and reconcile without overwriting. If it is a different repository, stop repository-changing actions and explain the mismatch.

Determine which milestone files are present. Install the documented dependencies into a local Python virtual environment and frontend node_modules. Run the meaningful backend tests and frontend typecheck/build. Start both services locally and verify the synthetic replay: at 09:30 no post-range confirmation; at 09:35 the qualified example; at 09:40 newly available evidence. Confirm unknown fundamentals, stale data and missing eligibility remain visible. Fix any implementation defects you find and update STATUS.md with exact results.

We are building a private decision-support app for Indian stocks with listed options. Nifty/sector context and quarterly fundamentals matter, but underlying screens are not option-trade recommendations. All orders stay manual in Zerodha. Do not connect a broker, spend money, call a paid LLM, deploy, or place trades as part of this setup.

Keep React+TypeScript and separate CSS modules. Preserve user changes. Do not change global Git identity. Keep secrets and private datasets out of Git. Report what is working, what remains unverified, and the next smallest real-data experiment. Do not invent a profitability result.

---

If a downloaded source ZIP was used, extract into a separate directory first. Do not overwrite an existing `.git` directory or user files. Let local Codex reconcile its contents with the intended checkout before committing.
