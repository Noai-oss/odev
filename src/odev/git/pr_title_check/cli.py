from .check_pr_title import pr_title_hook


def hook_main():
    raise SystemExit(pr_title_hook())


if __name__ == "__main__":
    hook_main()
