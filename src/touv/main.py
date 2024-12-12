from pathlib import Path
import tomli
import tomli_w
from typer import Argument, Typer
from . import poetry

app = Typer(help=__doc__, pretty_exceptions_enable=False, no_args_is_help=True)


@app.command()
def main(path: Path = Argument(Path("."))) -> None:
    data = tomli.loads((path / "pyproject.toml").read_text())
    print(tomli_w.dumps(poetry.convert_pyproject_toml(data)))


if __name__ == "__main__":
    app()
