
#!/usr/bin/env python3
import subprocess
import os
import shutil

CONFIG_PATH = "/boot/firmware/config.txt"
BACKUP_PATH = "/boot/firmware/config_backup.txt"

def run(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def apt_install(pkg):
    run(f"sudo apt-get install -y {pkg}")

def pip_install(pkg):
    run(f"sudo pip3 install {pkg} --break-system-packages")

def backup_config():
    if os.path.exists(CONFIG_PATH):
        shutil.copy(CONFIG_PATH, BACKUP_PATH)
        print(f"Backed up {CONFIG_PATH} to {BACKUP_PATH}")

def edit_config(camera_model, spi_enabled, i2c_baud):
    lines = []
    with open(CONFIG_PATH, "r") as f:
        lines = f.readlines()

    updated = []
    for line in lines:
        if "dtparam=spi=" in line:
            continue
        if "camera_auto_detect" in line or "dtoverlay=" in line:
            continue
        updated.append(line)

    if spi_enabled:
        updated.append("dtparam=spi=on\n")
    else:
        updated.append("# dtparam=spi=on  # SPI disabled for PCB V1\n")

    updated.append("camera_auto_detect=0\n")
    updated.append(f"dtoverlay={camera_model}\n")
    updated.append("dtparam=i2c_arm=on\n")
    updated.append(f"dtparam=i2c_arm_baudrate={i2c_baud}\n")

    with open(CONFIG_PATH, "w") as f:
        f.writelines(updated)

def install_vosk_models():
    os.makedirs("voice_models", exist_ok=True)
    os.chdir("voice_models")

    models = {
        "eo": "https://alphacephei.com/vosk/models/vosk-model-small-eo-0.22.zip",
        "en": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    }

    for lang, url in models.items():
        zip_name = url.split("/")[-1]
        folder_name = zip_name.replace(".zip", "")

        if os.path.exists(folder_name):
            print(f"{lang.upper()} model already exists, skipping download.")
            continue

        print(f"Downloading {lang.upper()} model...")
        run(f"wget {url}")
        run(f"unzip {zip_name}")
        os.remove(zip_name)

    os.chdir("..")

def main():
    print("=== Aranea Robot Installer ===")

    pcb = input("Which PCB version are you using? [1/2]: ").strip()
    spi_enabled = pcb == "2"

    camera_model = input("Enter the camera model (e.g., ov5647 or imx219): ").strip()
    i2c_baud = "400000"

    print("\nUpdating apt packages...")
    run("sudo apt-get update")

    print("\nInstalling apt dependencies...")
    apt_install("i2c-tools python3-smbus libportaudio2 libcamera-apps")

    print("\nInstalling Python modules...")
    pip_install("sounddevice vosk numpy flask")

    print("\nBacking up and editing config.txt...")
    backup_config()
    edit_config(camera_model, spi_enabled, i2c_baud)

    print("\nDownloading Vosk models...")
    install_vosk_models()

    print("\nSetup complete. Please reboot your Raspberry Pi.")

if __name__ == "__main__":
    main()
