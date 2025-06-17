from rich.layout import Layout


def make_layout() -> Layout:
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=10),
        Layout(name="main", ratio=1, minimum_size=10),
        Layout(name="footer", ratio=1, minimum_size=10),
    )
    return layout
