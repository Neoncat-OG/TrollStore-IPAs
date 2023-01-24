from github import Github
import json

if __name__ == "__main__":
    with open("apps.json", "r") as f:
        data = json.load(f)

    # clear apps
    data["apps"] = []

    g = Github()
    repo = g.get_repo("swaggyP36000/TrollStore-IPAs")
    releases = repo.get_releases()

    for release in releases:
        date = release.created_at
        release_date = date.strftime("%m-%d-%Y")
        versionDate = date.strftime("%Y-%m-%d")

        print(release.title)

        # second oldest release date, folder is "Update"
        if release_date == "11-10-2022":
            release_date = "Update"

        for asset in release.get_assets():
            if (asset.name[-3:] != "ipa"):
                continue
            name = asset.name[:-4]
            try:
                app_name, version = name.split("-", 1)
            except:
                app_name = name
                version = "1.0"

            data["apps"].append(
                {
                    "name": app_name,
                    "version": version,
                    "versionDate": versionDate,
                    "size": asset.size,
                    "downloadURL": f"https://github.com/swaggyP36000/TrollStore-IPAs/releases/download/{release_date}/{asset.name}"
                }
            )

    # data["apps"] = sorted(data["apps"],
    #                       key=lambda k: k['versionDate'], reverse=True)

    with open('apps.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
