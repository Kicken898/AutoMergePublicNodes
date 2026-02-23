import os
import yaml
import base64
import requests

# 节点来源网站列表（您可以根据需要增删）
SOURCES = [
    "https://nodefree.org/dy/2024.yaml",
    "https://clashnode.com/wp-content/uploads/2024/01/20240115.yaml",
    # 可添加更多源
]

def fetch_nodes():
    all_proxies = []
    for url in SOURCES:
        try:
            resp = requests.get(url, timeout=10)
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
                    except:
                        print(f"从 {url} 获取的内容既不是 YAML 也不是 Base64，跳过")
            except yaml.YAMLError:
                # 如果 YAML 解析失败，尝试 Base64 解码
                try:
                    decoded = base64.b64decode(resp.text).decode('utf-8')
                    data = yaml.safe_load(decoded)
                    if data and 'proxies' in data:
                        all_proxies.extend(data['proxies'])
                        print(f"从 {url} 获取到 {len(data['proxies'])} 个节点 (Base64)")
                except:
                    print(f"从 {url} 获取的内容无法解析")
        except Exception as e:
            print(f"抓取 {url} 异常: {e}")
    return all_proxies

def merge_with_base(new_proxies):
    # 读取基础配置文件（如果有）
    base_file = 'base.yaml'
    if os.path.exists(base_file):
        with open(base_file, 'r', encoding='utf-8') as f:
            base = yaml.safe_load(f) or {'proxies': []}
    else:
        base = {'proxies': []}

    # 简单去重（根据 server 和 port）
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
        print("已合并并保存为 list.txt")
    else:
        print("未获取到任何新节点")
