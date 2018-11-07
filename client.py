from tornado.httpclient import *
from tornado.httputil import HTTPHeaders
from multiprocessing import Process, Queue


def requ(q, x):
    http_client = HTTPClient()
    header = HTTPHeaders({'Range': 'bytes=0-220679'})
    request = HTTPRequest("http://localhost:8888/124.jpg", headers=header)

    try:
        response = http_client.fetch(request)
        result = response.body
    except HTTPError as e:
        # HTTPError is raised for non-200 responses; the response
        # can be found in e.response.
        result = "Error: " + str(e)
    except Exception as e:
        # Other errors are possible, such as IOError.
        result = "Error: " + str(e)
    http_client.close()
    with open('125.jpg', 'wb') as f:
        f.write(result)


if __name__ == '__main__':
    queue = Queue()
    p = Process(target=requ, args=(queue, 1))
    p.start()
    p.join()
    result = queue.get()
    print(result)
