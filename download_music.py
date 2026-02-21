import urllib.request
import os

sounds = {
    "bgm_action.ogg": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/snd/tgfcoder-FrozenJam-SeamlessLoop.ogg"
}

def download_music():
    print("Downloading Music Asset...")
    for filename, url in sounds.items():
        path = os.path.join("assets", "music", filename)
        # Verify dir exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
                print(f"Downloaded {filename}")
        except Exception as e:
            print(f"Failed to download {filename} from {url}: {e}")

if __name__ == '__main__':
    download_music()
