# 校验 index.json 的结构、字段、唯一性与排序。

import hashlib
import json
import os
import re
import sys

INDEX_PATH = 'index.json'
KINDS = ('plugin', 'theme')
REQUIRED_FIELDS = ('id', 'kind', 'name', 'version', 'author', 'summary',
                   'repo', 'asset', 'sha256')
ALLOWED_FIELDS = REQUIRED_FIELDS + ('license', 'min_client',
                                    'yanked', 'yank_reason')
ID_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_]*$')
VERSION_RE = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$')
REPO_RE = re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')
ASSET_RE = re.compile(r'^[A-Za-z0-9_.-]+\.zip$')
SHA256_RE = re.compile(r'^[0-9a-f]{64}$')
MIN_CLIENT_RE = re.compile(r'^[0-9]+\.[0-9]+$')
DATE_RE = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
SUMMARY_LIMIT = 120


def hash_file(path):
    # 返回文件的 sha256（小写十六进制）。
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def validate_entry(position, entry, seen):
    # 校验一条条目，返回问题列表。
    if not isinstance(entry, dict):
        return ['第 %d 条不是 JSON 对象。' % position]
    label = '第 %d 条（%s）' % (position, entry.get('id') or '缺 id')
    errors = []
    if not all(entry.get(field) for field in REQUIRED_FIELDS):
        missing = [field for field in REQUIRED_FIELDS if not entry.get(field)]
        errors.append('%s：缺少必需字段 %s。' % (label, '、'.join(missing)))
        return errors
    for field in entry:
        if field not in ALLOWED_FIELDS:
            errors.append('%s：出现未定义的字段 %s。' % (label, field))
    identifier = str(entry['id'])
    if not ID_RE.match(identifier):
        errors.append('%s：id 只能由字母、数字与下划线组成，且以字母开头。'
                      % label)
    if identifier in seen:
        errors.append('%s：id 与前面的条目重复。' % label)
    seen.add(identifier)
    if entry['kind'] not in KINDS:
        errors.append('%s：kind 必须是 %s。' % (label, ' 或 '.join(KINDS)))
    if not VERSION_RE.match(str(entry['version'])):
        errors.append('%s：version 必须是语义化版本，例如 1.0.0。' % label)
    if not REPO_RE.match(str(entry['repo'])):
        errors.append('%s：repo 应形如 owner/name。' % label)
    if not ASSET_RE.match(str(entry['asset'])):
        errors.append('%s：asset 必须是以 .zip 结尾的文件名。' % label)
    if not SHA256_RE.match(str(entry['sha256'])):
        errors.append('%s：sha256 必须是 64 位小写十六进制。' % label)
    if len(str(entry['summary'])) > SUMMARY_LIMIT:
        errors.append('%s：summary 超过 %d 字。' % (label, SUMMARY_LIMIT))
    if entry.get('min_client') and not MIN_CLIENT_RE.match(
            str(entry['min_client'])):
        errors.append('%s：min_client 应形如 1.0。' % label)
    if entry.get('yanked') and not entry.get('yank_reason'):
        errors.append('%s：yanked 为 true 时必须填 yank_reason。' % label)
    return errors


def validate(data):
    # 校验整个索引，返回问题列表；空列表表示通过。
    if not isinstance(data, dict):
        return ['索引顶层必须是一个 JSON 对象。']
    errors = []
    if data.get('schema') != 1:
        errors.append('schema 必须为 1（当前是 %r）。' % data.get('schema'))
    if data.get('updated') and not DATE_RE.match(str(data['updated'])):
        errors.append('updated 必须是 YYYY-MM-DD 格式。')
    packages = data.get('packages')
    if not isinstance(packages, list):
        return errors + ['packages 必须是数组。']
    seen = set()
    for position, entry in enumerate(packages, 1):
        errors.extend(validate_entry(position, entry, seen))
    identifiers = [str(entry.get('id')) for entry in packages
                   if isinstance(entry, dict)]
    if identifiers != sorted(identifiers):
        errors.append('条目未按 id 字母序排列，请插入到正确位置而不是追加到末尾。')
    return errors


def main(argv):
    # 命令行入口，返回进程退出码。
    if len(argv) > 2 and argv[1] == '--hash':
        if not os.path.exists(argv[2]):
            print('找不到文件：%s' % argv[2])
            return 1
        print(hash_file(argv[2]))
        return 0
    path = argv[1] if len(argv) > 1 else INDEX_PATH
    if not os.path.exists(path):
        print('找不到索引文件：%s' % path)
        return 1
    try:
        with open(path, encoding='utf-8') as handle:
            data = json.load(handle)
    except (OSError, ValueError) as exc:
        print('索引文件无法解析：%s' % exc)
        return 1
    errors = validate(data)
    if errors:
        print('校验未通过，共 %d 个问题：' % len(errors))
        for message in errors:
            print('  - %s' % message)
        return 1
    print('校验通过：%d 个条目。' % len(data['packages']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
