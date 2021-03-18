from database.thread import Thread


class ThreadPosts:
    thread_post = None
    posts = []
    last_post_date = None

    def __init__(self, thread_post: Thread):
        self.thread_post = thread_post

    def populate_posts(self, posts):
        self.posts = posts

    def update_last_post_date(self):
        if len(self.posts) >= 1:
            # get last and convert last post date to unix(??) epoch time thing for easier sort
            self.last_post_date = self.posts[-1].get_date_unix()
        else:
            # use the thread date itself
            self.last_post_date = self.thread_post.get_date_unix()
