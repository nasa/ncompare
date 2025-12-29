# Scripts

## bump_develop_after_release.sh

Automatically bumps the develop branch to the next minor version when a release branch is created.

**Usage:**
```bash
./scripts/bump_develop_after_release.sh <release_version>
```

**Example:**
```bash
./scripts/bump_develop_after_release.sh 1.11.0
```

This script is called automatically by CI when a release branch is first pushed. It:
1. Checks out develop
2. Verifies develop is still on the version being released
3. Bumps develop to the next minor alpha (e.g., `1.11.0a6 → 1.12.0a1`)
4. Commits and pushes the change

This prevents version collisions between hotfixes and develop.

**Manual Usage:**

If CI fails to auto-bump develop, you can run it manually:

```bash
git checkout release/1.11.0
bash scripts/bump_develop_after_release.sh 1.11.0
```

The script is idempotent - safe to run multiple times.