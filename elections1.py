from collections import defaultdict
from socialweb.tweets import Tweets

# this script collects Twitter followers for three presidential candidates; 
# checks the interesections of the followers; 
# checks the latest 10 tweets for the followers (only for those who follow only one candidate); 
# stores the hashtags; 
# calculates the hashtags that appear in tweets of more than one follower of a particular candidate
#
# where is socialweb package? yeah, I know - it is crazy, it is on Bitbucket (https://bitbucket.org/miha_stopar/mosaic-demo/src), perhaps it will be an independent library one day, but right now it is a part of the mOSAIC key value connectors demo

tweets = Tweets()
n1 = "DaniloTurk2012"
n2 = "BorutPahor"
n3 = "MilanZver"
candidates = [n1, n2, n3]
for candidate in candidates:
    followers = tweets.collect_user_followers(candidate)
    tweets.collect_users_info(followers)

print "Danilo's followers: %s" % len(tweets.get_followers(n1))
print "Borut's followers: %s" % len(tweets.get_followers(n2))
print "Milan's followers: %s" % len(tweets.get_followers(n3))

danilo_followers_db_key = tweets.get_db_id_by_screen_name(n1, "follower_ids")
borut_followers_db_key = tweets.get_db_id_by_screen_name(n2, "follower_ids")
milan_followers_db_key = tweets.get_db_id_by_screen_name(n3, "follower_ids")
inter_danilo_borut = tweets.get_intersection([danilo_followers_db_key, borut_followers_db_key])
print "intersection Danilo and Borut followers: %s" % len(inter_danilo_borut)
inter_danilo_milan = tweets.get_intersection([danilo_followers_db_key, milan_followers_db_key])
print "intersection Danilo and Milan followers: %s" % len(inter_danilo_milan)
inter_borut_milan = tweets.get_intersection([borut_followers_db_key, milan_followers_db_key])
print "intersection Borut and Milan followers: %s" % len(inter_borut_milan)
intersection_all_three = tweets.get_intersection([danilo_followers_db_key, borut_followers_db_key, milan_followers_db_key])
print len(intersection_all_three)

only_danilos_followers = tweets.get_sdiff([danilo_followers_db_key, borut_followers_db_key, milan_followers_db_key])
print "only Danilo's followers: %s" % len(only_danilos_followers)
only_boruts_followers = tweets.get_sdiff([borut_followers_db_key, danilo_followers_db_key, milan_followers_db_key])
print "only Borut's followers: %s" % len(only_boruts_followers)
only_milans_followers = tweets.get_sdiff([milan_followers_db_key, danilo_followers_db_key, borut_followers_db_key])
print "only Milan's followers: %s" % len(only_milans_followers)

all_interesting_followers = only_milans_followers.union(only_danilos_followers, only_boruts_followers)
for user in all_interesting_followers:
    user_info = tweets.get_user_info_by_id(user)
    if not tweets.exist_user_hashtags(user):
        print "not for %s" % user_info["screen_name"]
        tags = tweets.collect_user_hashtags(user, 1, 10)
    else:
        print "already exists for %s" % user_info["screen_name"]
        
def count_hashtags(followers):
    hashtags = defaultdict(int)
    for user in followers:
        user_info = tweets.get_user_info_by_id(user)
        screen_name = user_info["screen_name"]
        tweets_checked = tweets.r_server.hget(tweets.get_db_id_by_user_id(user, 'hashtags'), "tweets_checked")
        user_hashtags = tweets.get_user_hashtags(user)
        # don't be confused with "tweets_checked" value inside user's hashtags - it is not a hashtag, it 
        # is an info about number of tweets checked for this user
        print "%s / tweets checked: %s, hashtags: %s" % (screen_name, tweets_checked, len(user_hashtags))
        if user_hashtags:
            for k,v in user_hashtags.iteritems():
                if k != "tweets_checked":
                    hashtags[k] += 1
    print hashtags
    filtered = filter(lambda x : hashtags[x] > 1, hashtags)
    output = "" # string to be inserted in word cloud generator
    for f in filtered:
        print "%s: %s" % (f, hashtags[f])
        for i in range(hashtags[f]):
            output += f + " "
    print output

print "counting hashtags for Danilo's followers..................................................................."
count_hashtags(only_danilos_followers)
print "counting hashtags for Borut's followers...................................................................."
count_hashtags(only_boruts_followers)
print "counting hashtags for Milan's followers...................................................................."
count_hashtags(only_milans_followers)






