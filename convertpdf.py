#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

import img2pdf
import requests as requests
from bs4 import BeautifulSoup

CURRENT = os.path.dirname(__file__)
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/94.0.4606.61 Safari/537.36 '
}


def download_images(url):
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'html.parser')

    slide_name = os.path.basename(url)
    slide_title = soup.find('title').text
    slides = soup.findAll('div', {'class': 'slide'})
    slide_files = []

    # Create images directory
    os.mkdir(slide_name)

    for slide in slides:
        sources = slide.find('source').get('srcset').split(', ')
        hq_src = None
        hq_size = 0
        slide_no = int(slide.get('data-index'))
        for src in sources:
            if int(src.split(' ')[1].replace('w', '')) > hq_size:
                hq_size = int(src.split(' ')[1].replace('w', ''))
                hq_src = src.split(' ')[0].rsplit('?', 1)[0]
        print(f'[Slide #{slide_no}] Size: {hq_size}, Src: {hq_src}')
        raw_img = requests.get(hq_src, headers=REQUEST_HEADERS).content
        with open(slide_name + '/' + os.path.basename(hq_src), 'wb') as f:
            f.write(raw_img)
        slide_files.insert(slide_no, slide_name + '/' + os.path.basename(hq_src))
    global pdf_f
    pdf_f = slide_title + '.pdf'
    convert_pdf(slide_files)


def convert_pdf(img_files_array):
    pdf_bytes = img2pdf.convert(img_files_array)
    doc = open(pdf_f, 'wb')
    doc.write(pdf_bytes)
    doc.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = " ".join(sys.argv[1:])
        if len(sys.argv) > 2 and sys.argv[2].lower() == '--del':
            del_tmp = True
        else:
            del_tmp = False
    else:
        url = input('Slideshare URL: ').strip()
        del_tmp = input('Do you want to delete temp folder?[Y/n]: ').lower().split()[0] == 'y'
    if (url.startswith("'") and url.endswith("'")) or (url.startswith('"') and url.endswith('"')):
        url = url[1:-1]
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    pdf_f = re.sub('[^0-9a-zA-Z]+', '_', url.split("/")[-1])  # get url basename and replace non-alpha with '_'
    if pdf_f.strip() == '':
        print("Something wrong to get filename from URL, fallback to result.pdf")
        pdf_f = "result.pdf"
    else:
        pdf_f += ".pdf"
    download_images(url)
    print('Download Complete!!')
    if del_tmp and os.path.exists(os.path.basename(url)):
        for file in os.listdir(path=os.path.basename(url)):
            os.remove(os.path.basename(url)+'/'+file)
        os.removedirs(os.path.basename(url))
        print('All temp file deleted!!')
