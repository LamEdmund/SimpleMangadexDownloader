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

def download(host: str, chapter_hash: str, quality: str, page: str, path: str, skip: bool):
    '''
    Download a single page from a chapter.

    Make a request for page url using metadata from chapter's image delivery metadata
    then writes it into a folder (created if it doesn't exist).
    
    Args:
        host: Base url
        chapter_hash: Chapter id
        quality: Data or data-saver
        page: Page metadata
        path: Dir to save image to
        skip: Skip pages that already exists
    '''

    ''' TODO 
    https://api.mangadex.org/docs/retrieving-chapter/
    Sometimes, a request for an image will fail. There can be many reasons for that. 
    Typically it is caused by an unhealthy MangaDex@Home server. In order to keep track 
    of the health of the servers in the network and to improve the quality of service and
    reliability, we need you to report successes and failures when loading images.
    The MangaDex@Home report endpoint is for this. For each image you retrieve (successfully or not)
    from a base url that doesn't contain mangadex.org
    
    - Call the network report endpoint to notify it (see just below)
    - Call the /at-home/server/:chapterId endpoint again to get a new base url if it was a failure

    POST https://api.mangadex.network/report
    Content-Type: application/json
    '''
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
        logger.critical("ERROR, %s while retrieving page from [%s]", (r.status_code, r.url))
    
    time.sleep(5)

def downloadChapter(chapter_id: str, quality: int, skip: bool):
    '''
    Download a single Chapter.

    Makes a request for a chapter's image delivery metadata and passes it to download
    function. Creates a folder to store downloaded pages if sucessful.

    Args:
        chapter_id: Chapter id from manga feed
        quality: 0 = data 1 = data-saver
        skip: Skip pages that already exists
    '''

    # going to Mangadex@home for our data
    # /at-home/server/:chapter-id
    # admins don't like hardcoded baseurls
    logger.info("Retrieving chapter %s", (chapter_id))
    r = requests.get(f"{base_url}/at-home/server/{chapter_id}")

    if r.status_code == 200:
        folder_path = f"MDX-{chapter_id}"
        os.makedirs(folder_path, exist_ok=True)
        
        sys.stdout.write("Starting %s \n" % (chapter_id))
        r_json = r.json()

        host = r_json["baseUrl"]
        chapter_hash = r_json["chapter"]["hash"]
        data = r_json["chapter"]["data"]
        data_saver = r_json["chapter"]["dataSaver"]

        # Choose between source/original quality or compressed images
        if quality == 0:
            for page in data:
                download(host, chapter_hash, 'data', page, folder_path, skip)
        elif quality == 1:
            for page in data_saver:
                download(host, chapter_hash, 'data-saver', page, folder_path, skip)
    else:
        sys.stdout.write('\nERROR %s \n' % (str(r.status_code)))
        logger.critical("ERROR while retrieving chapter: %s", (r.status_code))

    sys.stdout.write("\nCompleted %s \n" % (chapter_id))
    logger.info("Completed chapter %s", (chapter_id))

def getChapterHash(request: requests.Response) -> list:
    '''
    Return a list of chapter id
    
    Args:
        request: Request obj for manga feed
    
    Returns:
        A list of chapter id
    '''

    return [chapter["id"] for chapter in request.json()["data"]]

def downloadManga(manga_id: str, quality: int, skip: bool):
    '''
    Download all manga chapters.

    Makes a request for a manga's feed metadata, filtered for English only.
    Calls downloadChapter() for each chapter in chapter_id.
    
    Args:
        manga_id: manga id
        quality: 0 = data 1 = data-saver
        skip: skip pages that already exists
    '''

    logger.info('Attempting to retrieve %s...', (manga_id))
    request = requests.get(base_url+'/manga/'+manga_id+'/feed',
                        params={'translatedLanguage[]': ["en"]}
                        )
    if request.status_code == 200:
        folder_path = f"Mangadex-{manga_id}"
        os.makedirs(folder_path, exist_ok=True)
        os.chdir(folder_path)

        chapter_Ids = getChapterHash(request)
        chapter_count = len(chapter_Ids)

        for i in range(0, chapter_count):
            sys.stdout.write('\n %s of %s chapters\n' % (i+1, chapter_count))
            downloadChapter(chapter_Ids[i], quality, skip)
    else:
        logger.critical("ERROR while retrieving manga: %s", (request.status_code))

def getMangaId(url: str) -> str:
    '''
    Extract manga id from the url.

    Args:
        url: mangadex url
    
    Returns:
        A string representing a manga id
    '''

    # TODO mangadex has a way of finding manga id by manga name
    return url.split('/')[4]

#downloadManga(getMangaId(manga_url), 1, True)
help(download)