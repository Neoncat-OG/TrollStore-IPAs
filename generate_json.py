from github import Github
import json
import argparse
import pandas as pd
from get_bundle_id import get_single_bundle_id
import os
import mistletoe
from bs4 import BeautifulSoup
from io import StringIO


def transform_object(original_object):
    transformed_object = {**original_object, 'apps': None}

    app_map = {}

    for app in original_object['apps']:
        name, bundle_identifier, version, version_date, size, download_url, developer_name, localized_description, icon_url = (
            app['name'], app['bundleIdentifier'], app['version'], app['versionDate'],
            app['size'], app['downloadURL'], app['developerName'], app['localizedDescription'], app['iconURL']
        )

        if name not in app_map:
            app_map[name] = {
                'name': name,
                'bundleIdentifier': bundle_identifier,
                'developerName': developer_name,
                'localizedDescription': localized_description,
                'iconURL': icon_url,
                'versions': [],
            }

        app_map[name]['versions'].append({
            'version': version,
            'date': version_date,
            'size': size,
            'downloadURL': download_url,
            'localizedDescription': localized_description,
        })

    for name, app_info in app_map.items():
        app_info['versions'].sort(key=lambda x: x['date'], reverse=True)

    transformed_object['apps'] = list(app_map.values())

    return transformed_object


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token", help="Github token")
    args = parser.parse_args()
    token = args.token

    with open("apps.json", "r") as f:
        data = json.load(f)

    if os.path.exists("bundleId.csv"):
        df = pd.read_csv("bundleId.csv")
    else: 
        df = pd.DataFrame(columns=["name", "bundleId"])

    md_df = None
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding='utf-8') as f:
            raw_md = f.read()
        html = mistletoe.markdown(raw_md)
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all('table')[1] # Must be 2nd table in markdown
        md_df = pd.read_html(StringIO(str(table)),keep_default_na=False)[0]
        md_df['App Name'] = md_df['App Name'].str.replace(' ', '').str.lower()

    # clear apps
    data["apps"] = []

    g = Github(token)
    repo = g.get_repo("swaggyP36000/TrollStore-IPAs")
    releases = repo.get_releases()

    for release in releases:
        print(release.title)

        for asset in release.get_assets():
            if (asset.name[-3:] != "ipa"):
                continue
            name = asset.name[:-4]
            date = asset.created_at.strftime("%Y-%m-%d")
            try:
                app_name, version = name.split("-", 1)
            except:
                app_name = name
                version = "1.0"

            if app_name in df.name.values:
                bundle_id = str(df[df.name == app_name].bundleId.values[0])
            else:
                bundle_id = get_single_bundle_id(asset.browser_download_url)
                df = pd.concat([df, pd.DataFrame(
                    {"name": [app_name], "bundleId": [bundle_id]})], ignore_index=True)
                
            desc = ""
            dev_name = ""
            if md_df is not None:
                row = md_df.loc[md_df['App Name'] == app_name.replace(' ', '').lower()]
                if len(row.values):
                    raw_desc = row['Description'].values[0]
                    raw_last_updated = row['Last Updated'].values[0]
                    desc = f'{raw_desc}\nLast updated: {raw_last_updated}'
                    dev_name = f"{row['Source/Maintainer'].values[0]}"

            data["apps"].append(
                {
                    "name": app_name,
                    "bundleIdentifier": bundle_id,
                    "version": version,
                    "versionDate": date,
                    "size": asset.size,
                    "downloadURL": asset.browser_download_url,
                    "developerName": dev_name,
                    "localizedDescription": desc,
                    "iconURL": f"https://raw.githubusercontent.com/swaggyP36000/TrollStore-IPAs/main/icons/{bundle_id}.png"
                }
            )

    df.to_csv("bundleId.csv", index=False)

    with open('apps.json', 'w') as json_file:
        json.dump(data, json_file, indent=2)

    with open('apps.json', 'r') as file:
        original_object = json.load(file)

    transformed_object = transform_object(original_object)
    
    with open('apps.json', 'w') as file:
        json.dump(transformed_object, file, indent=2)
