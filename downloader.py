import requests
import time
import os
import sys
import logging

# Create and configure logger
logging.basicConfig(filename="downloader.log",
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# The offical test manga for mangadex
test_manga_url = 'https://mangadex.org/title/f9c33607-9180-4ba6-b85c-e4b5faee7192/official-test-manga'
base_url = 'https://api.mangadex.org'
manga_url = 'https://mangadex.org/title/7dc523b0-8ecd-40b0-b86c-1ea57c07773c/all-you-need-is-kill'

def download(host, chapter_hash, quality, page, path, skip):
    if os.path.exists(f"{path}/{page}") and skip:
        sys.stdout.write('Skipping %s\n' % (page))
        logger.warning("Skipping %s", (page))
        return None
    r = requests.get(f"{host}/{quality}/{chapter_hash}/{page}")
    sys.stdout.write('Retrieving [%s] \r' %(page))

    if r.status_code == 200:
        f = open(f"{path}/{page}", mode="wb")
        f.write(r.content)
        f.close()

    # we're in trouble...
    else:
        sys.stdout.write('\nERROR %s \n' % (str(r.status_code)))
        logger.critical("ERROR while retrieving page: %s", (r.status_code))
    
    time.sleep(1)

# Download entire Chapter
def downloadChapter(chapter_id, quality, skip):
    folder_path = f"Mangadex-{chapter_id}"
    os.makedirs(folder_path, exist_ok=True)

    # going to Mangadex@home for our data
    logger.info("Retrieving chapter %s", (chapter_id))
    r = requests.get(f"{base_url}/at-home/server/{chapter_id}")
    if r.status_code == 200:
        sys.stdout.write("Starting %s \n" % (chapter_id))
        r_json = r.json()

        host = r_json["baseUrl"]
        chapter_hash = r_json["chapter"]["hash"]
        data = r_json["chapter"]["data"]
        data_saver = r_json["chapter"]["dataSaver"]

        if quality == 0: # png/raw
            for page in data:
                download(host, chapter_hash, 'data', page, folder_path, skip)
        elif quality == 1: # jpg
            for page in data_saver:
                download(host, chapter_hash, 'data-saver', page, folder_path, skip)
    else:
        sys.stdout.write('\nERROR %s \n' % (str(r.status_code)))
        logger.critical("ERROR while retrieving chapter: %s", (r.status_code))

    sys.stdout.write("\nCompleted %s \n" % (chapter_id))
    logger.info("Completed chapter %s", (chapter_id))

# create and return a list of chapter ID to go through
def getChapterHash(request):
    return [chapter["id"] for chapter in request.json()["data"]]

def downloadManga(manga_id, quality, skip):
    logger.info('Attempting to retrieve %s...', (manga_id))
    request = requests.get(base_url+'/manga/'+manga_id+'/feed',
                        params={'translatedLanguage[]': ["en"]}
                        )
    if request.status_code == 200:
        chapter_Ids = getChapterHash(request)
        chapter_count = len(chapter_Ids)
        for i in range(0, chapter_count):
            sys.stdout.write('\n %s of %s chapters\n' % (i+1, chapter_count))
            downloadChapter(chapter_Ids[i], quality, skip)
    else:
        logger.critical("ERROR while retrieving manga: %s", (request.status_code))

# using delimeter to acquire our manga id
# should be find as long as MDX doesn't change anything
def getMangaId(url):
    return url.split('/')[4]

downloadManga(getMangaId(manga_url), 1, True)