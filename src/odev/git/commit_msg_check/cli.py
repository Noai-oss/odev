from .check_commit_msg import commit_msg_hook


def hook_main():
    raise SystemExit(commit_msg_hook())


if __name__ == "__main__":
    hook_main()
