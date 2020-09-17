# download data

# define files to download
files = [
    # 'http://atena.ijs.si/data/factlog/tupras_preliminary.zip',
    'http://atena.ijs.si/data/factlog/continental_preliminary.zip'
]

targets = [
    # '../../data/interim/tupras_preliminary.zip',
    '../../../data/interim/continental_preliminary.zip',
]

raw_targets = [
    # '../../data/raw/tupras',
    '../../../data/raw/continental',
]

import requests, zipfile, io, sys
def download_url(url, save_path, chunk_size=256 * 1024):
    print("Starting download", url)
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            sys.stdout.write('.')
            sys.stdout.flush()
            fd.write(chunk)
    print(" Finished.\n")


if __name__ == "__main__":
    # download files
    print("### DOWNLOADING TO INTERIM FOLDER ###")
    for i in range(len(targets)):
        download_url(files[i], targets[i])

    # unzipping
    print("### UNZIPPING TO RAW FOLDER ###")
    for i in range(len(targets)):
        with zipfile.ZipFile(targets[i], 'r') as zip_ref:
            print("Starting to unzip into", raw_targets[i])
            zip_ref.extractall(raw_targets[i])