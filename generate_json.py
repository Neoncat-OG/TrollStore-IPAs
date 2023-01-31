from github import Github
import json
import argparse
import pandas as pd


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token", help="Github token")
    args = parser.parse_args()
    token = args.token

    with open("apps.json", "r") as f:
        data = json.load(f)

    df = pd.read_csv("bundleId.csv")

    # clear apps
    data["apps"] = []

    g = Github(token)
    repo = g.get_repo("swaggyP36000/TrollStore-IPAs")
    releases = repo.get_releases()

    for release in releases:
        print(release.title)
        date = release.created_at.strftime("%Y-%m-%d")

        for asset in release.get_assets():
            if (asset.name[-3:] != "ipa"):
                continue
            name = asset.name[:-4]
            try:
                app_name, version = name.split("-", 1)
            except:
                app_name = name
                version = "1.0"

            bundle_id = df[df.name == app_name].bundleId.values[0]

            data["apps"].append(
                {
                    "name": app_name,
                    "bundleIdentifier": bundle_id,
                    "version": version,
                    "versionDate": date,
                    "size": asset.size,
                    "downloadURL": f"https://github.com/swaggyP36000/TrollStore-IPAs/releases/download/{release.tag_name}/{asset.name}",
                    "developerName": "",
                    "localizedDescription": "",
                    "iconURL": "about:blank"
                }
            )

    # data["apps"] = sorted(data["apps"],
    #                       key=lambda k: k['versionDate'], reverse=True)

    with open('apps.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
