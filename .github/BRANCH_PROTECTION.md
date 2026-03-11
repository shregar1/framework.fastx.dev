# Branch Protection Setup

This document explains how to configure branch protection rules for the FastMVC repository.

## Required Settings for `main` Branch

### Step 1: Navigate to Branch Protection Rules

1. Go to your repository on GitHub
2. Click **Settings** → **Branches**
3. Under "Branch protection rules", click **Add rule**
4. Enter `main` as the branch name pattern

### Step 2: Configure Protection Rules

Enable the following settings:

#### ✅ Require a pull request before merging
- [x] **Require approvals** (set to 1 or more)
- [x] **Dismiss stale pull request approvals when new commits are pushed**
- [x] **Require review from Code Owners**

#### ✅ Require status checks to pass before merging
- [x] **Require branches to be up to date before merging**
- Add required status checks:
  - `test` (from CI workflow)
  - `lint` (if available)

#### ✅ Require conversation resolution before merging

#### ✅ Do not allow bypassing the above settings
- This prevents even admins from pushing directly

#### ❌ Allow force pushes - **DISABLED**

#### ❌ Allow deletions - **DISABLED**

### Step 3: Save Changes

Click **Create** or **Save changes**

---

## Quick Setup via GitHub CLI

If you have the GitHub CLI installed, run:

```bash
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["test"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

For this repository, use:

```bash
gh api repos/shregar1/fastMVC/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["check-pr"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

---

## Workflow Enforcement

The repository includes a GitHub Actions workflow that:
1. Runs tests on all PRs
2. Blocks merging if tests fail
3. Requires the CI to pass before merge

See `.github/workflows/ci.yml` for details.

---

## CODEOWNERS

The `.github/CODEOWNERS` file defines who must review changes to specific parts of the codebase.

All PRs modifying protected paths require approval from the designated code owners.
