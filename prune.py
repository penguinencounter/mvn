from pathlib import Path
from xml.etree import ElementTree
from rich.console import Console

snapshots = Path("./snapshots")
console = Console(color_system="standard", force_terminal=True)
rp = console.print


def collect_snapshots(root: Path):
    for root, _, _ in root.walk():
        if root.name.endswith("-SNAPSHOT"):
            yield root


def bytes(num: int):
    units = ["B", "kB", "MB", "GB", "TB"]
    ptr = 0
    while num > 1000 and ptr < len(units) - 1:
        ptr += 1
        num /= 1000
    if ptr == 0:
        return f"{num} {units[ptr]}"
    else:
        return f"{num:.2f} {units[ptr]}"


def sizeof(p: Path):
    total = sum((r/f).stat().st_size for r, _, fil in p.walk() for f in fil)
    return total


def prune_snapshot(sdir: Path):
    metafile = sdir / "maven-metadata.xml"
    # xml: ElementTree.Element
    with open(metafile, encoding="utf-8") as f:
        xml = ElementTree.fromstring(f.read())
    snap = next(xml.iter("snapshot"))
    timestamp = snap.find("timestamp").text
    shortname = str(sdir.relative_to(sdir.parent.parent))
    rp(f"[blue]{shortname:60}[/] : [yellow]t[bold]{timestamp}[/][/]")

    removed = 0
    for item in sdir.iterdir():
        if "maven-metadata" in item.name:
            continue
        if timestamp in item.name:
            continue
        itemsize = item.stat().st_size
        rp(f"  [red]- {item.name} ([bold]{bytes(itemsize)}[/])", highlight=False)
        removed += itemsize
        item.unlink()

    if removed == 0:
        rp("  [bright_black]+ everything up to date[/]")
    else:
        rp(f"  [green]+ freed [bold]{bytes(removed)}[/][/]")



def main():
    initial = sizeof(snapshots)
    rp(f"[green]initially [bold]{bytes(initial)}[/][/]")
    for snap in collect_snapshots(snapshots):
        prune_snapshot(snap)
    final = sizeof(snapshots)
    rp(f"[green]freed [bold]{bytes(initial - final)}[/] total[/]")


if __name__ == "__main__":
    main()
