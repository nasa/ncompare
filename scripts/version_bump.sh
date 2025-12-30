#!/usr/bin/env bash
set -e

BRANCH="${1}"
CURRENT=$(bump-my-version show current_version)

echo "Processing branch: $BRANCH (current: $CURRENT)"

ALREADY_COMMITTED=false
PUBLISH=false  # Default: most branches don't publish

case "$BRANCH" in
  develop)
    echo "📦 Bumping develop alpha"
    bump-my-version bump pre_number
    ;;

  release/*)
    echo "🎯 Bumping release"
    if [[ "$CURRENT" == *"a"* ]]; then
      echo "  Alpha → RC1"
      bump-my-version bump pre_label
      git commit -am "Bump to RC1 [skip ci]" && git push
      ALREADY_COMMITTED=true

      # Auto-bump develop
      RELEASE_VERSION="${BRANCH#release/}"
      if [ -f "scripts/bump_develop_after_release.sh" ]; then
        bash scripts/bump_develop_after_release.sh "$RELEASE_VERSION" || exit 1
      fi
      git checkout "$BRANCH"
    else
      echo "  Incrementing RC"
      bump-my-version bump pre_number
    fi
    PUBLISH=true
    ;;

  main)
    echo "🎉 Main branch"
    if [[ "$CURRENT" =~ (rc|a) ]]; then
      echo "  Stripping pre-release label"
      bump-my-version bump pre_label
    else
      echo "  Version already final: $CURRENT (no action needed)"
    fi
    ;;

  hotfix/*)
    echo "🔧 Bumping hotfix patch"
    [[ "$CURRENT" =~ (rc|a) ]] && bump-my-version bump pre_label
    bump-my-version bump patch
    ;;

  *)
    echo "🌟 Branch: no version bump"
    ;;
esac

VERSION=$(bump-my-version show current_version)

# Output for GitHub Actions
{
  echo "version=$VERSION"
  echo "publish=$PUBLISH"
  echo "already_committed=$ALREADY_COMMITTED"
} >> "$GITHUB_OUTPUT"

echo "📌 Version: $VERSION | 📤 Publish: $PUBLISH"
