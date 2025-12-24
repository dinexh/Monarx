# Contributing to Monarx

Thank you for your interest in contributing to **Monarx** 🚀  
Monarx is a lightweight system monitoring agent, currently focused on macOS,
with plans for Windows and Linux support.

This document explains how to contribute cleanly and safely.

---

## 1. Project Workflow (Important)

We follow a simple but strict workflow:

1. **Create or pick an Issue**
2. **Create a branch from `dev`**
3. **Make changes**
4. **Open a Pull Request (PR)**
5. **Get review & merge**

⚠️ Direct pushes to `main` are not allowed.

---

## 2. Branching Rules

- `main` → Stable, release-ready code
- `dev` → Active development branch
- Feature / fix branches:
- Example :
fix/dock-icon
feature/windows-agent
refactor/code-structure


Always branch **from `dev`**, never from `main`.

---

## 3. Issues First

Before making changes:
- Check existing Issues
- If none exist, **create one**

Issues help:
- Track bugs
- Discuss design decisions
- Coordinate platform-specific work

### Issue labels to use
- `bug`
- `enhancement`
- `refactor`
- `platform:mac`
- `platform:windows`
- `platform:linux`
- `good first issue`

---

## 4. Pull Requests (PRs)

Each PR should:
- Solve **one problem**
- Link to an Issue
- Target the `dev` branch

### PR title format
fix(mac): hide Dock icon for background app
feature(windows): initial system agent skeleton

### PR description should include:
- What changed
- Why it was needed
- Platform impact
- Linked Issue (`Closes #12`)

---

## 5. Code Organization Rules

Monarx is structured to support multiple platforms.

### Guidelines
- Shared logic goes in reusable modules
- Platform-specific code must be isolated
- Do not mix OS-level hacks into core logic

Example:
monarx/
core/ # shared logic
mac/ # macOS-specific code
windows/ # Windows-specific code


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
fix(mac): hide Dock icon using accessory policy
refactor: reorganize monitoring modules
feature: add configurable alert thresholds


This helps with:
- History readability
- Future releases
- Debugging regressions

---

## 8. Be Respectful

This project follows a friendly and respectful collaboration model.
Constructive feedback is always welcome.

Happy hacking 👋
