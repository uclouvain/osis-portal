import atexit
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        self._executor = ThreadPoolExecutor(max_workers=pool_threads, thread_name_prefix='API-CLIENT-THREADS')

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self._executor:
            self._executor.shutdown(wait=True)
            if hasattr(atexit, 'unregister'):
                atexit.unregister(self.close)

    def make_concurrent_api_requests(self, concurrent_api_requests: List[ConcurrentApiRequestRow]):
        concurrent_results = {}
        futures = []
        for concurrent_api_request in concurrent_api_requests:
            futures.append(
                self._executor.submit(
                    lambda c: {c.name: c.method(**c.kwargs)},
                    c=concurrent_api_request,
                )
            )

        for future in as_completed(futures):
            task_result = future.result()
            concurrent_results.update(task_result)
        return concurrent_results


instance = ApiClientThreadsPool(pool_threads=10)
