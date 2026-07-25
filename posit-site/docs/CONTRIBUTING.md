---
title: "Contributing"
---

Thank you for your interest in contributing. This document provides guidelines for contributing to the project.

---

## Documentation to Read First

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — System design, layers, data flow, component architecture
- **[STRUCTURE.md](STRUCTURE.md)** — Directory structure and file purposes
- **[ROUTES.md](ROUTES.md)** — Routes and sitemap
- **[PROMPT-DESIGN.md](PROMPT-DESIGN.md)** — Prompt construction, output schema (when modifying LLM behavior)
- **[IMPLEMENTATION-PLAN.md](https://github.com/Exios66/vizadvisor/blob/main/IMPLEMENTATION-PLAN.md)** — Phased build specification

---

## Development Setup

```bash
git clone https://github.com/your-username/vizadvisor.git
cd vizadvisor
npm install
cp .env.example .env
# Add VITE_ANTHROPIC_API_KEY or VITE_OPENAI_API_KEY
npm run dev:full
```

---

## Code Style

- **ESLint** — Run `npm run lint` before committing
- **Prettier** — Run `npm run format` for consistent formatting
- **Tests** — Run `npm test`; add tests for new logic

---

## Key Conventions

- **Components** — Functional components, hooks for stateful logic
- **State** — SessionContext for session data; SettingsContext for preferences
- **Services** — Plain JS modules; no React in services
- **Naming** — Descriptive, self-explanatory names (see [MOD_CODING] in project guidelines)

---

## Pull Request Process

1. Create a feature branch from `main`
2. Implement changes with tests where appropriate
3. Run `npm run lint` and `npm test`
4. Update documentation if behavior changes
5. Submit PR with a clear description

---

## Questions

Open an issue for questions or discussions.
