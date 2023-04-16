from typing import Any, Dict, Optional, Tuple

from aiohttp.client import ClientSession
from aiologger.loggers.json import JsonLogger

logger = JsonLogger.with_default_handlers()


class RequestError(Exception):
    pass


class BaseHTTPClient:

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def _http_request(
        self,
        path: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        awaited_result_codes: Tuple[int] = (200, 201),
    ) -> Dict[str, Any]:
        async with ClientSession as session:
            url = self.base_url + path
            logger.info(f'Try to http request {method} {url} with {params=} {body=} {headers=}')
            async with session.request(
                url=url,
                method=method,
                params=params or {},
                body=body or {},
                headers=headers or {},
            ) as response:
                if response.status not in awaited_result_codes:
                    logger.error(f'Got unexpected status code on request {method} {url}, {response.status=}')
                    raise RequestError(await response.json())
                return await response.json()
