from time import sleep
import json
import requests
import stashapi.log as log
from stashapi.stashapp import StashInterface
import os
from yt_dlp import YoutubeDL


def controller(urls, stashurl, method):
    mediapath = os.environ.get("STASH_MEDIA_PATH")+stashurl.split(':')[0]+"/"
    ydl_opts = {
        'outtmpl': mediapath+'/%(webpage_url_domain)s/%(uploader)s/%(title)s.%(ext)s',
        'external_downloader': 'aria2c',
        'writeinfojson': True,
        'quiet': True,
    }
    args = ["--write-info-json", "--add-metadata", "-o", mediapath+"%(webpage_url_domain)s/%(uploader)s/%(title)s.%(ext)s"]
    stash = StashInterface({
        "scheme": "http",
        "domain": stashurl.split(':')[0],
        "port": stashurl.split(':')[1],
        "logger": log
    })
    if method == 'videos':
        return videoslist(urls, stash, args, mediapath)
    elif method == 'phprofile':
        return phprofile(urls, stash, args, mediapath, args)
    elif method == 'test':
        return test(urls, stash, args, mediapath)
    else:
        return "uknown method"

class videomanager:
    def __init__(self, stash, mediapath, args, url, info):
        self.stash = stash
        self.mediapath = mediapath
        self.args = args
        self.url = url
        self.info = info
        self.status = "init"

        download = self.call("http://localhost:4444/rpc", 'Service.Exec', self.args)
        while self.call("http://localhost:4444/rpc", 'Service.Status', download['id'])['progress']['percentage'] != "-1":
            sleep(10)
        self.dlpinfo = self.call("http://localhost:4444/rpc", 'Service.Status', download['id'])['info']
        self.status = "downloaded"
        self.call("http://localhost:4444/rpc", 'Service.Kill', download['id'])

    def call(url, method, args):
        data = {
            'method': method,
            'params': [args]
        }

        res = requests.post(url=url, json=data, headers={'Content-Type': 'application/json'})
        response = json.loads(res.text)
        return response


def test(urls, stash, args, mediapath):
    call(urls[0], 'Service.Exec', args)


def phprofile(urls, stash, ydl_opts, mediapath, args):
    for line in urls:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(line, download=False)
            sperf = stash.find_performers({"name": {"modifier": "INCLUDES", "value": info['entries'][0]['uploader']}})
            if len(sperf) == 0:
                sperf = []
                sperf[0] = stash.create_performer({"name": info['entries'][0]['uploader']})
                log.debug("Created performer: "+info['entries'][0]['uploader']+" with ID: "+sperf[0]['id'])
            else:
                log.debug("Performer: "+info['entries'][0]['uploader']+" found with ID: "+sperf[0]['id'])




def videoslist(urls, stash, ydl_opts, mediapath):


def old_phprofile(urls, stash, ydl_opts, mediapath):
    for line in urls:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(line, download=False)
            perfid = stash.findPerformerIdWithName(
                info['entries'][0]['uploader'])
            if perfid == None:
                perfid = stash.createPerformerByName(
                    info['entries'][0]['uploader'])
                log.LogInfo(
                    "Performer: "+info['entries'][0]['uploader']+" created with ID: "+perfid)
            else:
                log.LogInfo(
                    "Performer: "+info['entries'][0]['uploader']+" found with ID: "+perfid)
            for video in info['entries']:
                error_code = ydl.download(video['webpage_url'])
                if (error_code != 0):
                    log.LogError(
                        "Download of Video: "+video['title']+" from profile "+video['uploader']+" failed ")
                else:
                    log.LogInfo(
                        "Download of Video: "+video['title']+" from profile "+video['uploader']+" successful")
            stashpath = mediapath + "stars/" + \
                info['entries'][0]['webpage_url_domain'] + "/" + \
                info['entries'][0]['uploader']+"/"
            stash.metadata_scan(stashpath)
            log.LogInfo("waiting 3 Minutes")
            sleep(int(os.environ.get("STASH_SCAN_TIMEOUT")))
            scenes = stash.findScenesByPathRegex(
                r'.*\.(?:[mM][pP]4|[wW][mM][vV])$')
            for video in info['entries']:
                for scene in scenes:
                    if scene['title'] == video['title']+"."+video['ext'] or video['title']+"."+video['ext'] == scene['path'].split("/")[-1]:
                        log.LogInfo("Found Scne with ID: " +
                                    scene['id']+" and Title: "+scene['title'])
                        updatescene = {}
                        updatescene['id'] = scene['id']
                        updatescene['url'] = video['webpage_url']
                        updatescene['title'] = video['title']
                        updatescene['tag_ids'] = [
                            stash.findTagIdWithName("scrape")]
                        updatescene['performer_ids'] = perfid
                        if scene.get('rating'):
                            updatescene['rating'] = scene.get('rating')
                        log.LogInfo("Updating Scene with ID: " +
                                    updatescene['id']+" with video: "+video['title'])
                        stash.updateScene(updatescene)
    return scenes


def old_videoslist(urls, stash, ydl_opts, mediapath):
    for line in urls:
        updatescenes = []
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(line, download=False)
            log.LogInfo("Identified Video as: "+info.get('title'))
            error_code = ydl.download(line)
            if (error_code != 0):
                log.LogError("Download of Video: "+info.get('title')+" failed")
                return "Download of Video: "+info.get('title')+" failed"
            else:
                log.LogInfo("Download of Video: " +
                            info.get('title')+" successful")
                stashpath = mediapath + \
                    info.get('webpage_url_domain')+"/"+info.get('uploader')+"/"
                stash.metadata_scan(stashpath)
                sleep(10)
                scenes = stash.findScenesByPathRegex(
                    r'.*\.(?:[mM][pP]4|[wW][mM][vV])$')
                for scene in scenes:
                    if scene['path'].split('/')[-1] == info['title']+"."+info['ext'] or scene['title'] == info['title']+"."+info['ext']:
                        pathstrip = scene['path'].split("/")
                        titel = pathstrip[len(pathstrip)-1].split(".")[0]
                        updatescene = {}
                        updatescene['id'] = scene['id']
                        updatescene['url'] = info.get('webpage_url')
                        updatescene['title'] = titel
                        updatescene['tag_ids'] = [
                            stash.findTagIdWithName("scrape")]
                        if scene.get('rating'):
                            updatescene['rating'] = scene.get('rating')
                        log.LogInfo("Updating Scene with ID: " +
                                    updatescene['id']+" with URL: "+line)
                        stash.updateScene(updatescene)
                        updatescenes += updatescene
        return updatescenes
