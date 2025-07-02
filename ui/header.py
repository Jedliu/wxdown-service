from rich.panel import Panel
from rich.table import Table
import version
from pathlib import Path

# SRC_PATH = Path.absolute(Path(__file__)).parent.parent
# LOGO_FILE = str(SRC_PATH / 'resources' / 'logo.txt')

logo = r'''                     __
                    /\ \
 __  __  __  __  _  \_\ \    ___   __  __  __    ___
/\ \/\ \/\ \/\ \/'\ /'_` \  / __`\/\ \/\ \/\ \ /' _ `\
\ \ \_/ \_/ \/>  <//\ \L\ \/\ \L\ \ \ \_/ \_/ \/\ \/\ \
 \ \___x___/'/\_/\_\ \___,_\ \____/\ \___x___/'\ \_\ \_\
  \/__//__/  \//\/_/\/__,_ /\/___/  \/__//__/   \/_/\/_/
'''


class Header:
    def __init__(self, clients = 0, credentials = 0):
        self.clients = clients
        self.credentials = credentials

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")

        grid.add_row(
            logo,
            f"v{version.version}\n\n\n\n\n客户端数: {self.clients}\nCredentials: {self.credentials}",
        )
        return Panel(
            grid,
            title="公众号下载助手 by Jock",
            title_align='left',
            border_style="bright_blue",
        )
