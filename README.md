# odev

Personal development helpers focused on git workflows

- [ghi](src/odev/git/hide/cli.py): Manage git local exclude patterns
- [odev-commit](src/odev/git/commit/cli.py): Create styled commits; add `-i/--ignore-emoji` to generate messages without emojis; add `-s/--signoff` to pass `git commit -s`; run `odev-commit reuse [-s]` or `odev-commit [-s] reuse` to commit with the last cached message
- [odev-commit-msg](src/odev/git/commit_msg_check/cli.py): Custom commit message checker
- [odev-pr-title-check](src/odev/git/pr_title_check/cli.py): Custom pull request title checker

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
          additional_dependencies: ['git+https://github.com/Noai-oss/odev.git@632bc674381247cea79f5b3565b73bd27fc212b8']
          # args: [-i]
          stages: [commit-msg]
  ```

  - `.github/workflows/pr-title-check.yml`

  ```yaml
  name: PR Title Check

  on:
    pull_request:
      types: [opened, edited, synchronize]
  
  jobs:
    check-title:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/setup-python@v6
          with:
            python-version: '3.13'

        - name: Install odev package
          run: python -m pip install git+https://github.com/Noai-oss/odev.git@632bc674381247cea79f5b3565b73bd27fc212b8
  
        - name: Check PR Title
          shell: bash -x -e -u -o pipefail {0}
          env:
            GITHUB_PULL_REQUEST_TITLE: ${{ github.event.pull_request.title }}
          run: |
            printf '%s\n' "$GITHUB_PULL_REQUEST_TITLE" > pr_title.txt
            # Add -i/--ignore-emoji after odev-pr-title-check to allow titles without emojis.
            odev-pr-title-check pr_title.txt
  ```
