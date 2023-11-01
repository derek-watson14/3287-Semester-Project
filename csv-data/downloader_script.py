import os
import requests
import time


def download_files(url_list, folder):
    """
    Downloads files from a list of URLs and saves them to a specified folder.

    Parameters:
    - url_list: List of URLs to download.
    - folder: Folder to save downloaded files.
    """

    # Ensure the folder exists or create it
    if not os.path.exists(folder):
        os.makedirs(folder)

    for url in url_list:
        response = requests.get(url, stream=True)
        # Extract the filename from the URL
        name = url.split("/")[-1].split(".")[0] + "-" + url.split("/")[-2] + ".csv"
        filename = os.path.join(folder, name)

        # Save the content to the file
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        # Wait 3 seconds to avoid overloading the server
        time.sleep(3)
        print(f"File {name} downloaded!")

    print("All files downloaded!")


base_url = "https://www.football-data.co.uk/mmz4281"

# All seasons from 02/03 to 22/23
seasons = [
    {"season": "2022/2023", "code": "2223"},
    {"season": "2021/2022", "code": "2122"},
    {"season": "2020/2021", "code": "2021"},
    {"season": "2019/2020", "code": "1920"},
    {"season": "2018/2019", "code": "1819"},
    {"season": "2017/2018", "code": "1718"},
    {"season": "2016/2017", "code": "1617"},
    {"season": "2015/2016", "code": "1516"},
    {"season": "2014/2015", "code": "1415"},
    {"season": "2013/2014", "code": "1314"},
    {"season": "2012/2013", "code": "1213"},
    {"season": "2011/2012", "code": "1112"},
    {"season": "2010/2011", "code": "1011"},
    {"season": "2009/2010", "code": "0910"},
    {"season": "2008/2009", "code": "0809"},
    {"season": "2007/2008", "code": "0708"},
    {"season": "2006/2007", "code": "0607"},
    {"season": "2005/2006", "code": "0506"},
    {"season": "2004/2005", "code": "0405"},
    {"season": "2003/2004", "code": "0304"},
    {"season": "2002/2003", "code": "0203"},
]

# All countries and leagues
countries = {
    "England": [("E0", "Premier League", "premierleague"), ("E1", "Championship", "championship")],
    "France": [("F1", "Ligue 1", "ligue1"), ("F2", "Ligue 2", "ligue2")],
    "Germany": [("D1", "1. Bundesliga", "bundesliga"), ("D2", "2. Bundesliga", "2bundesliga")],
    "Italy": [("I1", "Serie A", "seriea"), ("I2", "Serie B", "serieb")],
    "Spain": [("SP1", "La Liga", "laliga"), ("SP2", "La Liga 2", "laliga2")],
    "Netherlands": [("N1", "Eredivisie", "eredivisie")],
    "Portugal": [("P1", "Liga Portugal", "ligaportugal")],
}


def generate_url_list():
    """
    Generates a list of URLs to download.
    """

    url_list = []

    for season in seasons:
        for country in countries:
            for league in countries[country]:
                url = f"{base_url}/{season['code']}/{league[0]}.csv"
                url_list.append(url)

    return url_list


url_array = generate_url_list()
download_folder = "downloaded_csvs"
download_files(url_array, download_folder)
