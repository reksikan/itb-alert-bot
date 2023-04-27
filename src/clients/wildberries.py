from typing import List

from src.clients.base import BaseHTTPClient


class WildberriesClient(BaseHTTPClient):

    async def get_products(self, api_keys: str) -> List[int]:
        product_ids = []
        for api_key in api_keys:
            limit = 1000
            total = 1001
            last_prod_id = ''
            last_updated_at = ''

            while total > limit:
                result = await self._http_request(
                    'https://suppliers-api.wildberries.ru/content/v1/cards/cursor/list',
                    'POST',
                    headers={'Authorization': api_key},
                    body={
                        "sort": {
                            "cursor": {
                                "limit": limit
                            },
                            "filter": {
                                          "withPhoto": -1
                            } | ({'nmID': last_prod_id, 'updatedAt': last_updated_at} if last_prod_id else {})
                        }
                    }
                )
                total = result['cursor']['total']
                last_prod_id = result['cards'][-1]['nmID']
                last_updated_at = result['cards'][-1]['updateAt']
                for card in result['cards']:
                    product_ids.append(card['nmID'])

        return product_ids

    async def get_rate(self, product_wb_id: str, api_keys: List[str]) -> float:
        for api_key in api_keys:
            result = await self._http_request(
                'https://feedbacks-api.wildberries.ru/api/v1/feedbacks/products/rating/nmid',
                'GET',
                params={'nmId': product_wb_id},
                headers={'Authorization': api_key},
            )
            if result['error']:
                return result['data']['valuation']
        raise Exception('Нет доступного товара среди все кабинетов')

    async def check_available(self, product_wb_id: str) -> bool:
        return await self._http_request(
            'https://product-order-qnt.wildberries.ru/by-nm/',
            'GET',
            params={'nm': product_wb_id}
        ) != []
