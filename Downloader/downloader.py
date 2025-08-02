import os
import sys
import urllib.request

def download(url : str, counter: int, output_filepath : str = None):

    filename = url.split('/')[-1].split('?')[0]

    if output_filepath is None:
        output_filepath = filename
    elif os.path.isdir(output_filepath):
        output_filepath = os.path.join(output_filepath, filename)

    path = output_filepath
    head, sep, tail = path.rpartition('\\')
    path = head + sep + f"[{counter}]" + tail

    if os.path.exists(path):
        sys.stdout.write(f"\rDownloaded {counter} files")
        sys.stdout.flush()
        return output_filepath


    for attempt in range(1):
        try:
            req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9'
        })
            with urllib.request.urlopen(req) as response:
                with open(path, 'wb') as f:
                    f.write(response.read())
            sys.stdout.write(f"\rDownloaded {counter} files")
            sys.stdout.flush()
            urllib.request.urlretrieve(url, path)
            return output_filepath
        except urllib.error.HTTPError as e:
            #if e.code == 403:
            #    print(f"Attempt {attempt + 1} failed to download {filename} at {url}: {e}")
            #else:
            #    print(f"HTTP Error {e.code}: {url}")
            # //// HERE ERRORS FOR SOME REASON ACTUALLY AREN'T ERRORS ////
            continue
        except Exception as e:
            print(f"\nSomething went wrong {e}\n\n")
            continue
    return None


