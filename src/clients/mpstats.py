from typing import List

from src.clients.base import BaseHTTPClient


class MPStatsClient(BaseHTTPClient):

    async def get_ozon_rate(self, mpstats_tokens: List[str], product_id: str) -> int: pass
