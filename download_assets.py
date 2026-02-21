import urllib.request
import os

sounds = {
    "snd_shoot.wav": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/snd/pew.wav",
    "snd_hit.wav": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/snd/expl3.wav",
    "snd_buy.wav": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/snd/pow4.wav",
    "snd_over.wav": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/snd/rumbling1.ogg",
    "snd_ketchup.wav": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/snd/expl6.wav",
    "snd_slow.wav": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/snd/pow5.wav",
}

def download_files():
    print("Downloading Audio Assets from KidsCanCode...")
    for filename, url in sounds.items():
        path = os.path.join("assets", "sounds", filename)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
                print(f"Downloaded {filename}")
        except Exception as e:
            print(f"Failed to download {filename} from {url}: {e}")

if __name__ == '__main__':
    download_files()
