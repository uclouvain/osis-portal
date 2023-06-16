import atexit
from multiprocessing.pool import ThreadPool
from typing import List


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

    def make_concurrent_api_requests(self, api_requests: List[any]):
        api_results = []
        for api_request in api_requests:
            api_results.append(
                self._pool.apply_async(api_request)
            )
        return [api_result.get() for api_result in api_requests]


instance = ApiClientThreadsPool(pool_threads=4)
