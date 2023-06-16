import atexit
from collections import namedtuple
from multiprocessing.pool import ThreadPool
from typing import Dict, List

ConcurrentApiRequestRow = namedtuple('ConcurrentApiRequestRow', ['name', 'method', 'kwargs'])


class ApiClientThreadsPool(object):
    """
    param pool_threads: The number of threads to use for async requests
        to the API. More threads means more concurrent API requests.
    """
    def __init__(self, pool_threads=1):
        atexit.register(self.close)
        self._pool = ThreadPool(pool_threads)

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self._pool:
            self._pool.close()
            self._pool.join()
            self._pool = None
            if hasattr(atexit, 'unregister'):
                atexit.unregister(self.close)

    def make_concurrent_api_requests(self, concurrent_api_requests: List[ConcurrentApiRequestRow]):
        concurrent_results = {}
        for concurrent_api_request in concurrent_api_requests:
            concurrent_results[concurrent_api_request.name] = self._pool.apply_async(
                concurrent_api_request.method,
                kwds=concurrent_api_request.kwargs
            )

        return {
            name: api_result.get() for name, api_result in concurrent_results.items()
        }


instance = ApiClientThreadsPool(pool_threads=10)
