import os
import threading
import time

from flask import Flask
from slackclient import SlackClient

from bot import Brain


app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World?"


@app.route("/main/")
def main():
    return "Main"


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
            responses = sc.rtm_read()
            for response in responses:
                try:
                    if not self.is_message(response) or self.is_from_bot(response):
                        continue
                    self.say(response)
                except:
                    pass
            time.sleep(1)


SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
sc = SlackClient(SLACK_BOT_TOKEN)


if __name__ == '__main__':
    if sc.rtm_connect():
        bot = Bot(sc)
        thread = threading.Thread(target=bot.listen, args=())
        thread.daemon = True
        thread.start()
        app.run(host='0.0.0.0', port=2888, threaded=True)
    else:
        print('export SLACK_BOT_TOKEN=xoxb-your-token 을 먼저 실행하세요.')
        print('또는 올바른 Slack Token 인지 확인해보세요.')
