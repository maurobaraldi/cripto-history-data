from queue import Queue
from sys import exit as _exit
from time import sleep
from threading import Thread
from urllib.request import Request, urlopen

concurrent = 200

def getStatus(url):
    try:
        request = Request(url, headers={'User-agent': 'Mozilla/5.0'})
        sleep(0.5)
        with urlopen(request) as r:
            return r.status, url
    except:
        return "error", url

def doSomethingWithResult(status, url):
    print(status, url)

def doWork():
    while True:
        url = q.get()
        status, url = getStatus(url)
        doSomethingWithResult(status, url)
        q.task_done()

q = Queue(concurrent * 2)

for i in range(concurrent):
    t = Thread(target=doWork)
    t.daemon = True
    t.start()

try:
    for day in range(1, 30):
        q.put(f'https://www.mercadobitcoin.net/api/xrp/day-summary/2022/{day}/11/')
    q.join()
except KeyboardInterrupt:
    _exit(1)

