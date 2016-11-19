
import slack
from slack import MsgResource

class YoutubeDownloader(object):

    def __init__(self, text):
        self.input = text
        self.slackbot = slack.SlackerAdapter()

    def make_link(self, params=None):
        # Get Only url
        url = params[params.index("http"):].split(" ")[0]
        feature = self.get_feature(url)
        if feature is None:
            text = MsgResource.YOUTUBE_DOWNLOADER + "\n" + url.replace("youtube.com", "ssyoutube.com")
        else:
            param = self.get_param(feature, url)
            ssyoutube_link = "https://www.ssyoutube.com/watch?v=" + param + "&feature=" + feature
            text = MsResource.YOUTUBE_DOWNLOADER + "\n" + ssyoutube_link
        self.slackbot.send_message(text=text)

    def get_feature(self, url):
        feature_list = ['youtu.be']
        for feature in feature_list:
            if feature in url:
                return feature
        return None

    def get_param(self, feature, url):
        param = url[url.index(feature)+len(feature)+1:]
        return param
