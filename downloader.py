import requests
import time
import os
import sys
import logging
#import json

# Create and configure logger
logging.basicConfig(filename="downloader.log",
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# The offical test manga for mangadex
# test_manga_url = 'https://mangadex.org/title/f9c33607-9180-4ba6-b85c-e4b5faee7192/official-test-manga'
base_url = 'https://api.mangadex.org'
# manga_url = 'https://mangadex.org/title/7dc523b0-8ecd-40b0-b86c-1ea57c07773c/all-you-need-is-kill'
post_url = 'https://api.mangadex.network/report'

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
    
    Returns:
        response status code
    '''

    if os.path.exists(f"{path}/{page}") and skip:
        sys.stdout.write('Skipping %s\n' % (page))
        logger.warning(f"Skipping {page}")
        return None
    
    r = requests.get(f"{host}/{quality}/{chapter_hash}/{page}")
    sys.stdout.write('Retrieving [%s] \r' %(page))

    # check if r.url is for main server or @home
    # report MDX@home server if used regardless of success or failure.
    # do not report main server
    if r.url.find('uploads.mangadex.org') < -1:
        data = {
            "url": r.url,
            "success": r.ok,
            "bytes": len(r.content),
            "duration": r.elapsed.total_seconds(),
            "cached": False
            }
        post = requests.post(post_url, json=data)
        logger.info(f'Post response: {post.text}')

    if r.status_code == 200:
        f = open(f"{path}/{page}", mode="wb")
        f.write(r.content)
        f.close()

    # we're in trouble...
    else:
        sys.stdout.write('\nERROR %s \n' % (str(r.status_code)))
        logger.critical(f"ERROR, {r.status_code} while retrieving page from [{r.url}]")
    
    time.sleep(5)
    return r.status_code

def downloadChapter(chapter_id: str, chapter_title:str, quality: str, skip: bool):
    '''
    Download a single Chapter.

    Makes a request for a chapter's image delivery metadata and passes it to download
    function. Creates a folder to store downloaded pages if sucessful.

    Args:
        chapter_id: Chapter id from manga feed
        chapter_title: name of chapter
        quality: data or data-saver
        skip: Skip pages that already exists
    '''

    # going to Mangadex@home for our data
    # /at-home/server/:chapter-id
    logger.info(f"Retrieving chapter {chapter_title}, ID = {chapter_id}")
    r = requests.get(f"{base_url}/at-home/server/{chapter_id}")

    if r.status_code == 200:
        folder_path = f"MDX-{chapter_title}-{chapter_id}"
        os.makedirs(folder_path, exist_ok=True)
        
        sys.stdout.write("Retrieving chapter: %s - %s \n" % (chapter_title, chapter_id))
        r_json = r.json()

        host = r_json["baseUrl"]
        chapter_hash = r_json["chapter"]["hash"]

        # Choose between source/original quality or compressed images
        if quality == 'data-saver':
            key = 'dataSaver'
        else:
            key = quality

        for page in r_json['chapter'][key]:
            rcode = download(host, chapter_hash, quality, page, folder_path, skip)

            # non 2xx response
            if rcode == 504:
                logger.warning(f"Error code {rcode}, retrying in 60s.")
                time.sleep(60)
                download(host, chapter_hash, quality, page, folder_path, skip)
    else:
        sys.stdout.write(f"ERROR while retrieving chapter: {r.status_code}")
        logger.critical(f"ERROR while retrieving chapter: {r.status_code}")

    sys.stdout.write(f"Completed chapter {chapter_id}")
    logger.info(f"Completed chapter {chapter_id}")

def getChapterHash(request: requests.Response) -> list:
    '''
    Return a list of chapter id
    
    Args:
        request: Request obj for manga feed
    
    Returns:
        A list of chapter id
    '''

    return [chapter["id"] for chapter in request.json()["data"]]

def getChapterName(request: requests.Response) -> list:
    '''
    Return a list of chapter names
    
    Args:
        request: Request obj for manga feed
    
    Returns:
        A list of chapter names
    '''

    return [chapter["attributes"]['title'] for chapter in request.json()["data"]]

def downloadManga(manga_id: str, quality: str, skip: bool):
    '''
    Download all manga chapters.

    Makes a request for a manga's feed metadata, filtered for English only.
    Calls downloadChapter() for each chapter in chapter_id.
    
    Args:
        manga_id: manga id
        quality: data or data-saver
        skip: skip pages that already exists
    '''

    logger.info(f"Attempting to retrieve {manga_id}...")
    request = requests.get(f'{base_url}/manga/{manga_id}/feed',
                        params={'translatedLanguage[]': ["en"]}
                        )
    if request.status_code == 200:
        manga_info = requests.get(f'{base_url}/manga/{manga_id}').json()['data']
        manga_title = manga_info['attributes']['title']['en']

        folder_path = f"Mangadex-{manga_title}-{manga_id}"
        os.makedirs(folder_path, exist_ok=True)
        os. chdir(folder_path)

        chapter_Ids = getChapterHash(request)
        chapterTitle = getChapterName(request)
        chapter_count = len(chapter_Ids)

        for i in range(0, chapter_count):
            sys.stdout.write('\n %s of %s chapters\n' % (i+1, chapter_count))
            downloadChapter(chapter_Ids[i], chapterTitle[i], quality, skip)
    else:
        logger.critical(f"ERROR while retrieving manga: {request.status_code}")

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

# downloadManga(getMangaId(manga_url), 1, True)