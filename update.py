#!/usr/bin/env python3
from requests import get
import json
import os

PAPER_ROOT = "https://api.papermc.io/v2/"
GEYSER_ROOT = "https://download.geysermc.org/v2/"


def version_to_int(version):
    version_parts = version.split('.')
    summary = 0
    power = 1
    for version_part in version_parts:
        power -= len(version_part)
        summary += int(version_part) * pow(10, power)
    return summary


def need_to_update(installed_version, version, build):
    if installed_version is None:
        return True
    installed_value = version_to_int(f"{installed_version['version']}.{installed_version['build']}")
    latest_value = version_to_int(f"{version}.{build}")
    return latest_value > installed_value


def update_paper(paper_version):
    # Paper Update
    print("Updating Paper...")
    # Fetch the latest minecraft version
    mc_version = get(f"{PAPER_ROOT}projects/paper").json()["versions"][-1]
    print("Found", mc_version, "version. Fetching builds...")
    # Fetch latest paper build
    latest_paper = get(f"{PAPER_ROOT}projects/paper/versions/{mc_version}").json()["builds"][-1]
    print("Found", latest_paper, "for minecraft version", mc_version)
    # Check Need To Update
    if not need_to_update(paper_version, mc_version, latest_paper):
        print("Paper is up to date")
        return paper_version
    # Download the latest paper build
    print("Downloading the new paper....")
    paper_resp = get(
        f"{PAPER_ROOT}projects/paper/versions/{mc_version}/builds/{latest_paper}/downloads/paper-{mc_version}-{latest_paper}.jar")
    open("server/paper.jar", "wb").write(paper_resp.content)
    print("Paper updated successfully")
    return {'version': mc_version, 'build': latest_paper}


def update_geyser(geyser_version):
    print("Updating Geyser...")
    # Fetch the latest geyser build
    geyser_build_info = get(f"{GEYSER_ROOT}projects/geyser/versions/latest/builds/latest").json()
    version = geyser_build_info["version"]
    build = geyser_build_info["build"]
    print("Found", f"{version}:{build}", "version.")
    # Check need to update
    if not need_to_update(geyser_version, version, build):
        print("Geyser is up to date")
        return geyser_version
    # Download the latest paper build
    paper_resp = get(
        f"{GEYSER_ROOT}projects/geyser/versions/{version}/builds/{build}/downloads/standalone")
    open("geyser/geyser.jar", "wb").write(paper_resp.content)
    print("Geyser updated successfully")
    return {'version': version, 'build': build}


if __name__ == "__main__":
    VERSION_JSON = "version.json"
    print("Starting fetch and download updates...")
    if os.path.exists(VERSION_JSON):
        versions = json.load(open(VERSION_JSON, "r"))
        versions["paper"] = update_paper(versions["paper"])
        versions["geyser"] = update_geyser(versions["geyser"])
        json.dump(versions, open(VERSION_JSON, "w"))
    else:
        paper = update_paper(None)
        geyser = update_geyser(None)
        json.dump({'paper': paper, 'geyser': geyser}, open(VERSION_JSON, "w"))
