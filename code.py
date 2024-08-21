import time
import sdcardio
import board
import busio
import digitalio
import storage
import os
import supervisor

# Setup SPI and SD card
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_flash = board.D10

spiflash = sdcardio.SDCard(spi, cs_flash)
vfs = storage.VfsFat(spiflash)
storage.mount(vfs, "/sd")

print("Ready to receive commands")

def list_files(directory):
    files = []
    for item in os.listdir(directory):
        path = directory + "/" + item
        try:
            with open(path, 'r'):
                files.append("File: " + path)
        except OSError:
            files.append("Directory: " + path)
            files.extend(list_files(path))
    return files

def test(file_name):
    try:
        with open("/sd/" + file_name, "r") as f:
            print("Reading from sd card")
            while True:
                line = f.readline()
                if not line:
                    break
                print(line.strip())
     
    except OSError as e:
        print("Failed to read file:", e)



while True:
    if supervisor.runtime.serial_bytes_available:
        command = input().strip()
        if command == "LIST":
            try:
                print("Listing files...")  # Debug print
                files = list_files("/sd")
                for file in files:
                    print(file)
                print("Done listing files.")  # Debug print
            except OSError as e:
                print("Failed to read SPI", e)

        elif command.startswith("DOWNLOAD"):
            try:
                file_name = command.split("_", 1)[1]  # Extract the file name
                test(file_name)
            except IndexError:
                print("Invalid command format. Use 'DOWNLOAD_<filename>'")
            except OSError as e:
                print("Failed to download file:", e)
            print("DONE")
    time.sleep(0.1)
