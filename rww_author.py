from   settings import *
import tweepy

class RWWauthor(object):
    """
    This class handles checking ReadWriteWeb for new posts and updating Twitter
    accordingly, further using any specified delays in order to avoid being
    abusive to the services in use.

    RWWauthor maintains state between calls and, through a data file, instances
    of the class, in order to avoid repetitive reposts.
    """

    def __init__(self):
        """
        Initializes the class and loads data from previos usage from
        `settings.POST_DATA_FILE`, if such a file is valid and available.
        """
        self.twitter   = None # will be authenticated when needed
        self.data_file = POST_DATA_FILE
        self._load()

    def _twitter_auth(self):
        """
        Authenticate with the Twitter API and provide access via
        `self.twitter`.
        """
        import tweepy
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SEC)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SEC)
        self.twitter = tweepy.API(auth)

    def _load(self):
        """
        Laod data used in between calls to and instances of this class from an
        external data file.
        """
        import pickle
        try:
            dfile = open(self.data_file, 'rb')
            data            = pickle.load(dfile)
        except:
            self.etag       = ''
            self.last_post  = ''
        else:
            self.etag       = data['etag']
            self.last_post  = data['last_post']
            dfile.close()

    def _save(self):
        """
        Save data used in between calls to and instances of this class to an
        external data file in order to prevent duplicates once the updating is
        resumed.
        """
        import pickle
        dfile = open(self.data_file, 'wb')
        data  = {
            'etag':      self.etag,
            'last_post': self.last_post,
        }
        pickle.dump(data, dfile)
        dfile.close()

    def _get_new_posts(self):
        """
        Retrieve all new posts from the URL specified in `settings.FEED_URL`,
        returned as a list of links to each post.

        The links are ordered chronologically so that the oldest posts are
        tweeted first. Further, they are limited to `settings.POST_LIMIT` posts
        to prevent being abusive toward any services in use.
        """
        import requests
        rsp      = requests.head(FEED_URL)
        new_etag = rsp.headers['etag']
        posts    = []

        # Retrieve new posts
        if new_etag != self.etag:
            import feedparser
            self.etag   = new_etag
            feed        = feedparser.parse(FEED_URL)
            entries     = feed['entries']

            for entry in entries:
                link = entry['link']
                if link == self.last_post:
                    break
                posts.append(link)

        # Reverse ordering for chronological tweeting; only up to [P] posts.
        return posts[::-1][:POST_LIMIT]

    def _tweet_post(self, url):
        """
        Given a URL to a RWW post, retrieves the necessary tweet data and sends
        a status update to the authorized account.
        """
        # Retrieve tweet author and other related data from post on website
        from urllib     import urlopen
        from lxml.html  import document_fromstring
        content = urlopen(url).read()
        html    = document_fromstring(content)
        phead   = html.get_element_by_id('metadata_digg_left')
        tweet   = phead.xpath('div/div[@class="share-tweet-mini"]/a')[0]
        tdata   = dict(tweet.items())

        # "Post Title by @author via @via"
        tweet_text = "%(data-text)s %(data-url)s via @%(data-via)s" % tdata
        self.twitter.update_status(tweet_text)

    def update(self):
        """
        Checks for any new posts from ReadWriteWeb and, if available, tweets
        them in chronological order with a mention to the post author.

        To be curteous to the services in use, this will sleep in between each
        tweet for `settings.TWEET_DELAY` seconds.
        """
        posts = self._get_new_posts()

        # If there are any posts, note most recen
        if posts:
            self.last_post = posts[-1]
            self._twitter_auth()

        for post in posts:
            self._tweet_post(post)

            # Delay in between tweets to avoid any trouble
            from time import sleep
            sleep(TWEET_DELAY)

        self._save()

if __name__ == '__main__':
    import daemon

    with daemon.DaemonContext():
        rww = RWWauthor()
        rww.update()

        # Delay in between checking for new posts
        from time import sleep
        sleep(POST_DELAY)
