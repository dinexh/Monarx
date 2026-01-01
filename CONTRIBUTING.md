# Contributing to Monarx

Thank you for your interest in contributing to **Monarx** 🚀

Monarx is a lightweight macOS-only system monitoring agent. This document explains how to contribute cleanly and safely.

---

## 1. Project Workflow

We follow a simple workflow:

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
- Feature / fix branches → Always branch **from `dev`**

### Branch naming examples:
```
fix/memory-leak
feature/detailed-gpu
refactor/ui-components
```

---

## 3. Issues First

Before making changes:
- Check existing Issues
- If none exist, **create one**

### Issue Labels
- `bug` - Report bugs
- `enhancement` - Suggest new features
- `refactor` - Code improvements
- `good first issue` - Suitable for new contributors

---

## 4. Pull Requests (PRs)

Each PR should:
- Solve **one problem**
- Link to an Issue
- Target the `dev` branch

### PR Title Format
```
fix: correct memory pressure calculation
feature: add system temperature monitoring
refactor: optimize process scanning
```

---

## 5. Code Organization

```
core/         # Shared logic (macOS focused)
mac/          # macOS-specific implementation (AppKit/rumps)
main.py       # Entry point
```

---

## 6. Development Rules

- Use AppKit / PyObjC responsibly.
- Ensure background-only behavior (Accessory policy).
- No Dock icon unless explicitly configured.
- Follow PEP 8 style for Python code.

---

## 7. Commit Message Style

We follow **semantic commit messages**:
```
fix: fix crash on memory pressure event
refactor: clean up process menu generation
feature: add disk usage to menu bar
```

---

## 8. Be Respectful

This project follows a friendly and respectful collaboration model. Constructive feedback is always welcome.

Happy hacking 👋
