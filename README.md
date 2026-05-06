# odev

Personal development helpers focused on git workflows

- [ghi](src/odev/git/hide/cli.py): Manage git local exclude patterns
- [odev-commit-msg](src/odev/git/commit_msg_check/cli.py): Custom commit message checker

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
          additional_dependencies: ['git+https://github.com/Noai-oss/odev.git@01f1da1c4261ea0d2071ca1453641a3bf665ed1d']
          stages: [commit-msg]
  ```
