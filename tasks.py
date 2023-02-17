from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@192.168.1.97//')

@app.task
def add(x, y):
    print(y, y)
    return x + y

#if __name__ == '__main__':
#    for i in range(10000):
#        add(i, i)

@app.task
def run1():
    while True:
        print('run1')
        time.sleep(5)
    return


@app.task
def run2():
    while True:
        print('run2')
        time.sleep(2)
    return
