from lxml import html
import requests
import shutil
import re
import html as html2
import demjson
from pprint import pprint
import os

def download_url(url, filename):
    if len(url):
        print(url)
        r = requests.get(url, stream=True)

        if r.status_code == 200:
            with open(filename, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            print("bad status")
        return r.status_code
    else:
        print("bad url")
        return -1


def download_vid(raw_html):
    tree = html.fromstring(raw_html)
    all_urls = re.findall('"(https://[^"]*?[.]jpg[^"]*)"', raw_html)
    all_def_vid_urls = re.findall('url:.?"([^"]*?[.]mp4[^"]*)"', raw_html)
    all_hd_vid_urls = re.findall('hd_src:.?"([^"]*)"', raw_html)
    all_sd_vid_urls = re.findall('sd_src:.?"([^"]*)"', raw_html)

    from requests.utils import requote_uri
    all_sd_vid_urls = list(set(all_sd_vid_urls))
    all_hd_vid_urls = list(set(all_hd_vid_urls))
    all_def_vid_urls = list(set(all_def_vid_urls))
    mvd = re.findall('require\("TimeSlice"\).guard\(\(function\(\){bigPipe\.onPageletArrive\(({.*?})\);}\)', raw_html)
    download_img = False
    if download_img:
        a = tree.xpath('//meta[@property="og:image"]')
        if len(a):
            url = a[0].get("content")
            download_url(url, "thumbnail.jpg")

        i = 0
        for url in all_urls:
            download_url(html2.unescape(url), "imagen"+str(i)+".jpg")
            i += 1
    sel_definition = "hd"
    hd_vids_count = len(all_hd_vid_urls)
    sd_vids_count = len(all_sd_vid_urls)
    def_vids_count = len(all_def_vid_urls)
    from urllib.parse import urlparse
    if sel_definition == "hd":
        if hd_vids_count:
            print("trying with hd urls")
            failed_vids = []
            success_vids = []
            for url in all_hd_vid_urls:
                a = urlparse(url)
                filename = os.path.basename(a.path)
                print("downloading hd:", filename)
                status = download_url(requote_uri(url), filename)
                if status != 200:
                    print("failed")
                    failed_vids.append(filename)
                else:
                    print("success")
                    success_vids.append(filename)
            if len(failed_vids):
                if sd_vids_count:
                    failed_vids2 = []
                    for url in all_sd_vid_urls:
                        a = urlparse(url)
                        filename = os.path.basename(a.path)
                        if filename not in failed_vids:
                            continue
                        print("downloading sd:", filename)
                        status = download_url(requote_uri(url), filename)
                        if status != 200:
                            print("failed")
                            failed_vids2.append(filename)
                        else:
                            print("success")
                            success_vids.append(filename)
                    if len(failed_vids2):
                        if def_vids_urls:
                            failed_vids3 = []
                            for url in all_def_vid_urls:
                                a = urlparse(url)
                                filename = os.path.basename(a.path)
                                print("downloading default:", filename)
                                status = download_url(requote_uri(url), filename)
                                if status != 200:
                                    failed_vids3.append(filename)
                                else:
                                    success_vids.append(filename)
                            if len(failed_vids3):
                                for v in failed_vids3:
                                    print("failed to download", v)
                        else:
                            for v in failed_vids2:
                                print("failed to download:", v)
                        
                
        else:
            print("hd urls not found, trying sd")
            if sd_vids_count:
                failed_vids = []
                success_vids = []
                for url in all_sd_vid_urls:
                    a = urlparse(url)
                    filename = os.path.basename(a.path)
                    print("downloading sd:", filename)
                    status = download_url(requote_uri(url), filename)
                    if status != 200:
                        print("failed")
                        failed_vids.append(filename)
                    else:
                        print("success")
                        success_vids.append(filename)
                if len(failed_vids):
                    for f in failed_vids:
                        print("failed todownload:", f)
            else:
                print("no video found")

    elif sel_definition == "sd":
        if sd_vids_count:
            i = 0
            for url in all_hd_vid_urls:
                download_url(url, "video_hd"+str(i)+".mp4")
                i += 1
        else:
            if hd_vids_count:
                i = 0
                for url in all_hd_vid_urls:
                    input()
                    print(i)
                    download_url(requote_uri(url), "video_sd"+str(i)+".mp4")
                    i += 1
            else:
                i  = 0
                for url in all_def_vid_urls:
                    input()
                    print(i)
                    download_url(requote_uri(url), "video_def"+str(i)+".mp4")
                    i += 1


r = requests.get(input("ingrese url: "))
raw_html = r.text
video_paths = re.findall('video_path:.?"([^"]*)"', raw_html)
print(video_paths)
for v in video_paths:
    uri = "https://www.facebook.com"+v
    r = requests.get(uri)
    print("Downloading vid:", v)
    download_vid(r.text)

