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
          additional_dependencies: ['git+https://github.com/Noai-oss/odev.git@cd36de80bdbfc5e9b2c84f15210823562b87aa9d']
          stages: [commit-msg]
  ```
