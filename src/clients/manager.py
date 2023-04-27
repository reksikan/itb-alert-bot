from src.clients.wildberries import WildberriesClient
from src.clients.ozon import OzonClient
from src.clients.ya_market import YaMarketClient
from src.clients.mpstats import MPStatsClient


class ClientManager:
    def __init__(self):
        self._wb_client = WildberriesClient
        self._ozon_client = OzonClient
        self._ya_market_client = YaMarketClient
        self._mpstats_client = MPStatsClient

    @property
    def wb_client(self):
        return self._wb_client

    @property
    def ozon_client(self):
        return self._ozon_client

    @property
    def ya_market_client(self):
        return self._ya_market_client

    @property
    def mpstats_client(self):
        return self._mpstats_client
