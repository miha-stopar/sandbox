import requests
import json
import sys
import gevent
from gevent import monkey; monkey.patch_all(thread=False)

class Github():
    def __init__(self):
        self.type_error_count = 0
        self.users_error_count = 0
        self.hours_error_count = 0
        self.not_registered_count = 0
        self.failed_users = []
        
    def _get_user_type(self, user):
        url = 'https://api.github.com/users/%s' % user
        try:
            r = requests.get(url)
            if(r.ok):
                rep = json.loads(r.text or r.content)
                user_type = rep['type']
            print "user type for user %s: %s" % (user, user_type)
            return user_type
        except Exception, e:
            print "Error when retrieving user type for %s. Error: %s" % (user, str(e))
            self.type_error_count += 1
        return None

    def get_users(self, url, users, pages_users):
        try:
            r = requests.get(url)
            if(r.ok):
                pages_users -= 1
                page = json.loads(r.text or r.content)
                next_url = None
                if 'next' in r.links:
                    next_url = r.links['next']['url']
                    print next_url
                for item in page:
                    actor = item['actor']
                    if 'login' in actor:
                        user = actor['login']
                    else:
                        continue
                    user_type = self._get_user_type(user)
                    user_already_in = user in users
                    if not user_already_in and user_type == "User": #filter out organizations ...
                        users.append(str(user))
                    else:
                        #print "user %s not registered (user_already_in: %s, type: %s)" % (user, user_already_in, user_type)
                        self.not_registered_count += 1
                if pages_users > 0 and next_url != None:
                    self.get_users(next_url, users, pages_users)
        except Exception, e:
            print "Error when retrieving users on the url %s. Error: %s" % (url, str(e))
            self.users_error_count += 1


    def get_followers(self, user, users):
        try:
            url = 'https://api.github.com/users/%s/followers' % user
            r = requests.get(url)
            if(r.ok):
                page = json.loads(r.text or r.content)
                followers = []
                for item in page:
                    follower = item['login']
                    user_type = self._get_user_type(follower)
                    if follower not in users and user_type == "User": #filter out organizations ...
                        followers.append(str(follower))
                return followers
        except Exception, e:
            print "Error when retrieving followers for user: %s. Error: %s" % (user, str(e))
            return []

    def _get_hours(self, url, hours):
        try:
            r = requests.get(url)
            print "processing url: %s" % url
            if(r.ok):
                page = json.loads(r.text or r.content)
                next_url = None
                if 'next' in r.links:
                    next_url = r.links['next']['url']
                for item in page:
                    date = item['created_at']
                    hour = date.split('T')[1][:2]
                    if hour not in hours:
                        hours.append(str(hour))
                if next_url != None:
                    status = self._get_hours(next_url, hours)
                    return status
        except Exception, e:
            print "Error when retrieving user hours on the url %s. Error: %s" % (url, str(e))
            self.hours_error_count += 1
            user = url.split("/users/")[1]
            user = user.split("/events/public")[0]
            self.failed_users.append(user)
            return "error"

    def get_data(self, user):
        hours = []
        start_url = 'https://api.github.com/users/%s/events/public' % user
        try:
            status = self._get_hours(start_url, hours)
            if status != "error":
                return user, len(hours)
            else:
                return user, None
        except:
            print "Error when retrieving data for user %s. Error: %s" % (user, sys.exc_info()[0])
            return user, None

if __name__ == "__main__":
    github = Github()
    users = []
    events_url = 'https://api.github.com/events'
    pages_users = 10 # ten is actually the max you can get
    github.get_users(events_url, users, pages_users)
    followers = []
    for user in users:
        folls = github.get_followers(user, users)
        print "followers for user %s: %s" % (user, folls)
        followers.extend(folls)
    users.extend(followers)
    
    import time
    a = time.time()
    jobs = [gevent.spawn(github.get_data, user) for user in users]
    gevent.joinall(jobs)
    user_hours = [job.value for job in jobs if job.value[1] != None]
    print users
    users_h = map(lambda x : x[0], user_hours)
    print users_h
    print "-----------------------------------------------------------------------"
    print user_hours
    print "all users: %s" % len(users)
    print "followers: %s" % len(followers)
    print "number of users checked for hours: %s" % len(users)
    print "number of users with known hours: %s" % len(user_hours)
    average = sum(map(lambda  x: x[1], user_hours)) / float(len(user_hours))
    print "average: %s" % average
    print "errors when retrieving type: %s" % github.type_error_count
    print "errors when retrieving users: %s" % github.users_error_count
    print "errors when retrieving hours: %s" % github.hours_error_count
    print "failed users: %s" % github.failed_users
    # number of failed users - if due to some network connection problems the REST call failed
    # if network connection is good there shouldn't be any errors:
    print "number of failed users: %s" % len(github.failed_users)
    # intersection of users where an error happened and users with know hours - intersection should be empty:
    print "intersection: %s" % set(github.failed_users).intersection(set(users_h))
    # not registered users - for example users that appeared more than once where registered only once
    print "not registered: %s" % github.not_registered_count
    d = {}
    for i in range(0,25):
        d[i] = 0
    s = ""
    for item in user_hours:
        d[item[1]] += 1 
    for k, v in d.iteritems():
        s += "['%s', %s],\n" % (k, v)
    print d
    #print s # formatting for javascript graph generation
    print "time: %s" % (time.time() - a)
    
    



