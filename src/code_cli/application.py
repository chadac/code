from cleo.application import Application

from code_cli.commands.git import GitCommand
from code_cli.commands.git_args import GitArgsCommand

cli = Application()

cli.add(GitCommand())
cli.add(GitArgsCommand())


def main():
    cli.run()


if __name__ == "__main__":
    main()
