# -*- coding: utf-8 -*-


class Record():

    def __init__(self, timestamp, first_ip, http_method, url, journal, user_agent, raw_user_agent, second_ip, referer, http_response_code):
        self.timestamp = timestamp
        self.first_ip = first_ip
        self.http_method = http_method
        self.url = url
        self.journal = journal
        self.user_agent = user_agent
        self.raw_user_agent = raw_user_agent
        self.second_ip = second_ip
        self.referer = referer
        self.http_response_code = http_response_code


class Journal():

    def __init__(self, name, year, volume, issue, article_id):
        self.name = name
        self.year = year
        self.volume = volume
        self.issue = issue
        self.article_id = article_id
