import argparse
import time

from Combiner.combiner import combiner, get_all_attachments, get_unique_attachments, parse_message_file
from Downloader.downloader import download
import os

def reconstruct(messages1 : str, messages2 : str, output_folder: str):

    timer = time.time()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if not os.path.isdir(output_folder):
        output_folder = os.path.dirname(output_folder)

    combiner(messages1, messages2, os.path.join(output_folder, "messages.json"))
    attachments = get_all_attachments(parse_message_file(os.path.join(output_folder, "messages.json")))
    downloadfolder = os.path.join(output_folder, r"download")

    os.makedirs(downloadfolder, exist_ok=True)

    counter = 1

    print("\nDownloading attachments:")
    for att in attachments:
        try:

            if int(time.time() - timer) < 600 and counter % 9500 == 0:
                print("\n")
                print("\n")
                print("You have exceeded the download limit of Discord.")
                print(
                    "The program will automatically halt for 10 minutes, and resume once the limit is reset. Please be patient.")
                time.sleep(600)
                print("\n")
                print("\n")
            if int(time.time() - timer) > 600:
                timer = time.time()

            download(att, counter, downloadfolder)
            counter += 1
        except Exception as e:
            print(f"Download failed: {e}")

def main():

    parser = argparse.ArgumentParser(
        description="Reconstruct messages from message files"
    )

    parser.add_argument('--input_file_1', '-file1', type=str, required=True)
    parser.add_argument('--input_file_2', '-file2', type=str, required=True)
    parser.add_argument('--output_folder', '-folder', type=str, required=True)

    args = parser.parse_args()

    print("Reconstructing messages from message files:")
    reconstruct(args.input_file_1, args.input_file_2, args.output_folder)
    print("\nSuccessfully reconstructed messages from message files")

if __name__ == "__main__":
    main()