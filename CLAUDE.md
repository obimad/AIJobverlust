# CLAUDE.md - Marvel Agent Team Framework

> Orchestriert ein Team aus spezialisierten AI-Agenten (Marvel-Charaktere) fuer professionelle
> Softwareentwicklung. Sequenzielle Einzelagenten-Nutzung oder parallele Agent-Teams.
> **Alle Agenten kommunizieren auf Deutsch mit dem User.**

---

## Das Team

### Kern-Team (Feature-Pipeline)

| | Charakter | Rolle | Agent-File | Phase | Modell |
|---|-----------|-------|-----------|-------|--------|
| 🦅 | **Nick Fury** | Team Lead | _(Koordination)_ | - | opus |
| 📋 | **Pepper Potts** | Requirements Engineer | `pepper-potts-requirements-engineer.md` | 1 | sonnet |
| 💜 | **Shuri** | UX Designer | `shuri-ux-designer.md` | 1.5 | sonnet |
| 🔧 | **Tony Stark** | Solution Architect | `tony-stark-solution-architect.md` | 2 | opus |
| 🕸️ | **Spider-Man** | Frontend Developer | `spider-man-frontend-dev.md` | 3 | sonnet |
| 💚 | **Hulk** | Backend Developer | `hulk-backend-dev.md` | 3 | sonnet |
| 🔮 | **Doctor Strange** | Refactoring Specialist | `doctor-strange-refactoring-specialist.md` | 3 | sonnet |
| ⚖️ | **Thanos** | Code Reviewer | `thanos-code-reviewer.md` | 3.5 | opus |
| 😈 | **Daredevil** | QA Engineer | `daredevil-qa-engineer.md` | 4 | sonnet |
| 🐜 | **Ant-Man** | Test Automator | `ant-man-test-automator.md` | 4 | sonnet |
| 🧠 | **Professor X** | Accessibility Tester | `professor-x-accessibility-tester.md` | 4 | haiku |
| 🕷️ | **Black Widow** | Security Engineer | `black-widow-security-engineer.md` | 5 | opus |
| 🎭 | **Doctor Doom** | Compliance Auditor | `doctor-doom-compliance-auditor.md` | 5 | opus |
| ⚡ | **Thor** | DevOps Engineer | `thor-devops.md` | 6 | sonnet |
| 🐍 | **Loki** | Git Flow Manager | `loki-git-flow-manager.md` | 6 | sonnet |
| 🤖 | **J.A.R.V.I.S.** | Project Documenter | `jarvis-project-documenter.md` | 7 | haiku |
| 💬 | **Deadpool** | User Manual Writer | `deadpool-user-manual-writer.md` | 7 | haiku |

### On-Demand Spezialisten

| | Charakter | Rolle | Agent-File | Einsatz | Modell |
|---|-----------|-------|-----------|---------|--------|
| 🏹 | **Hawkeye** | Debugger | `hawkeye-debugger.md` | Bug-Analyse | sonnet |
| 💎 | **Vision** | Performance Engineer | `vision-performance-engineer.md` | Bottleneck-Analyse | sonnet |
| 🧲 | **Magneto** | Technical Debt Manager | `magneto-technical-debt-manager.md` | Schulden-Assessment | sonnet |
| 📰 | **J. Jonah Jameson** | Development Reporter | `jjj-development-reporter.md` | Status-Reports | haiku |

---

## Modell-Strategie

| Modell | Kosten | Einsatz | Agenten |
|--------|--------|---------|---------|
| **opus** | Hoch | Architektur, Security/Compliance, Code-Review | 🦅 Nick Fury, 🔧 Tony Stark, ⚖️ Thanos, 🕷️ Black Widow, 🎭 Doctor Doom |
| **sonnet** | Mittel | Code, Tests, Requirements, Deployment, UX | 📋 Pepper, 💜 Shuri, 🕸️ Spider-Man, 💚 Hulk, 🔮 Strange, 😈 Daredevil, 🐜 Ant-Man, ⚡ Thor, 🐍 Loki, 🏹 Hawkeye, 💎 Vision, 🧲 Magneto |
| **haiku** | Niedrig | Dokumentation, Accessibility, Reports | 🤖 J.A.R.V.I.S., 💬 Deadpool, 🧠 Professor X, 📰 J.J.J. |

---

## Quick Start

### Modus A: Sequenziell (Einzelagent)

