# -*- coding: utf-8 -*-
"""
cron: 0 */4 * * *
new Env('IPTV自动整理推送-央视置顶版');
"""

import requests
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor

# 禁用SSL检查警告
requests.packages.urllib3.disable_warnings()

# ================= 1. 环境变量配置 =================
# 请在青龙面板-环境变量中配置以下变量
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_EMAIL = os.getenv("GITHUB_EMAIL")

# 待爬取的原始源地址
SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/cymz6/AutoIPTV-Hotel/main/display.m3u",
    "https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u",
    "https://raw.githubusercontent.com/YueChan/live/main/hotel.m3u",
    "https://raw.githubusercontent.com/Guutong/IPTV/main/live.m3u",
    "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u",
    "https://raw.githubusercontent.com/yuanzl77/IPTV/main/living.m3u"
]

OUTPUT_FILENAME = "iptv_tested_final.m3u"
# =================================================

def get_group(name):
    """根据频道名自动分配分组"""
    name = name.upper()
    if "CCTV" in name or "中央" in name: return "央视频道"
    if "卫视" in name: return "卫视频道"
    provinces = ["北京", "上海", "广东", "深圳", "天津", "重庆", "湖南", "湖北", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "河北", "山西", "内蒙", "辽宁", "吉林", "黑龙江", "四川", "贵州", "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆", "广西", "海南"]
    for p in provinces:
        if p in name: return f"{p}频道"
    return "其他频道"

def get_sort_weight(item):
    """央视置顶排序逻辑"""
    group = item['group']
    name = item['name'].upper()
    if group == "央视频道":
        weight = 0
        nums = re.findall(r'\d+', name)
        if nums:
            weight += int(nums[0])
            if "+" in name: weight += 0.5
        return weight
    if group == "卫视频道": return 100
    if "频道" in group: return 200
    return 900

def check_streaming(item):
    """深度可用性探测：尝试读取数据流"""
    info, url, name = item
    session = requests.Session()
    session.trust_env = False # 直连测速，绕过OpenClash防止误判
    
    # 针对运营商内网/单播特征：GitHub环境测不通，青龙环境若IPv6不稳也难测，故强制保留
    if any(x in url for x in [":6610", ":81", ":808", "rtp://", "udp://", "2409:", "2408:"]):
        return {"group": get_group(name), "info": info, "url": url, "name": name}

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        with session.get(url, headers=headers, timeout=3, stream=True, verify=False) as r:
            if r.status_code == 200:
                # 尝试读取前512字节，确保有实际流数据
                if next(r.iter_content(512)):
                    return {"group": get_group(name), "info": info, "url": url, "name": name}
    except:
        # IPv4 酒店源如果没有特殊端口但属于内网段，保守保留
        if "[:" not in url: 
            return {"group": get_group(name), "info": info, "url": url, "name": name}
    return None

def push_to_github():
    if not all([GITHUB_TOKEN, GITHUB_USER, GITHUB_REPO]):
        print("⚠️ 环境变量缺失，跳过 GitHub 推送流程")
        return

    print("🚀 开始推送至 GitHub...")
    # 基础配置
    os.system(f'git config --global user.email "{GITHUB_EMAIL or "ql@bot.com"}"')
    os.system(f'git config --global user.name "{GITHUB_USER}"')
    os.system(f"git config --global http.sslVerify false")
    
    # 初始化检查
    if not os.path.exists(".git"):
        print("[*] 正在初始化本地仓库...")
        os.system("git init")
        remote_url = f"https://{GITHUB_USER}:{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{GITHUB_REPO}.git"
        os.system(f"git remote add origin {remote_url}")
    else:
        remote_url = f"https://{GITHUB_USER}:{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{GITHUB_REPO}.git"
        os.system(f"git remote set-url origin {remote_url}")

    # 提交与推送
    os.system(f"git add {OUTPUT_FILENAME}")
    os.system(f'git commit -m "Auto Update: {time.strftime("%Y-%m-%d %H:%M:%S")}"')
    
    print("[*] 正在上传...")
    # 尝试推送 main 或 master 分支
    res = os.system("git push -u origin main")
    if res != 0:
        res = os.system("git push -u origin master")
    
    if res == 0: print("✅ GitHub 推送成功！")
    else: print("❌ 推送失败，请检查网络或 Token 权限")

def main():
    print("📡 正在抓取原始源数据...")
    tasks = []
    seen_urls = set()
    
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15, verify=False)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                lines = [l.strip() for l in r.text.split('\n') if l.strip()]
                for i in range(len(lines)):
                    if lines[i].startswith("#EXTINF") and i+1 < len(lines):
                        info, s_url = lines[i], lines[i+1]
                        name = re.search(r',([^,]+)$', info).group(1) if re.search(r',([^,]+)$', info) else "未知"
                        if s_url not in seen_urls:
                            tasks.append((info, s_url, name))
                            seen_urls.add(s_url)
        except: continue

    print(f"[*] 抓取到 {len(tasks)} 条待测链接，开始深度嗅探...")

    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(check_streaming, tasks))
    
    valid_results = sorted([r for r in results if r], key=lambda x: (get_sort_weight(x), x['name']))

    print(f"[*] 测速筛选完成，剩余 {len(valid_results)} 条有效源，正在整理分组...")

    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for item in valid_results:
            # 统一注入分类标签
            clean_info = re.sub(r'group-title="[^"]*"', f'group-title="{item["group"]}"', item["info"])
            if 'group-title="' not in clean_info:
                clean_info = clean_info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{item["group"]}"')
            f.write(f"{clean_info}\n{item['url']}\n")
    
    print(f"✅ 文件生成成功: {OUTPUT_FILENAME}")

if __name__ == "__main__":
    main()
    push_to_github()