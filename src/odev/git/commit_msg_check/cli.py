from .check_commit_msg import commit_msg_hook
import sys


def hook_main():
    sys.exit(commit_msg_hook())
