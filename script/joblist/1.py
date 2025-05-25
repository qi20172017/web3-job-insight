import requests

cookies = {
    '_ga': 'GA1.1.1131030652.1748042377',
    'cf_clearance': 'YvrSf3rHNsIZIcx6SWtDgN9gP.659Cfs0EMBwilaChM-1748044899-1.2.1.1-oaNM9o3T0V.WWeWeCAWPFzxFSehlCraLImNEQUAgaWZ22kiGDHiGDEBJP8vvBb6vObYtij2gJbWJQveq7slINAKTAi4V1VP0xUCErxCRV_hhifziOPiYGeGsy.hcoDvOHHMznvqcnxzsVi98Mza_90voU49XqmgS5uuSBsEw1IMYrYh4a.eJz3Efnz7ZLD7q9M4lW0UPVNg3jH5Tsu89ow55vvZmSQjKV5_.tlEk3iH0WMapS8YG8YdTNIwPagrx.BmXFw4WQdnDU60VyayO90onzM9M_4OdddjC_2vu5vEP8f3K_KjGmw03wRg4KjE_68tqRSaIlDD2CnIySAL6Mkf2X6h8K5tFlEvvHIYuF4Q',
    '_ga_8FJ0E1ZNFE': 'GS2.1.s1748132953$o4$g1$t1748134555$j60$l0$h0',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'priority': 'u=1, i',
    'referer': 'https://cryptojobslist.com/',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'x-nextjs-data': '1',
    # 'cookie': '_ga=GA1.1.1131030652.1748042377; cf_clearance=YvrSf3rHNsIZIcx6SWtDgN9gP.659Cfs0EMBwilaChM-1748044899-1.2.1.1-oaNM9o3T0V.WWeWeCAWPFzxFSehlCraLImNEQUAgaWZ22kiGDHiGDEBJP8vvBb6vObYtij2gJbWJQveq7slINAKTAi4V1VP0xUCErxCRV_hhifziOPiYGeGsy.hcoDvOHHMznvqcnxzsVi98Mza_90voU49XqmgS5uuSBsEw1IMYrYh4a.eJz3Efnz7ZLD7q9M4lW0UPVNg3jH5Tsu89ow55vvZmSQjKV5_.tlEk3iH0WMapS8YG8YdTNIwPagrx.BmXFw4WQdnDU60VyayO90onzM9M_4OdddjC_2vu5vEP8f3K_KjGmw03wRg4KjE_68tqRSaIlDD2CnIySAL6Mkf2X6h8K5tFlEvvHIYuF4Q; _ga_8FJ0E1ZNFE=GS2.1.s1748132953$o4$g1$t1748134555$j60$l0$h0',
}

params = {
    'page': '2',
}

response = requests.get(
    'https://cryptojobslist.com/_next/data/-N4d-XdsLSxqWmcTCJXr1/index.json',
    params=params,
    cookies=cookies,
    headers=headers,
)

print(response.json())

def func2():

    cookies = {
        '_ga': 'GA1.1.1131030652.1748042377',
        'cf_clearance': 'YvrSf3rHNsIZIcx6SWtDgN9gP.659Cfs0EMBwilaChM-1748044899-1.2.1.1-oaNM9o3T0V.WWeWeCAWPFzxFSehlCraLImNEQUAgaWZ22kiGDHiGDEBJP8vvBb6vObYtij2gJbWJQveq7slINAKTAi4V1VP0xUCErxCRV_hhifziOPiYGeGsy.hcoDvOHHMznvqcnxzsVi98Mza_90voU49XqmgS5uuSBsEw1IMYrYh4a.eJz3Efnz7ZLD7q9M4lW0UPVNg3jH5Tsu89ow55vvZmSQjKV5_.tlEk3iH0WMapS8YG8YdTNIwPagrx.BmXFw4WQdnDU60VyayO90onzM9M_4OdddjC_2vu5vEP8f3K_KjGmw03wRg4KjE_68tqRSaIlDD2CnIySAL6Mkf2X6h8K5tFlEvvHIYuF4Q',
        '_ga_8FJ0E1ZNFE': 'GS2.1.s1748132953$o4$g1$t1748134605$j10$l0$h0',
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'priority': 'u=1, i',
        'referer': 'https://cryptojobslist.com/?page=2',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'x-nextjs-data': '1',
        # 'cookie': '_ga=GA1.1.1131030652.1748042377; cf_clearance=YvrSf3rHNsIZIcx6SWtDgN9gP.659Cfs0EMBwilaChM-1748044899-1.2.1.1-oaNM9o3T0V.WWeWeCAWPFzxFSehlCraLImNEQUAgaWZ22kiGDHiGDEBJP8vvBb6vObYtij2gJbWJQveq7slINAKTAi4V1VP0xUCErxCRV_hhifziOPiYGeGsy.hcoDvOHHMznvqcnxzsVi98Mza_90voU49XqmgS5uuSBsEw1IMYrYh4a.eJz3Efnz7ZLD7q9M4lW0UPVNg3jH5Tsu89ow55vvZmSQjKV5_.tlEk3iH0WMapS8YG8YdTNIwPagrx.BmXFw4WQdnDU60VyayO90onzM9M_4OdddjC_2vu5vEP8f3K_KjGmw03wRg4KjE_68tqRSaIlDD2CnIySAL6Mkf2X6h8K5tFlEvvHIYuF4Q; _ga_8FJ0E1ZNFE=GS2.1.s1748132953$o4$g1$t1748134605$j10$l0$h0',
    }

    params = {
        'tag': 'solidity',
        'location': 'all',
    }

    response = requests.get(
        'https://cryptojobslist.com/_next/data/-N4d-XdsLSxqWmcTCJXr1/tags/solidity/all.json',
        params=params,
        cookies=cookies,
        headers=headers,
    )