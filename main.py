import os
import json
import zipfile
import urllib.request




class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



def init():
    if not "DepotDownloader.exe" in os.listdir():
        print(f"{BColors.FAIL}DepotDownloader.exe not found{BColors.ENDC}")
        print("downloading...")
        try:
            os.system("wget https://github.com/SteamRE/DepotDownloader/releases/download/DepotDownloader_2.5.0/DepotDownloader-windows-x64.zip")
        except Exception as e:
            print(f"{BColors.FAIL}Failed to download DepotDownloader.exe{BColors.ENDC}")
            print(f"{BColors.FAIL}Error: {e}{BColors.ENDC}")
            exit(-1)

        try:
            zipfile.ZipFile("DepotDownloader-windows-x64.zip").extractall()
        except Exception as e:
            print(f"{BColors.FAIL}Failed to unzip DepotDownloader.exe{BColors.ENDC}")
            print(f"{BColors.FAIL}Error: {e}{BColors.ENDC}")
            exit(-1)
        os.remove("DepotDownloader-windows-x64.zip")
    else:
        print(f"{BColors.OKGREEN}DepotDownloader.exe found{BColors.ENDC}")


def parse_bethesda_manifest(manifest):
    """
    {
  "GameName": "Skyrim",
  "GameVersion": "1.3.667",
  "SteamData": {
    "AppId": 892970,
    "Manifests": [489, 777, 89, 559]
  }
}
    """
    return manifest['SteamData']


def download_depot(user_credentials, steam_data: dict, depot_dir: str = "depot", ):
    if not os.path.exists(depot_dir):
        os.mkdir(depot_dir)

    command = f'DepotDownloader.exe -app {steam_data["AppId"]} -dir "{depot_dir}"'
    command += " -username " + user_credentials['username']
    if user_credentials['password'] == "":
        command += " -remember-password "
    else:
        command += " -password " + user_credentials['password']
    for manifest_id in steam_data['Manifests']:
        command2 = command + f" -depot {manifest_id}"
        print(command2)
        os.system(command2)



def parseRepoUrl(repoUrl):
    x = repoUrl.split("/")
    return x[3], x[4]


if __name__ == '__main__':
    init()
    #ask = input("enter Depot Repo URL: ")

    ### OVERRIDE:
    ask = "https://github.com/Blazzycrafter/BethesdaDepotRepo"
    maintainer, repo = parseRepoUrl(ask)
    repo = "https://raw.githubusercontent.com/" + maintainer + "/" + repo + "/main/masterManifest.json"

    manifest = json.loads(urllib.request.urlopen(repo).read())
    gamelist =  []
    for game in manifest:
        if game['Game'] not in gamelist:
            gamelist.append(game['Game'])
        else:
            continue


    for game in gamelist:
        print(game)


    selectGame = input("select game: ")
    if selectGame not in gamelist:
        print(f"{BColors.FAIL}Game not found{BColors.ENDC}")
        exit(-1)

    for i in manifest:
        if i['Game'] == selectGame:
            for j in i['Versions']:
                print(j['Version'])

    selectVersiom = input("select version: ")
    for i in manifest:
        if i['Game'] == selectGame:
            for j in i['Versions']:
                if j['Version'] == selectVersiom:
                    manifest_ULI = j['URI']

    ## REUSE: manifest variable
    manifest = json.loads(urllib.request.urlopen(manifest_ULI).read())

    steam_data = parse_bethesda_manifest(manifest)
    print(steam_data)
    # prepare for download
    depot_dir = f"{selectGame}_{selectVersiom}"
    if not os.path.exists(depot_dir):
        os.mkdir(depot_dir)

    if os.path.exists(".DepotDownloader"):
        #move to depot dir
        os.rename(".DepotDownloader", f"{depot_dir}/.DepotDownloader")

    user_credentials = dict()
    user_credentials['username'] = input("Steam Username: ")
    steam_data.update(user_credentials)
    download_depot(steam_data=steam_data, user_credentials=user_credentials, depot_dir=depot_dir)
    # clean up
    if os.path.exists(f"{depot_dir}/.DepotDownloader"):
        #move from depot dir
        os.rename(f"{depot_dir}/.DepotDownloader", ".DepotDownloader")

    print(f"{BColors.OKGREEN}Done{BColors.ENDC}")
