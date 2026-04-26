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
          entry: uvx --from git+https://github.com/ooooo-create/odev.git@f6eaffb7a7519513baa0c1828c72b4d5afa7acb7 odev-commit-msg
          language: system
          stages: [commit-msg]
  ```
