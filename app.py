import os
import threading
import time

from flask import Flask

from slackclient import SlackClient


app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World?"


@app.route("/main/")
def main():
    return "Main"


def run():
    while True:
        responses = sc.rtm_read()
        for response in responses:
            try:
                print(response)
            except:
                pass
        time.sleep(1)


SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
sc = SlackClient(SLACK_BOT_TOKEN)


if __name__ == '__main__':
    if sc.rtm_connect():
        thread = threading.Thread(target=run, args=())
        thread.daemon = True
        thread.start()
        app.run(host='0.0.0.0', port=2888, threaded=True)
    else:
        print('export SLACK_BOT_TOKEN=xoxb-your-token 을 먼저 실행하세요.')
        print('또는 올바른 Slack Token 인지 확인해보세요.')
