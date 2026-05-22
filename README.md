# odev

Personal development helpers focused on git workflows

- [ghi](src/odev/git/hide/cli.py): Manage git local exclude patterns
- [odev-commit-msg](src/odev/git/commit_msg_check/cli.py): Custom commit message checker

  - `.pre-commit-config.yaml`

  ```yaml
  default_install_hook_types:
    # - pre-commit
    - commit-msg

  repos:
    - repo: local
      hooks:
        - id: commit-style-check
          name: Custom commit message style check
          entry: odev-commit-msg
          language: python
          additional_dependencies: ['git+https://github.com/Noai-oss/odev.git@e31e40245c74e14f9ee8ce1b08593cce5d319bde']
          stages: [commit-msg]
  ```

  - `.github/workflows/pr-title-check.yaml`

  ```yaml
  name: PR Title Check

  on:
    pull_request:
      types: [opened, edited, synchronize]
  
  jobs:
    check-title:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v6
          with:
            fetch-depth: 1
            persist-credentials: false
  
        - name: Setup uv
          uses: astral-sh/setup-uv@v7
  
        - name: Check PR Title
          shell: bash -x -e -u -o pipefail {0}
          env:
            GITHUB_PULL_REQUEST_TITLE: ${{ github.event.pull_request.title }}
          run: |
            printf '%s\n' "$GITHUB_PULL_REQUEST_TITLE" > pr_title.txt
            uvx --from git+https://github.com/Noai-oss/odev.git@e31e40245c74e14f9ee8ce1b08593cce5d319bde odev-commit-msg pr_title.txt
  ```
