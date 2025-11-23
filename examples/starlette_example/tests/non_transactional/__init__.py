"""
Fair tests in which the application manages the session lifecycle itself.
Data isolation between tests is performed by running "TRUNCATE TABLE" before
    and after each test.
This is fair testing, but slower.
"""
