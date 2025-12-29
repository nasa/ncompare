#!/bin/bash
# Auto-bump develop to next minor when release branch is created
# Usage: ./scripts/bump_develop_after_release.sh <release_version>
#
# Example: ./scripts/bump_develop_after_release.sh 1.11.0
#
# This script:
# 1. Checks out develop
# 2. Checks if develop is still on the version being released
# 3. If yes, bumps to next minor (e.g., 1.11.0a6 → 1.12.0a1)
# 4. Commits and pushes

set -e  # Exit on error

RELEASE_VERSION=$1

if [ -z "$RELEASE_VERSION" ]; then
  echo "Usage: $0 <release_version>"
  echo "Example: $0 1.11.0"
  exit 1
fi

echo "🚀 Auto-bumping develop after release/$RELEASE_VERSION creation"

# Fetch and checkout develop
git fetch origin develop
git checkout develop
git pull origin develop

# Get current develop version
CURRENT=$(bump-my-version show current_version)
echo "   Develop is currently at: $CURRENT"

# Check if develop is still on the version being released
if [[ "$CURRENT" == "${RELEASE_VERSION}"* ]]; then
  echo "   Develop needs to be bumped to next minor"

  # Calculate next minor version
  MAJOR=$(echo "$RELEASE_VERSION" | cut -d. -f1)
  MINOR=$(echo "$RELEASE_VERSION" | cut -d. -f2)
  NEXT_MINOR=$((MINOR + 1))
  NEXT_VERSION="${MAJOR}.${NEXT_MINOR}.0a1"

  echo "   Bumping: $CURRENT → $NEXT_VERSION"

  # Bump to next minor
  bump-my-version bump --new-version "$NEXT_VERSION" minor

  # Commit and push
  git commit -am "Start $NEXT_VERSION development [skip ci]"
  git push origin develop

  echo "✅ Develop bumped to $NEXT_VERSION"
else
  echo "ℹ️  Develop already at $CURRENT (not on $RELEASE_VERSION), skipping bump"
fi