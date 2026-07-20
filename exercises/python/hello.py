from platform import python_version
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    print('pre-master-foundation is ready.')
    print(f'Python version:{python_version()}')
    print(f'Repository root:{repo_root}')


if __name__ == '__main__':
    main()