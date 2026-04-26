# odev

Personal development helpers focused on git workflows

- [ghi](src/odev/git/hide/cli.py): Manage git local exclude patterns
- [odev-commit-msg](src/odev/git/commit_msg_check/cli.py): Custom commit message checker

  ```yaml
  default_install_hook_types:
    - pre-commit
    - commit-msg

  repos:
    - repo: local
      hooks:
        - id: commit-style-check
          name: Custom commit message style check
          entry: uvx --from git+https://github.com/ooooo-create/odev.git@fc9b176312086175763b5410b50c5f8c7167a2f3 odev-commit-msg
          language: system
          stages: [commit-msg]
  ```