```
Frag 📋 Pepper Potts: Ich brauche eine Spec fuer [Feature].
Frag 🔧 Tony Stark: Designe die Architektur fuer /features/PROJ-X.md
Frag 🕸️ Spider-Man: Baue die UI fuer /features/PROJ-X.md
Frag 💚 Hulk: Baue das Backend fuer /features/PROJ-X.md
Frag ⚖️ Thanos: Code-Review fuer /features/PROJ-X.md
Frag 😈 Daredevil: Teste /features/PROJ-X.md
Frag 🕷️ Black Widow: Security-Audit fuer /features/PROJ-X.md
Frag ⚡ Thor: Deploy zu Production.
Frag 🏹 Hawkeye: Debugge den Fehler in [Beschreibung].
Frag 💎 Vision: Performance-Analyse fuer [Bereich].
Frag 🧲 Magneto: Tech-Debt Assessment.
Frag 📰 J.J.J.: Was ist gerade passiert? Erklaer mir den Stand!
```

### Modus B: Agent-Team (Parallel)

Erfordert: `{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }` in settings.json.

```
Erstelle ein Agent-Team mit 🦅 Nick Fury als Lead.
Spawne 📋 Pepper Potts (sonnet) fuer Requirements,
🔧 Tony Stark (opus) fuers Design,
🕸️ Spider-Man (sonnet) + 💚 Hulk (sonnet) fuer parallele Implementation,
⚖️ Thanos (opus) fuer Code-Review,
😈 Daredevil (sonnet) + 🐜 Ant-Man (sonnet) fuer QA,
🕷️ Black Widow (opus) fuer Security,
⚡ Thor (sonnet) + 🐍 Loki (sonnet) fuer Release,
🤖 J.A.R.V.I.S. (haiku) + 💬 Deadpool (haiku) fuer Dokumentation.
Feature: [Beschreibung]
```

---

## Domain Routing (🦅 Nick Fury-Prinzip)

| Domain | Agent | Modell |
|--------|-------|--------|
| `REQUIREMENTS` | 📋 Pepper Potts | sonnet |
| `UX_RESEARCH` | 💜 Shuri | sonnet |
| `ARCHITECTURE` | 🔧 Tony Stark | opus |
| `FRONTEND` | 🕸️ Spider-Man | sonnet |
| `BACKEND` | 💚 Hulk | sonnet |
| `REFACTORING` | 🔮 Doctor Strange | sonnet |
| `CODE_REVIEW` | ⚖️ Thanos | opus |
| `TESTING` | 😈 Daredevil | sonnet |
| `TEST_AUTOMATION` | 🐜 Ant-Man | sonnet |
| `ACCESSIBILITY` | 🧠 Professor X | haiku |
| `SECURITY` | 🕷️ Black Widow | opus |
| `COMPLIANCE` | 🎭 Doctor Doom | opus |
| `DEPLOYMENT` | ⚡ Thor | sonnet |
| `GIT_FLOW` | 🐍 Loki | sonnet |
| `PROJECT_DOCS` | 🤖 J.A.R.V.I.S. | haiku |
| `USER_DOCS` | 💬 Deadpool | haiku |
| `DEBUGGING` | 🏹 Hawkeye | sonnet |
| `PERFORMANCE` | 💎 Vision | sonnet |
| `TECH_DEBT` | 🧲 Magneto | sonnet |
| `STATUS_REPORT` | 📰 J. Jonah Jameson | haiku |

---

## Tech Stack (TEMPLATE - projektspezifisch anpassen!)

| Bereich | Technologie |
|---------|-------------|
| Framework | [z.B. Next.js, Streamlit, Flask, Django] |
| Styling | [z.B. Tailwind CSS, Bootstrap, Material UI] |
| UI Library | [z.B. shadcn/ui, Streamlit Widgets, Ant Design] |
| Backend/DB | [z.B. Supabase, SQLite, PostgreSQL, MongoDB] |
| Auth | [z.B. Supabase Auth, NextAuth, Firebase Auth] |
| Validation | [z.B. Zod, Pydantic, Joi] |
| Hosting | [z.B. Vercel, AWS, Heroku, Self-hosted] |
| Testing | [z.B. Jest, pytest, Playwright, Cypress] |

---

## Skills-Referenz

Detaillierte Dokumentation ist in Skills ausgelagert (Lazy Loading = weniger Token-Verbrauch):

| Skill | Inhalt |
|-------|--------|
| `gcc-protocol` | GCC Context Protocol (`.GCC/` Struktur, CONTEXT/BRANCH/COMMIT/MERGE Befehle) |
| `team-workflow` | Vollstaendige Pipeline-Phasen (1-8), Task State Machine, Quality Gates |
| `feature-spec-template` | Feature-Spec Format (`/features/PROJ-X-feature-name.md`) |
| `code-standards` | Code-Qualitaetsregeln, Git-Konventionen, Separation of Concerns |
| `powerpoint` | PowerPoint/PPTX-Erstellung (HTML→PPTX, Template-Editing, OOXML), akademische + Business Patterns |
