import os
from typing import List
import sys
import zipfile
import shutil
import os
import subprocess
import glob
import tomlkit
# download the required .whl files for all platforms

required_packages = [
    "mrcfile==1.4.3",
    "starfile==0.5.6",
    "scipy",
    "MDAnalysis==2.6.0",
    "biotite==0.40.0",
]
supported_platforms = [
    "macosx_12_0_arm64",
    # "manylinux2014_28_x86_64",
    # "win_amd64",
    # "macosx_10_9_x86_64",
]


def run_python(args: str):
    python = os.path.realpath(sys.executable)
    subprocess.run([python] + args.split(" "))


def download_whls(
    python_version="3.11", packages=required_packages, platforms=supported_platforms
):
    for platform in platforms:
        run_python(
            f"-m pip download {' '.join(packages)} --dest ./molecularnodes/wheels --only-binary=:all: --python-version={python_version} --platform={platform}"
        )


toml_path = "molecularnodes/blender_manifest.toml"


def update_toml_whls(platform: str | None = None):
    # List all .whl files in the wheels/ subdirectory
    wheel_files = glob.glob("molecularnodes/wheels/*.whl")

    # Load the TOML file
    with open(toml_path, "r") as file:
        manifest = tomlkit.parse(file.read())

    # Update the wheels list
    manifest["wheels"] = wheel_files
    if platform:
        manifest["version"] = "{}-{}".format(manifest["version"], platform)
    manifest_str = (
        tomlkit.dumps(manifest)
        .replace('["', '[\n\t"')
        .replace('", "', '",\n\t"')
        .replace('"]', '",\n]')
        .replace("molecularnodes/", "./")
        .replace("\\\\", "/")
    )

    # Write the updated TOML file
    with open(toml_path, "w") as file:
        file.write(manifest_str)


def zip_extension(platform: str | None = None) -> None:
    # Load the TOML file
    with open(toml_path, "r") as file:
        manifest = tomlkit.parse(file.read())

    # Get the version number
    version = manifest["version"].split("-")[0]

    if platform:
        # Define the zip file name
        zip_file_name = f"molecularnodes_{version}_{platform}.zip"
    else:
        zip_file_name = f"molecularnodes_{version}.zip"

    # Create the zip file
    with zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Walk the molecularnodes folder
        for root, dirs, files in os.walk("molecularnodes"):
            for file in files:
                # Get the file path
                file_path = os.path.join(root, file)

                # Add the file to the zip file
                zip_file.write(
                    file_path, arcname=os.path.relpath(file_path, "molecularnodes")
                )


def remove_whls():
    dir_path = ".molecularnodes/wheels"
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)


def build(platform: str | None = None) -> None:
    download_whls(platforms=[platform])
    update_toml_whls(platform=platform)
    zip_extension(platform=platform)
    remove_whls()


if __name__ == "__main__":
    for platform in supported_platforms:
        build(platform)
