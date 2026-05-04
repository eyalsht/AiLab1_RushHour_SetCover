import urllib.request
import os

files = [
    "scp41.txt", "scp42.txt", "scp43.txt", "scp44.txt",
    "scp51.txt", "scp52.txt", "scp53.txt",
    "scpa1.txt", "scpa2.txt", "scpa3.txt"
]

base_url = "http://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/"
target_dir = os.path.join("data", "setcover")
os.makedirs(target_dir, exist_ok=True)

for file in files:
    url = base_url + file
    target_path = os.path.join(target_dir, file)
    if not os.path.exists(target_path):
        print(f"Downloading {file}...")
        try:
            urllib.request.urlretrieve(url, target_path)
            print(f"Saved to {target_path}")
        except Exception as e:
            print(f"Failed to download {file}: {e}")
    else:
        print(f"{file} already exists.")
