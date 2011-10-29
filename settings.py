# A list of sane default settings.

# NOTE: The Twitter authentication details *should* be set below. This is
# further designated with "[EDIT]" prepended to the block comment.

#-----------#
#- Twitter -#
#-----------#

# [EDIT] Twitter credentials for application usage
CONSUMER_KEY        = ''
CONSUMER_SEC        = ''
ACCESS_TOKEN        = ''
ACCESS_TOKEN_SEC    = ''

# Delay in seconds between each tweet
TWEET_DELAY         = 0.1

#----------------#
#- Feed Details -#
#----------------#

# Number of posts per check with which to update Twitter.
POST_LIMIT          = 5

# Delay in seconds between each check of RWW for new posts
POST_DELAY          = 60

# Stores data regarding most recently processed post to maintain state between
# usages of the program and, most importantly, prevent duplicates.
POST_DATA_FILE      = 'rww_data'

# URL from which RWW is checked for new posts. Should almost certainly *not* be
# changed.
FEED_URL            = 'http://feeds.feedburner.com/readwriteweb'
