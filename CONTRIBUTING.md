# Contributing to Monarx

Thank you for your interest in contributing to **Monarx** 🚀

Monarx is a lightweight system monitoring agent, currently focused on macOS, with plans for Windows and Linux support.

This document explains how to contribute cleanly and safely.

---

## 1. Project Workflow (Important)

We follow a simple but strict workflow:

1. **Create or pick an Issue**
2. **Create a branch from `dev`**
3. **Make changes**
4. **Open a Pull Request (PR)**
5. **Get review & merge**

> ⚠️ **Important:** Direct pushes to `main` are not allowed.

---

## 2. Branching Rules

- `main` → Stable, release-ready code
- `dev` → Active development branch
- Feature / fix branches → Always branch **from `dev`**, never from `main`

### Branch naming examples:

```
fix/dock-icon
feature/windows-agent
refactor/code-structure
```

---

## 3. Issues First

Before making changes:
- Check existing Issues
- If none exist, **create one**

Issues help:
- Track bugs
- Discuss design decisions
- Coordinate platform-specific work

### Issue Labels

Use these labels when creating issues:
- `bug` - Report bugs and unexpected behavior
- `enhancement` - Suggest new features or improvements
- `refactor` - Code improvements without changing functionality
- `platform:mac` - macOS-specific issues
- `platform:windows` - Windows-specific issues
- `platform:linux` - Linux-specific issues
- `good first issue` - Suitable for new contributors

---

## 4. Pull Requests (PRs)

Each PR should:
- Solve **one problem**
- Link to an Issue
- Target the `dev` branch

### PR Title Format

Use semantic commit format:

```
fix(mac): hide Dock icon for background app
feature(windows): initial system agent skeleton
refactor: reorganize monitoring modules
```

### PR Description Template

Your PR description should include:
- **What changed** - Brief summary of changes
- **Why it was needed** - Context and motivation
- **Platform impact** - Which platforms are affected
- **Linked Issue** - Reference with `Closes #12` or `Fixes #12`

---

## 5. Code Organization Rules

Monarx is structured to support multiple platforms.

### Guidelines

- Shared logic goes in reusable modules
- Platform-specific code must be isolated
- Do not mix OS-level hacks into core logic

### Example Structure

```
core/         # shared logic
  __init__.py
  config.py
mac/          # macOS-specific code
  __init__.py
windows/      # Windows-specific code
  __init__.py
linux/        # Linux-specific code
  __init__.py
main.py       # Entry point
```

---

## 6. Platform-Specific Rules

### macOS

- Use AppKit / PyObjC responsibly
- Ensure background-only behavior when required
- No Dock or Cmd+Tab visibility unless intentional

### Windows / Linux

- Avoid assumptions from macOS behavior
- Keep implementations modular and replaceable

---

## 7. Commit Message Style

We follow **semantic commit messages**:

```
fix(mac): hide Dock icon using accessory policy
refactor: reorganize monitoring modules
feature: add configurable alert thresholds
```

This helps with:
- History readability
- Future releases
- Debugging regressions

---

## 8. Be Respectful

This project follows a friendly and respectful collaboration model. Constructive feedback is always welcome.

Happy hacking 👋