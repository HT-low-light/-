import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from lxml import etree


def fetch_page(keyword, page_num):
    jobs_data = []
    url = f'https://sou.zhaopin.com/?jl=551&kw={keyword}&p={page_num}'
    res = requests.get(url)
    res.encoding = 'utf-8'
    # print(res.text)
    html = etree.HTML(res.text)
    page_data_list = html.xpath('//*[@id="positionList-hook"]')
    for pdl in page_data_list:
        # 岗位
        position_text = pdl.xpath("./div/div[1]/div/div[1]/div[1]/div[1]/a/text()")
        # 公司
        company = pdl.xpath("./div/div[1]/div/div[1]/div[2]/div[1]/a/text()")
        company_text = [item.replace("\n", "").replace(" ", "") for item in company]
        # 薪资
        salary = pdl.xpath("./div/div[1]/div/div[1]/div[1]/div[1]/p/text()")
        salary_text = [item.replace("\n", "").replace(" ", "").replace("薪", '').replace("/天", "") for item in salary]

        jobs_data.append({
            "position": position_text,
            "company": company_text,
            "salary": salary_text
        })
        return jobs_data


def Spiders(keyword, page_num):
    jobs_data = []
    with ThreadPoolExecutor(max_workers=3) as executor:  # 可以根据需要调整max_workers
        future_to_page = {executor.submit(fetch_page, keyword, i): i for i in range(1, page_num + 1)}
        for future in as_completed(future_to_page):
            page_num = future_to_page[future]
            try:
                jobs_for_page = future.result()
                jobs_data.extend(jobs_for_page)
            except Exception as exc:
                print(f'Error fetching page {page_num}: {exc}')

    # 保存数据到JSON文件
    with open('jobs_data.json', 'w', encoding='utf-8') as f:
        json.dump(jobs_data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    Spiders("python", 9)