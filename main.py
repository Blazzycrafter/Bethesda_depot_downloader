import os
import json
import zipfile
import urllib.request


skip_depot = False
useLocalBethesda = False
DEBUG = True


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






def main():
    init()
    # ask = input("enter Depot Repo URL: ")

    ### OVERRIDE:
    ask = "https://github.com/Blazzycrafter/BethesdaDepotRepo"
    maintainer, repo = parseRepoUrl(ask)
    repo = "https://raw.githubusercontent.com/" + maintainer + "/" + repo + "/main/masterManifest.json"
    if not useLocalBethesda:
        manifest = json.loads(urllib.request.urlopen(repo).read())
        gamelist = []
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

    else:
        manifest = json.loads(open("local.json").read())

    steam_data = parse_bethesda_manifest(manifest)
    print(steam_data)
    # prepare for download
    depot_dir = f"{selectGame}_{selectVersiom}"
    if not os.path.exists(depot_dir):
        os.mkdir(depot_dir)

    if os.path.exists(".DepotDownloader"):
        # move to depot dir
        os.rename(".DepotDownloader", f"{depot_dir}/.DepotDownloader")

    user_credentials = dict()
    user_credentials['username'] = input("Steam Username: ")
    user_credentials['password'] = ""
    steam_data.update(user_credentials)
    if not skip_depot:
        download_depot(steam_data=steam_data, user_credentials=user_credentials, depot_dir=depot_dir)
    # clean up
    if os.path.exists(f"{depot_dir}/.DepotDownloader"):
        # move from depot dir
        os.rename(f"{depot_dir}/.DepotDownloader", ".DepotDownloader")

    print(f"{BColors.OKGREEN}Done{BColors.ENDC}")


def download_depot2(username : str, appid: int, Selected_depots, depot_dir: str = "depot"):
    if not os.path.exists(depot_dir):
        os.mkdir(depot_dir)

    for depot_info in Selected_depots:
        command = f'DepotDownloader.exe -app {appid} -dir "{depot_dir}" -depot {depot_info["Depot"]} -manifest {depot_info["Manifest"]} -username {username} -remember-password'
        print(command)
        os.system(command)


def rdebug():
    manifest = json.loads(open("local.json").read())
    Selected_depots = json.loads("[]")

    for i in manifest["SteamData"]["Base"]:
        Selected_depots.append({"Manifest": i["ManifestId"], "Depot": i["DepotId"]})

    enabled_dlcs = []
    while True:
        os.system("cls")
        C = 1
        # menu of DLCs
        for i in manifest["SteamData"]["DLC"]:
            print(f"{BColors.OKBLUE}{C}. ",end="")
            if i["Name"] not in enabled_dlcs:
                print(BColors.FAIL,end="")
            else:
                print(BColors.OKGREEN,end="")
            print(f"{i['Name']} {BColors.ENDC}")
            C += 1

        select_dlc = input("select dlc (type c for continue and x for exit): ")

        if select_dlc == "c":
            break
        elif select_dlc == "x":
            exit(-1)
        elif select_dlc.isdigit():
            if int(select_dlc) in range(1, C):
                if manifest["SteamData"]["DLC"][int(select_dlc) - 1]["Name"] not in enabled_dlcs:
                    enabled_dlcs.append(manifest["SteamData"]["DLC"][int(select_dlc) - 1]["Name"])
                else:
                    enabled_dlcs.remove(manifest["SteamData"]["DLC"][int(select_dlc) - 1]["Name"])

    # Language menu
    enabled_languages = []
    while True:
        os.system("cls")
        C = 1
        for i in manifest["Languages"]:
            print(f"{BColors.OKBLUE}{C}. ",end="")
            if i not in enabled_languages:
                print(BColors.FAIL,end="")
            else:
                print(BColors.OKGREEN,end="")
            print(f"{i} {BColors.ENDC}")
            C += 1

        select_language = input("select language (type c for continue and x for exit): ")

        if select_language == "c":
            break
        elif select_language == "x":
            exit(-1)
        elif select_language.isdigit():
            if int(select_language) in range(1, C):
                if manifest["Languages"][int(select_language) - 1] not in enabled_languages:
                    enabled_languages.append(manifest["Languages"][int(select_language) - 1])
                else:
                    enabled_languages.remove(manifest["Languages"][int(select_language) - 1])

        # select depots phase
    print(f"{BColors.OKGREEN}Selecting depots...{BColors.ENDC}")
    # json.dumps(manifest["SteamData"]["DLC"], indent=4)
    for dlc in manifest["SteamData"]["DLC"]:
        if dlc["Name"] in enabled_dlcs:
            # add to Selected_depots
            Selected_depots.append({"Manifest": dlc["ManifestId"], "Depot": dlc["DepotId"]})

    for lang in enabled_languages:
        # select language
        langO = manifest["SteamData"]["Language"][lang]
        for i in langO:
            if i["type"] == "Base":
                # add to Selected_depots
                Selected_depots.append({"Manifest": i["ManifestId"], "Depot": i["DepotId"]})
            elif i["type"] in enabled_dlcs:
                # add to Selected_depots
                Selected_depots.append({"Manifest": i["ManifestId"], "Depot": i["DepotId"]})

    print(f"{BColors.OKGREEN}Downloading...{BColors.ENDC}")
    print(f'{BColors.HEADER} we need an steam account to download{BColors.ENDC}')
    print(f'{BColors.HEADER} please use steam login_name{BColors.ENDC}')
    print(f'{BColors.HEADER} and after that press enter{BColors.ENDC}')
    print(f'{BColors.HEADER} you may need to enter your password for steam login{BColors.ENDC}')
    username = input(f"{BColors.HEADER} username: {BColors.OKGREEN}")
    print(BColors.ENDC)
    download_depot2(username = username, Selected_depots=Selected_depots, depot_dir="depot", appid=manifest["SteamData"]["AppID"])







def rdebug2():
    pass



if __name__ == '__main__':
    if not DEBUG:
        main()
    else:
        rdebug()