import subprocess
import argparse
from typing import List, Optional, Tuple
import re
from pathlib import Path
from termcolor import colored

# Replace these with their appropriate fields
ADB = "C:\\Users\\Nghi Nguyen\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe"
JADX = "C:\\Users\\Nghi Nguyen\\Documents\\jadx\\bin\\jadx.bat"
# fixed column widths and truncation
NAME_COL_W = 37
PATH_COL_W = 70


def parse_args() -> argparse.Namespace:
    """Define and parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Pull APK from connected Android device and decompile it."
    )
    parser.add_argument(
        "-p",
        "--package",
        dest="package",
        help="The package name of the app to pull and decompile.",
    )
    parser.add_argument(
        "-l",
        "--list-packages",
        dest="list_packages",
        action="store_true",
        help="List all installed packages on the connected device.",
    )
    parser.add_argument(
        "-f",
        "--filter",
        dest="filter",
        help="Filter string to narrow down listed packages.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir", 
        help="Directory to save the extracted APK contents.",
    )
    return parser.parse_args()


def list_packages(adb_path: str = ADB) -> List[str]:
    """Return a list of installed package names from the connected device."""
    cmd = [adb_path, "shell", "pm", "list", "packages", "-f"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return [ln for ln in result.stdout.strip().splitlines() if ln]


def get_apk_path(package: str, adb_path: str = ADB) -> Optional[str]:
    """Return the device path to the APK for `package`, or None if not found."""
    cmd = [adb_path, "shell", "pm", "path", package]
    result = subprocess.run(cmd, capture_output=True, text=True)
    apk_path = result.stdout.strip().replace("package:", "")
    return apk_path if apk_path else None


def pull_apk(apk_path: str, local_apk_path: str, adb_path: str = ADB) -> None:
    """Pull an APK from the device to the local filesystem."""
    cmd = [adb_path, "pull", apk_path, local_apk_path]
    subprocess.run(cmd, check=True)


def decompile_apk(local_apk_path: str, out_dir: str, jadx_path: str = JADX) -> None:
    """Decompile an APK using jadx into `out_dir`."""
    cmd = [jadx_path, "-d", out_dir, local_apk_path]
    subprocess.run(cmd)


def parse_package_entry(entry: str) -> Optional[Tuple[str, str]]:
    """Parse an entry line from `pm list packages -f`.

    Expected form: 'package:/path/to/base.apk=package.name'
    Returns (apk_path_on_device, package_name) or None.
    """
    m = re.match(r"package:(?P<apk>.*\.apk)=(?P<pkg>.+)", entry)
    if not m:
        return None
    return m.group("apk"), m.group("pkg")

def filter_packages(packages: List[str], filter_str: str) -> List[str]:
    """Filter the list of packages based on the filter string."""
    return [pkg for pkg in packages if filter_str.lower() in pkg.lower()]

def print_packages(packages: List[str]) -> None:
    for pkg in packages:
        parsed = parse_package_entry(pkg)
        if parsed:
            apk_path_on_device, pkg_name = parsed
        else:
            # fallback parsing if entry is unexpected
            if "=" in pkg:
                left, right = pkg.split("=", 1)
                apk_path_on_device = left.replace("package:", "")
                pkg_name = right
            else:
                apk_path_on_device = pkg.replace("package:", "")
                pkg_name = ""

        def trunc(string: str, width: int) -> str:
            # if the string is longer than width, truncate and add "..."
            return string if len(string) <= width else string[: width - 3] + "..."

        # pad the string for table neatness. 
        name_display = trunc(pkg_name, NAME_COL_W).ljust(NAME_COL_W)
        path_display = trunc(apk_path_on_device, PATH_COL_W).ljust(PATH_COL_W)

        print(
            colored("| ", "cyan")
            + colored(name_display, "white")
            + colored(" | ", "cyan")
            + colored(path_display, "white")
            + colored(" |", "cyan")
        )

def main() -> None:
    args = parse_args()

    # List packages if arg supplied
    if args.list_packages:
        try:
            packages = list_packages()
            print(colored("| Package Name \t\t\t\t| Path on Device\t\t\t\t\t\t\t|", "cyan"))
            print(colored("-"*114, "cyan"))
            if args.filter:
                packages = filter_packages(packages, args.filter) 
            print_packages(packages)
        except subprocess.CalledProcessError as e:
            print(f"Error listing packages: {e}")
        return

    package_name = args.package
    if not package_name:
        print(colored("No package supplied. Use -p/--package to specify a package, or -l to list packages.", "red"))
        return

    # Main flow: pull and decompile specified package(s)
    try:
        # prepare base output directory
        if args.output_dir:
            base_out = Path(args.output_dir)
        else:
            base_out = Path("mobile_dump")

        if not base_out.exists():
            base_out.mkdir(parents=True, exist_ok=True)
            print(colored(f"Created output directory {base_out}/", "green"))

        all_packages = list_packages()
        matching_packages = filter_packages(all_packages, package_name)
        if not matching_packages:
            print(colored(f"No packages found matching package name: {package_name}", "red"))
            return

        print(colored("Found matching packages:", "green"))
        for package in matching_packages:
            print(colored(f"\t> {package.replace('package:', '')}", "cyan"))

        confirmation = input(colored("Press (Y/y) and Enter to continue: ", "yellow"))
        if confirmation.lower() != 'y':
            print(colored("Operation cancelled by user.", "red"))
            return

        apk_dir = base_out.joinpath("apk_dump")
        apk_dir.mkdir(parents=True, exist_ok=True)
        decompiled_dir = base_out.joinpath("decompiled")
        decompiled_dir.mkdir(parents=True, exist_ok=True)

        for entry in matching_packages:
            parsed = parse_package_entry(entry)
            if not parsed:
                print(colored(f"Skipping unparsable entry: {entry}", "yellow"))
                continue

            apk_path_on_device, pkg_name = parsed
            local_apk_path = str(apk_dir.joinpath(f"{pkg_name}.apk"))

            try:
                pull_apk(apk_path_on_device, local_apk_path)
                print(colored(f"Pulled APK to {local_apk_path}", "green"))
            except subprocess.CalledProcessError as e:
                print(colored(f"Error pulling {pkg_name}: {e}", "red"))
                continue

            # decompile into per-package subdirectory
            out_path = str(decompiled_dir.joinpath( pkg_name))
            try:
                decompile_apk(local_apk_path, out_path)
                print(colored(f"Decompiled APK to {out_path}/", "green"))
            except subprocess.CalledProcessError as e:
                print(colored(f"Error decompiling {pkg_name} with jadx: {e}", "red"))
                continue
    except subprocess.CalledProcessError as e:
        print(colored(f"Error listing or querying packages: {e}", "red"))
        return


if __name__ == "__main__":
    main()
