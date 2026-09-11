# 下载索引里各条目的 Release 附件，重算 sha256 并与索引比对。

import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

INDEX_PATH = 'index.json'
TOKEN_ENV = 'GITHUB_TOKEN'
TIMEOUT = 60


def asset_url(entry):
    # 按「仓库 + 版本 + 附件名」拼出固定下载地址（不使用 latest）。
    return 'https://github.com/%s/releases/download/v%s/%s' % (
        entry['repo'], entry['version'], entry['asset'])


def download(url, token):
    # 下载并返回内容字节，失败时抛出异常。
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'easyplugin-registry-verifier')
    if token:
        request.add_header('Authorization', 'Bearer %s' % token)
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read()


def verify(entry, token):
    # 核验单条条目，返回 (是否通过, 说明文字)。
    url = asset_url(entry)
    try:
        payload = download(url, token)
    except (urllib.error.URLError, OSError) as exc:
        return False, '下载失败（%s）：%s' % (url, exc)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != entry['sha256']:
        return False, '哈希不符：索引为 %s，实际为 %s' % (
            entry['sha256'], digest)
    return True, '哈希一致，共 %d 字节' % len(payload)


def main(argv):
    # 命令行入口，返回进程退出码。
    wanted = argv[1] if len(argv) > 1 else ''
    path = argv[2] if len(argv) > 2 else INDEX_PATH
    if not os.path.exists(path):
        print('找不到索引文件：%s' % path)
        return 1
    with open(path, encoding='utf-8') as handle:
        packages = json.load(handle).get('packages', [])
    targets = [entry for entry in packages
               if not wanted or entry.get('id') == wanted]
    if not targets:
        print('索引里没有匹配的条目：%s' % (wanted or '（空索引）'))
        return 1
    token = os.environ.get(TOKEN_ENV, '')
    failures = 0
    for entry in targets:
        passed, message = verify(entry, token)
        mark = '[OK]  ' if passed else '[FAIL]'
        pieces = [mark, entry.get('id'), entry.get('version'), message]
        print(' '.join(str(piece) for piece in pieces))
        failures += 0 if passed else 1
    passed_count = len(targets) - failures
    print('核验完成：%d 条通过，%d 条失败。' % (passed_count, failures))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
