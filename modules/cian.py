import requests
import json
import time
from modules.logger import Logger

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

CFG_PATH = "./configs/cian.json"
SUCCESS_STATUS = "ok"

class Cian:
    def __init__(self, config=None, proxies=[], logger=Logger()) -> None:
        self.config = config
        self.logger = logger
        self.last_update = None
        self.last_token_obtain = None
        self.headers = {
            'Host': 'api.cian.ru',
            'BuildNumber': '0',
            'Accept': '*/*',
            'Os': 'ios',
            'Accept-Language': 'ru-RU;q=1, en-RU;q=0.9',
            'Content-Type': 'application/json',
            'ApplicationID': '0',
            'VersionCode': '0',
            'User-Agent': 'Cian/1.331.1 (iPhone; iOS 17.4.1; Scale/3.00; 0',
            'Device': 'Phone',
        }
        self.proxies_list = proxies
        self.current_proxy = 0
        self.proxy = None

        self._obtain_token()
        if not self.config:
            self._parse_config()

    def _switch_proxy(self) -> None:
        if len(self.proxies_list) == 0:
            return
        self.current_proxy = (self.current_proxy + 1) % len(self.proxies_list)
        self.logger.log("current ip: {}".format(self.proxies_list[self.current_proxy]))
        self.proxy = { 
            "https": f"http://{self.proxies_list[self.current_proxy]}/",
            "https": f"https://{self.proxies_list[self.current_proxy]}/", 
        }

    def _parse_config(self) -> bool:
        try:
            with open(CFG_PATH, "r", encoding="utf-8") as f:
                json_file = json.load(f)
                self.config = json.dumps(json_file).encode()
                return True
        except Exception as e:
            return False

    def _obtain_token(self) -> bool:
        self._switch_proxy()
        r = requests.post(
            'https://api.cian.ru/1.4/ios/get-session-anonymous',
            headers=self.headers,
            proxies=self.proxy,
            verify=False
        )
        if r.status_code != 200:
            self.logger.log("request failed: {}\n{}".format(r.status_code, r.text))
            return False
        try:
            body = r.json()
        except Exception as e:
            self.logger.log("decoding failed: {}".format(e))
            return False
        if body.get("status", "") != SUCCESS_STATUS:
            self.logger.log("responsed with error: {}".format(body))
            return False
        if body.get("data", {"sid": None})["sid"]:
            self.headers["Authorization"] = "simple {}".format(body["data"]["sid"])
            self.last_token_obtain = time.time()
            self.logger.log("new token obtained: {}...".format(self.headers["Authorization"][7:17]))
            return True
        self.logger.log("unable to find token: {}".format(body))
        return False

    def _get_offers(self) -> dict:
        self._switch_proxy()
        r = requests.post(
            'https://api.cian.ru/search-offers/v4/search-offers-mobile-apps/',
            params={
                'tz_offset': '3',
            },
            headers=self.headers,
            data=self.config,
            proxies=self.proxy,
            verify=False
        )
        if r.status_code != 200:
            self.logger.log("request failed: {}\n{}".format(r.status_code, r.text))
            return {}
        try:
            return r.json()["items"]
        except Exception as e:
            self.logger.log("decoding failed: {}".format(e))
            return {}

    def get_last_offer(self) -> int:
        return self._get_offers()[0]["offer"]["id"]

    def parse_offers(self):
        offers = self._get_offers()
        for offer in offers:
            yield {
                "id": offer["offer"]["id"],
                "info": offer["offer"]["formattedFullInfo"],
                "price": offer["offer"]["formattedShortPrice"],
                "additional": offer["offer"]["formattedAdditionalInfo"],
                "url": offer["offer"]["siteUrl"],
                "imgs": [photo["full"] for photo in offer["offer"]["photos"][:5]],
                "address": offer["offer"]["geo"]["userInput"],
                "underground": ", ".join(
                    "{} ({} {})".format(
                        u["name"],
                        u["time"],
                        "пешком" if u["transportType"] == "walk" else "ехать"
                    ) for u in offer["offer"]["geo"]["undergrounds"]
                ),
                "created_at": offer["offer"]["creationDate"],
            }
    def refresher(self) -> None:
        while True:
            time.sleep(60 * 60)
            self._obtain_token()
        

def main() -> None:
    cian = Cian(
        config='{"query":{"geo":{"type":"geo","value":[{"name":"Выделенная область","type":"polygon","coordinates":[["37.485679434077895","55.924208530196694"],["37.45322063338472","55.91828501733163"],["37.43049946423207","55.90119286721603"],["37.404938148935344","55.88226873419615"],["37.391548882350804","55.8640198332477"],["37.38465137838131","55.846218861597826"],["37.379782556420025","55.82772456823048"],["37.39966359181062","55.810592345145956"],["37.418733132110276","55.79276679617156"],["37.43374534553959","55.77561911546829"],["37.4641754827976","55.763496850258875"],["37.49582282554593","55.74976896207237"],["37.5278759034577","55.73283121617271"],["37.55384295391789","55.71496992316358"],["37.58914191313718","55.70763983956673"],["37.62200646137583","55.70237048883059"],["37.65730542059512","55.70007924419467"],["37.68895276334345","55.71451183340212"],["37.70842805118858","55.732602277154065"],["37.7157312841305","55.7511419692618"],["37.71289113798639","55.76944409490886"],["37.70558790504447","55.78705174472042"],["37.67840364909398","55.80670798803897"],["37.65487100961448","55.82521231621453"],["37.64472763052845","55.84576231873926"],["37.64472763052845","55.8640198332477"],["37.662985712883255","55.882724846378146"],["37.67799791393057","55.901420812317305"],["37.64513336569192","55.918740704442065"],["37.61105161196295","55.92124688739648"],["37.57656412307051","55.9221581863095"],["37.54410530999533","55.92261382769752"],["37.51002355626636","55.9221581863095"],["37.477970478354564","55.92010773349807"],["37.441454313644954","55.9059794318683"]]}]},"price":{"value":{"gte":45000,"lte":65000},"type":"range"},"engine_version":{"value":"2","type":"term"},"region":{"type":"terms","value":[1]},"for_day":{"value":"!1","type":"term"},"total_area":{"type":"range","value":{"gte":30}},"sort":{"type":"term","value":"creation_date_desc"},"objects_on_images":{"value":[],"type":"terms"},"outdated_repair":{"value":false,"type":"term"},"with_neighbors":{"value":false,"type":"term"},"limit":{"value":20,"type":"term"},"page":{"value":1,"type":"term"},"bbox":{"type":"term","value":[[37.792723782201364,56.064596450425725],[37.338119359589626,55.565132328609153]]},"building_status":{"type":"term","value":1},"_type":"flatrent","room":{"value":[2,1],"type":"terms"}}}'.encode()
    )
    for x in cian.parse_offers():
        cian.logger.log(x)

if __name__ == "__main__":
    main()