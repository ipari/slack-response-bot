from __future__ import print_function
from __future__ import unicode_literals

import codecs
import random
import time
import yaml

from konlpy.tag import Okt

__all__ = [b'Bot', b'Brain']


class Bot(object):
    def __init__(self, sc):
        self.sc = sc
        self.brain = Brain()

    @staticmethod
    def is_message(response):
        return response['type'] == 'message' and 'text' in response

    @staticmethod
    def is_from_bot(response):
        return 'bot_id' in response

    def say(self, response):
        answer = self.brain.find_answer(response['text'])
        if answer is None:
            return

        kwargs = {}
        # Required
        kwargs['channel'] = response['channel']
        kwargs['text'] = answer
        # Optional
        kwargs['as_user'] = True
        if 'thread_ts' in response:
            kwargs['thread_ts'] = response['thread_ts']

        self.sc.api_call('chat.postMessage', **kwargs)

    def listen(self):
        while True:
            responses = self.sc.rtm_read()
            for response in responses:
                try:
                    if not self.is_message(response) or self.is_from_bot(response):
                        continue
                    self.say(response)
                except:
                    pass
            time.sleep(1)


class Brain(object):

    def __init__(self):
        self.data = None
        self.groups = {}
        self.triggers = None
        self.qnas = []

        self.load_data()
        self.okt = Okt()

    def process_group(self, keyword, allow_group=True):
        if not keyword.startswith('group:'):
            return keyword

        if not allow_group:
            print('group 에서는 group 을 사용할 수 없습니다.')
            return

        group_key = keyword.split(':')[1]
        try:
            return self.groups[group_key]
        except KeyError:
            print('groups 에서 {}를 찾을 수 없습니다.', group_key)

    def process_keywords(self, keywords, allow_group=True):
        if not isinstance(keywords, list):
            keywords = [keyword.strip() for keyword in keywords.split(',')]
        keywords = [self.process_group(keyword, allow_group) for keyword in keywords]
        return keywords

    def load_data(self):
        with codecs.open('data.yml', 'r', 'utf-8') as f:
            data = yaml.load(f)

            if data['groups'] is not None:
                for group, keywords in data['groups'].items():
                    data['groups'][group] = self.process_keywords(keywords, allow_group=False)
            self.groups = data['groups']

            if data['triggers'] is not None:
                data['triggers'] = self.process_keywords(data['triggers'])
            self.triggers = data['triggers']

            for qna in data['qnas']:
                qna['keywords'] = self.process_keywords(qna['keywords'])
            self.qnas = data['qnas']

    def to_pos(self, sentence):
        pos = self.okt.pos(sentence, stem=True)
        pos = [p[0] for p in pos]
        return pos

    def check_keywords(self, sentence, keywords, pos=None):
        is_valid = True
        pos = pos or self.to_pos(sentence)

        for keyword in keywords:
            if isinstance(keyword, list):
                if any(word in pos for word in keyword):
                    continue
                if any(word in sentence for word in keyword):
                    continue
                is_valid = False
            else:
                if keyword not in pos and keyword not in sentence:
                    is_valid = False
        return is_valid

    def find_answer(self, sentence):
        if self.triggers is not None:
            if not self.check_keywords(sentence, self.triggers):
                return

        pos = self.to_pos(sentence)
        for qna in self.qnas:
            keywords = qna['keywords']
            if self.check_keywords(sentence, keywords, pos=pos):
                answers = qna['answers']
                if isinstance(answers, list):
                    return random.choice(answers)
                return answers
