SECRET_KEY = ''

PROD_MODE = True
if PROD_MODE:
    SQLALCHEMY_DATABASE_URI = "postgres://" \
                              ":" \
                              "@" \
                              ":5432" \
                              "/"
else:
    SQLALCHEMY_DATABASE_URI = "postgres://postgres" \
                              ":" \
                              "@localhost" \
                              ":5432" \
                              "/"

MAX_CONTENT_LENGTH = 5 * 1024 * 1024

RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
