from __future__ import print_function
from __future__ import unicode_literals

import codecs
import os
import random
import time
import yaml

from konlpy.tag import Twitter
from slackclient import SlackClient


def process_keywords(keywords, allow_group=True):
    def process_group(keyword):
        if keyword.startswith('group:'):
            if allow_group:
                group_key = keyword.split(':')[1]
                try:
                    return data['groups'][group_key]
                except KeyError:
                    print('groups에서 {}를 찾을 수 없습니다.'.format(group_key))
                    raise
            print('groups: 는 conditions의 keywords 에만 사용할 수 있습니다.')
            raise
        return keyword

    if not isinstance(keywords, list):
        keywords = keywords.split(',')
        keywords = [keyword.strip() for keyword in keywords]
    keywords = [process_group(keyword) for keyword in keywords]
    return keywords


with codecs.open('keywords.yml', 'r', 'utf-8') as f:
    data = yaml.load(f)

    if data['groups'] is not None:
        for group, keywords in iter(data['groups'].items()):
            data['groups'][group] = process_keywords(keywords, False)

    if data['triggers'] is not None:
        data['triggers'] = process_keywords(data['triggers'])

    for condition in data['conditions']:
        condition['keywords'] = process_keywords(condition['keywords'])


SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
sc = SlackClient(SLACK_BOT_TOKEN)
twitter = Twitter()


def to_pos(sentense):
    pos = twitter.pos(sentense, stem=True)
    pos = [p[0] for p in pos]
    return pos


def check_keywords(sentense, keywords, pos=None):
    is_valid = True
    pos = pos or to_pos(sentense)

    for keyword in keywords:
        if isinstance(keyword, list):
            if any(word in pos for word in keyword):
                continue
            if any(word in sentense for word in keyword):
                continue
            is_valid = False
        else:
            if keyword not in pos and keyword not in sentense:
                is_valid = False
    return is_valid


def find_answer(sentense):
    if data['triggers'] is not None:
        if not check_keywords(sentense, data['triggers']):
            return

    pos = to_pos(sentense)
    for condition in data['conditions']:
        keywords = condition['keywords']
        if check_keywords(sentense, keywords, pos=pos):
            answers = condition['answers']
            if isinstance(answers, list):
                return random.choice(answers)
            return answers
    return


def is_message(response):
    return response['type'] == 'message' and 'text' in response


def is_from_bot(response):
    return 'bot_id' in response


def say(response):
    answer = find_answer(response['text'])
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

    sc.api_call('chat.postMessage', **kwargs)


if __name__ == '__main__':
    if sc.rtm_connect():
        print('채팅봇이 실행중입니다.')
        print('CTRL+C 로 종료할 수 있습니다.')
        while True:
            responses = sc.rtm_read()
            for response in responses:
                if not is_message(response) or is_from_bot(response):
                    continue
                say(response)
            time.sleep(1)
    else:
        print('export SLACK_BOT_TOKEN=xoxb-your-token 을 먼저 실행하세요.')
        print('또는 올바른 Slack Token 인지 확인해보세요.')
