import sys

from postmaster.app import PostmasterApp


def main() -> None:
    app = PostmasterApp()
    app.run()


if __name__ == "__main__":
    main()
