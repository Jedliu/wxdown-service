from rich.panel import Panel
from rich.table import Table
import version
from pathlib import Path

SRC_PATH = Path.absolute(Path(__file__)).parent.parent
LOGO_FILE = str(SRC_PATH / 'resources' / 'logo.txt')


class Header:
    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")

        with open(LOGO_FILE) as file:
            logo = file.read()
        grid.add_row(
            logo,
            f"v{version.version}",
        )
        return Panel(
            grid,
            title="公众号下载助手 by Jock",
            title_align='left',
            border_style="bright_blue",
        )
