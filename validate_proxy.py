#!/usr/bin/env python3
import asyncio
import aiohttp
import time
import json
from sys import stderr
from loguru import logger
from urllib3 import disable_warnings
import requests


PARALLEL_COUNT = 200



index = 0
counter = 0
proxies=[]

valid_proxies=[]

def _load_proxies(file_name: str):
    with open(file_name, 'r') as file:
        # data = json.load(file)
        proxies = [
                        # f'http://{proxy_data["auth"]}@{proxy_data["ip"]}'
                        f'{proxy_data["ip"]}'
                        for proxy_data in json.load(file)
                    ]
        print(f"Proxy count {len(proxies)}")
        return(proxies)


TIMEOUT = aiohttp.ClientTimeout(
    total=10,
    connect=10,
    sock_read=10,
    sock_connect=10,
)


def get_index():
    global counter
    counter -= 1 
    return counter


async def start_one(url: str):
    global proxies
    cntr = get_index()
    while cntr >= 0:
        try:
            proxy = proxies[cntr]
            for scheme in ["http", "https","socks5","socks4"]:
                proxy_scheme = f'{scheme}://{proxy}'
                async with aiohttp.ClientSession() as session:
                    status = await request(session, url, proxy_scheme)
                    # print(f'{proxy}    {status}')
                    if (status >= 200) and (status < 300):
                        valid_proxies.append({"scheme":scheme,"ip":proxy})
                    # else:
                        

        except Exception as e:
            logger.warning(f'Exception, retrying, exception={e}')
        cntr = get_index()
        

async def request(session: aiohttp.ClientSession, url: str, proxy: str = None) -> int:
    try:
        async with session.get(url, proxy=proxy, verify_ssl=False) as response:
            return response.status
    except Exception as e:
            logger.warning(f'Exception on request, exception={e}, url={url}, proxy={proxy}')
    return -1


def main():
    global counter
    global proxies
    proxies = _load_proxies("proxy.json")[:10]
    counter = len(proxies)
    loop = asyncio.get_event_loop()
    union = asyncio.gather(*[
        start_one("https://github.com")
        # start_one("https://postman-echo.com/get")
        for _ in range(PARALLEL_COUNT)
    ])
    loop.run_until_complete(union)
    
    # print(valid_proxies)
    # res_dct = [ {"ip":valid_proxies[i]}for i in range(0, len(valid_proxies))  ]
    jsonString = json.dumps(valid_proxies)
    jsonFile = open("valid_proxy2.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()


if __name__ == '__main__':
    logger.remove()
    logger.add(
        stderr,
        format='<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>'
    )
    disable_warnings()
    main()
