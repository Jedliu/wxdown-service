from rich.layout import Layout


def make_layout() -> Layout:
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=10),
        Layout(name="main"),
    )
    layout['main'].split_row(
        Layout(name="service"),
        Layout(name="status"),
    )
    return layout
