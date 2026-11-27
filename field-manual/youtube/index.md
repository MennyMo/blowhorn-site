# YouTube: the feed that asks how it went

> YouTube asks its viewers whether a video was worth their time. Make the one they're glad they watched.


## How YouTube recommends

- **Rewards satisfaction, not just watch time.** Signals include "clicks, watchtime, survey responses, sharing, likes, and dislikes," and YouTube measures "valued watchtime" through surveys where "Only videos that you rate highly with four or five stars are counted" ([YouTube Blog](https://blog.youtube/inside-youtube/on-youtubes-recommendation-system/)).
- **Listens to "no."** Dislikes, "Not interested" and "Don't recommend channel" tell the system what to avoid ([YouTube Help](https://support.google.com/youtube/answer/16089387)).

A video people are glad they watched beats a video that tricked them into staying.

## What YouTube prohibits

- **Fake engagement.** "YouTube doesn't allow anything that artificially increases the number of views, likes, comments, or other metrics either by using automatic systems or serving up videos to unsuspecting viewers." That includes "sub4sub" trades ([Fake engagement policy](https://support.google.com/youtube/answer/3399767)).
- **Comment spam.** "Using high-volume, repetitive, or deceptive comments, live chats, or other messages," such as "Posting identical or similar 'check out my channel' messages across hundreds of videos" ([Spam policy](https://support.google.com/youtube/answer/2801973)).
- **Automated access.** You may not "access the Service using any automated means (such as robots, botnets or scrapers)" or "cause or encourage any inaccurate measurements of genuine user engagement with the Service" ([YouTube Terms of Service, 15 Dec 2023](https://www.youtube.com/static?template=terms)).

The last rule is about software, not only behavior. Blowhorn acts in your own signed-in browser through the extension, or, once a profile gives YouTube Data API consent, through YouTube's official API. Either way it works at your pace and leaves every comment, reply and like to a run you start. It is still software acting on YouTube, so weigh that rule before you run anything there.

## Do's and don'ts

- **Do** write the title and description for the person deciding whether to watch.
- **Do** answer comments in your own words, one at a time.
- **Don't** like one video from a crowd of your own profiles.
- **Don't** paste the same comment under many videos.

## What Blowhorn does on YouTube

Once you turn on YouTube for a browser profile, Blowhorn runs these actions in your own signed-in browser, through the extension: uploads videos (private unless you choose unlisted or public), publishes posts on your channel's Posts tab, and comments, replies and likes. Once that profile gives YouTube Data API consent, uploads, comments, replies and likes go through YouTube's official API instead. Posts on the Posts tab have no Data API path and stay in the signed-in browser. Reading your channel's analytics needs that consent.

A scheduled run never comments, replies, likes or posts on the Posts tab. Each profile has daily ceilings, counted across every run that day: 3 uploads, 10 comments, 10 replies, 20 likes and 2 Posts tab posts. An activity past its ceiling waits for the next day.

Further reading: [YouTube platform reference](/docs/reference/platforms/youtube/).

