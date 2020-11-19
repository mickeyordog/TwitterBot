import praw
import requests
import tweepy
import time
from model.credentials import *


def strip_title(title):
    if len(title) < 94:
        return title
    else:
        return title[:93] + "..."


def tweet_creator(subreddit_info):
    post_dict = {}
    post_ids = []
    print("[bot] Getting posts from Reddit")
    for submission in subreddit_info.hot(limit=50):
        post_dict[strip_title(submission.title)] = (submission.url, submission.shortlink, submission.author)
        post_ids.append(submission.id)
    return post_dict, post_ids


def setup_connection_reddit(subreddit):
    print("[bot] setting up connection with Reddit")
    r = praw.Reddit(client_id=reddit_client_id, client_secret=reddit_client_secret, user_agent=reddit_user_agent)
    subreddit = r.subreddit(subreddit)
    return subreddit


def duplicate_check(post_id):
    found = 0
    with open('posted_posts.txt', 'r') as file:
        for line in file:
            if post_id in line:
                found = 1
    return found


def add_id_to_file(post_id):
    with open('posted_posts.txt', 'a') as file:
        file.write(str(post_id) + "\n")


def main():
    subreddit = setup_connection_reddit('pixelart')
    post_dict, post_ids = tweet_creator(subreddit)
    tweeter(post_dict, post_ids)


def tweeter(post_dict, post_ids):
    auth = tweepy.OAuthHandler(pixel_twitter_consumer_key, pixel_twitter_consumer_secret)
    auth.set_access_token(pixel_twitter_access_token, pixel_twitter_access_token_secret)
    api = tweepy.API(auth)
    posted = 0
    for post, post_id in zip(post_dict, post_ids):
        found = duplicate_check(post_id)
        if found == 0 and posted <= 3:
            try:
                url = post_dict[post][0]
                short_link = post_dict[post][1]
                user = post_dict[post][2]

                if '.png' not in url:
                    print("not a png")
                    continue

                print("[bot] Posting this link on twitter")
                print(f"\"{post}\" by u/{user} \n{short_link} #pixelart #reddit #gamedev #indiegame #art")

                r = requests.get(url)
                with open('image.png', 'wb') as f:
                    f.write(r.content)

                api.update_with_media(filename='image.png',
                                      status=f"\"{post}\" by u/{user} \n{short_link} #pixelart #reddit #gamedev "
                                             f"#indiegame #art")
                add_id_to_file(post_id)
                posted += 1
                time.sleep(180)
            except:
                print('An error occurred')
        else:
            print("[bot]  Already posted")


if __name__ == '__main__':
    main()
