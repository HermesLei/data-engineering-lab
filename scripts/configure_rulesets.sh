#!/usr/bin/env bash
set -euo pipefail

# Apply repository Rulesets for main and dev.
# Requires: gh, jq, an authenticated GitHub account with repository admin access.
REPO="${GITHUB_REPOSITORY:-HermesLei/data-engineering-lab}"

for command in gh jq; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "::error::Required command not found: $command"
    exit 1
  fi
done

gh auth status >/dev/null

# These are the job names returned by successful Actions runs on the current main.
REQUIRED_CHECKS=(
  "Python lint and unit tests"
  "Build image and validate Airflow DAGs"
  "Validate Docker Compose configuration"
  "Validate branch flow"
)

apply_ruleset() {
  local branch="$1"
  local name="Protect ${branch}"
  local payload
  local ruleset_id

  payload="$(mktemp)"
  trap 'rm -f "$payload"' RETURN

  jq -n \
    --arg name "$name" \
    --arg repo "$REPO" \
    --arg branch "$branch" \
    --argjson checks "$(printf '%s\n' "${REQUIRED_CHECKS[@]}" | jq -R . | jq -s '[.[] | {context: ., integration_id: 15368}]')" \
    '{
      name: $name,
      target: "branch",
      source: $repo,
      enforcement: "active",
      conditions: {
        ref_name: {
          include: ["refs/heads/" + $branch],
          exclude: []
        }
      },
      rules: [
        {type: "deletion"},
        {type: "non_fast_forward"},
        {
          type: "pull_request",
          parameters: {
            allowed_merge_methods: ["merge", "squash", "rebase"],
            dismiss_stale_reviews_on_push: false,
            require_code_owner_review: false,
            require_last_push_approval: false,
            required_approving_review_count: 0,
            required_review_thread_resolution: false
          }
        },
        {
          type: "required_status_checks",
          parameters: {
            strict_required_status_checks_policy: true,
            do_not_enforce_on_create: false,
            required_status_checks: $checks
          }
        }
      ],
      bypass_actors: []
    }' > "$payload"

  ruleset_id="$(
    gh api --paginate "repos/$REPO/rulesets" \
      --jq ".[] | select(.name == \"$name\") | .id" | head -n 1 || true
  )"

  if [[ -n "$ruleset_id" ]]; then
    echo "Updating Ruleset '$name' (ID: $ruleset_id)..."
    gh api --method PUT "repos/$REPO/rulesets/$ruleset_id" --input "$payload" >/dev/null
  else
    echo "Creating Ruleset '$name'..."
    gh api --method POST "repos/$REPO/rulesets" --input "$payload" >/dev/null
  fi

  echo "Applied: $name"
}

apply_ruleset "main"
apply_ruleset "dev"

echo
echo "Rulesets applied. Verify with:"
echo "gh api repos/$REPO/rulesets"
