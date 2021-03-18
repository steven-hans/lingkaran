from datetime import datetime

from dateutil.parser import parse
from dateutil.tz import tzoffset
from flask import Blueprint

from database.content import Content
from database.post import Post
from database.thread import Thread
from threadposts import ThreadPosts

from main import db

db_handle = Blueprint('db_handle', __name__, template_folder='templates')


# returns ALL threads available in the last week, and at most three latest posts in that thread.
def get_mainpage_threads():
    res = []

    # TODO handle multiple pages.
    # page_number = 0  # should be obtained from get request
    # select * from thread max 30

    # thread_list = db.session.query(Content).join(Thread).filter(Content.id == Thread.thread_number).all()
    thread_list = db.session.query(Thread).all()

    for t in thread_list:
        # for each thread, make a thread_post
        thread = Thread(t.id, t.name, t.ip, t.content, t.date_post, t.subject, t.pinned, t.locked, t.media_link)
        thread_post = ThreadPosts(thread)

        # then populate with posts in that thread at most three last posts (grab 3 last)
        assert (isinstance(t.id, int))
        latest_posts = [Post(p.id, p.name, p.ip, p.content, p.date_post, t.id, p.media_link)
                        for p in db.session.query(Post)
                            .filter(Post.post_number == Post.id,
                                       Post.thread_anchor == t.id)
                            .order_by(Post.date_post.desc()).limit(3)]
        latest_posts = latest_posts[::-1]
        thread_post.populate_posts(latest_posts)

        # update_last_post_date() for each thread_post
        thread_post.update_last_post_date()

        # now append pair<date, thread_post>
        res.append((thread_post, thread_post.last_post_date,))

    # and sort it. this is the final output, ready to be rendered into the template.
    if res is not None:
        res = sorted(res, key=lambda tup: tup[1])

    return [r[0] for r in res]


def get_thread(id: int):
    #thread = db.session.query(Content).join(Thread, Content.id == Thread.thread_number)\
    #    .filter(Thread.thread_number == id)\
    #    .values(Thread.subject, Thread.pinned, Thread.locked,
    #            Content.id, Content.ip, Content.content, Content.date_post)
    thread = db.session.query(Thread).filter(Thread.thread_number == id).all()

    for t in thread:
        thread = Thread(t.id, t.name, t.ip, t.content, t.date_post, t.subject, t.pinned, t.locked, t.media_link)
        thread_post = ThreadPosts(thread)
        all_posts = [Post(p.id, p.name, p.ip, p.content, p.date_post, t.id, p.media_link)
                     for p in db.session.query(Post)
                     .filter(Post.thread_anchor == t.id, Post.post_number == Post.id)
                     .order_by(Post.date_post.asc())]
        thread_post.populate_posts(all_posts)
        thread_post.update_last_post_date()
        return thread_post


TIMEZONE_OFFSET = tzoffset(None, 7 * 3600)


def get_formatted_displayed_date():
    return datetime.now(TIMEZONE_OFFSET).strftime('%y/%m/%d %H:%M')


def get_datetime():
    return datetime.now(TIMEZONE_OFFSET).strftime('%Y-%m-%d %H:%M')


def get_datetime():
    return datetime.now(TIMEZONE_OFFSET)


def post_new_thread(name: str, subject: str, ip: str, content: str, file_name: str):
    # insert without id field, let sqlite decide the next id.
    new_thread_id = get_new_id()
    #new_content = Content(new_thread_id, name, ip, content, get_datetime())
    #db.session.add(new_content)
    #db.session.flush()
    new_thread = Thread(new_thread_id, name, ip, content, get_datetime(), subject, 0, 0, file_name) # TODO implement pinned and locked thread
    db.session.add(new_thread)
    db.session.commit()


def get_new_id():
    res = db.session.query(db.func.max(Content.id)).scalar()
    if res is not None:
        return res+1
    else:
        return 1


def post_reply(new_id: int, thread_anchor: int, name: str, ip: str, content: str, file_name: str):
    #new_content = Content(new_id, name, ip, content, get_datetime())
    new_post = Post(new_id, name, ip, content, get_datetime(), thread_anchor, file_name)
    #db.session.add(new_content)
    #db.session.flush()
    db.session.add(new_post)
    db.session.commit()


def delete_thread(thread_id: int):
    thread = db.session.query(Thread).filter(Thread.thread_number == thread_id).first()

    if thread is None:
        return False

    post_ids = [post.post_number for post in db.session.query(Post).filter(Post.thread_anchor == thread_id).all()]

    Post.query.filter(Post.thread_anchor == thread_id).delete()
    db.session.flush()

    for post_id in post_ids:
        Content.query.filter(Content.id == post_id).delete()

    db.session.flush()

    Thread.query.filter(Thread.thread_number == thread_id).delete()
    db.session.flush()

    Content.query.filter(Content.id == thread_id).delete()

    db.session.commit()


def delete_post(post_id: int):
    Post.query.filter(Post.post_number == post_id).delete()
    Content.query.filter(Content.id == post_id).delete()

    db.session.commit()


def hour_diff_from_now(time_str: str):
    return (parse(time_str) - datetime.now()) // 3600


# for all threads that's still active, but the last reply is above 72 hours,
# immediately delete said thread and its posts.
# def purge_all_inactive_threads():
#     print('Purging inactive threads...')
#     threads_purged = 0
#
#     # get all thread ids only
#     threads = []
#     for thread in query_db('select thread_number, date_post from thread, content '
#                            'where thread_number=id'):
#         threads.append((thread['thread_number'], thread['date_post'],))
#
#     for thread in threads:
#         # get latest post from thread ids
#         assert (isinstance(thread[0], int))  # thread id has to be integer
#         latest_post_date = query_db('select date_post from content, post '
#                                     'where thread_anchor=? and id=post_number '
#                                     'order by date(date_post) desc limit 1', [thread[0]])
#
#         if latest_post_date is not None:
#             latest_post_date = latest_post_date['date_post']
#         else:
#             latest_post_date = thread[1]
#
#         if hour_diff_from_now(latest_post_date) >= 72:
#             delete_thread(thread[0])
#             threads_purged += 1
#             print('Thread', thread[0], 'deleted (last active is >= 72 hours).')
#
#     print('Purging complete.', threads_purged, 'thread(s) purged.')
