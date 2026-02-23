import os
import yaml
import base64
import requests

# 当前可能有效的免费节点源（2026年2月）
SOURCES = [
    # 基于 GitHub 的节点池
    "https://raw.githubusercontent.com/mfuu/v2ray/master/clash.yaml",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/clash.yml",
    "https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/clash/clash.provider.yaml",
    "https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/clash.yml",
    "https://raw.githubusercontent.com/adiwzx/freenode/main/adispeed.yml",
    # 其他来源
    "https://yoyapai.com/clash/proxies",  # 可能有效
    "https://nodefree.org/raw/clash.yaml",  # nodefree 新地址
]

def fetch_nodes():
    all_proxies = []
    for url in SOURCES:
        try:
            print(f"正在抓取: {url}")
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                print(f"抓取 {url} 失败，状态码：{resp.status_code}")
                continue

            # 尝试解析为 YAML
            try:
                data = yaml.safe_load(resp.text)
                if data and 'proxies' in data:
                    all_proxies.extend(data['proxies'])
                    print(f"从 {url} 获取到 {len(data['proxies'])} 个节点 (YAML)")
                else:
                    # 如果不是 YAML，可能是 Base64 编码的订阅
                    try:
                        decoded = base64.b64decode(resp.text).decode('utf-8')
                        data2 = yaml.safe_load(decoded)
                        if data2 and 'proxies' in data2:
                            all_proxies.extend(data2['proxies'])
                            print(f"从 {url} 获取到 {len(data2['proxies'])} 个节点 (Base64 -> YAML)")
                        else:
                            print(f"从 {url} 获取的内容解码后无 proxies 字段，跳过")
                    except Exception as e:
                        print(f"从 {url} 获取的内容不是 Base64 或无法解析: {e}")
            except yaml.YAMLError:
                # 如果 YAML 解析失败，尝试 Base64 解码
                try:
                    decoded = base64.b64decode(resp.text).decode('utf-8')
                    data = yaml.safe_load(decoded)
                    if data and 'proxies' in data:
                        all_proxies.extend(data['proxies'])
                        print(f"从 {url} 获取到 {len(data['proxies'])} 个节点 (Base64)")
                    else:
                        print(f"从 {url} 解码后无 proxies 字段")
                except Exception as e:
                    print(f"从 {url} 获取的内容无法解析为 YAML 或 Base64: {e}")
        except Exception as e:
            print(f"抓取 {url} 异常: {e}")
    return all_proxies

def merge_with_base(new_proxies):
    base_file = 'base.yaml'
    if os.path.exists(base_file):
        with open(base_file, 'r', encoding='utf-8') as f:
            base = yaml.safe_load(f) or {'proxies': []}
    else:
        base = {'proxies': []}

    # 去重（根据 server 和 port）
    existing = {(p.get('server'), p.get('port')) for p in base.get('proxies', [])}
    for p in new_proxies:
        key = (p.get('server'), p.get('port'))
        if key not in existing:
            base['proxies'].append(p)
            existing.add(key)
    return base

if __name__ == '__main__':
    print("开始抓取节点...")
    new_nodes = fetch_nodes()
    print(f"共抓取到 {len(new_nodes)} 个新节点")

    if new_nodes:
        final_config = merge_with_base(new_nodes)
        # 以 YAML 格式写入 list.txt
        with open('list.txt', 'w', encoding='utf-8') as f:
            yaml.dump(final_config, f, allow_unicode=True, sort_keys=False)
        print("已合并并保存为 list.txt，节点总数:", len(final_config['proxies']))
    else:
        print("未获取到任何新节点，保留原有文件。")
