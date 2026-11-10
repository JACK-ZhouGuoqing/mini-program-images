#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键切换为「云存储远程图片」模式（仅在你已完成上传 + 提供 HTTPS 基址后运行）。

用法：
  python apply_cloud.py "https://你的基址/（结尾必须带 /）"

示例：
  python apply_cloud.py "https://env-xxxx.tcb.qcloud.la/assets/"
  python apply_cloud.py "https://cdn.example.com/xiaoman/assets/"

作用：
  1) 把 utils/assets.wxs 的 ASSET_BASE 填为你给的基址，并把 LOCAL 改为 false
  2) 删除本地 images/ 下除 tab/ 图标以外的所有图片，主包瞬间 < 200KB
  3) 复算主包体积，确认切换成功

注意：
  - 必须传入以 http(s):// 开头、结尾带 / 的基址
  - 运行前请确认图片已能从该基址正常访问（先用真机/模拟器确认）
  - 测试号(touristappid)无法开通微信云开发，但用任意 HTTPS 图床地址即可正常显示图片
"""
import os, sys, argparse

PROJECT = r'C:\Users\02030022\WorkBuddy\EV-RT 日常工作\小满智选小程序'
WXS = os.path.join(PROJECT, 'utils', 'assets.wxs')


def main():
    p = argparse.ArgumentParser(description='一键切换为云存储远程图片模式')
    p.add_argument('base', help='云存储/图床的 HTTPS 基址，结尾带 /，例如 https://xxx/aaa/assets/')
    args = p.parse_args()

    base = args.base.strip()
    if not base.startswith('http'):
        print('[错误] 基址必须以 http:// 或 https:// 开头')
        sys.exit(1)
    if not base.endswith('/'):
        base += '/'

    if not os.path.exists(WXS):
        print('[错误] 找不到', WXS)
        sys.exit(1)

    # 1) 填 ASSET_BASE + 关 LOCAL
    t = open(WXS, encoding='utf-8').read()
    if "var ASSET_BASE = '';" not in t:
        print('[警告] 未发现空的 ASSET_BASE 占位，可能已配置过，脚本将尝试强制覆盖。')
    t = t.replace("var ASSET_BASE = '';", "var ASSET_BASE = '%s';" % base)
    t = t.replace('var LOCAL = true;', 'var LOCAL = false;')
    open(WXS, 'w', encoding='utf-8').write(t)
    print('已设置 ASSET_BASE =', base)
    print('已设置 LOCAL = false（不再用本地兜底）')

    # 2) 删除本地大图（保留 tab 图标）
    img_dir = os.path.join(PROJECT, 'images')
    kept = 0
    if os.path.isdir(img_dir):
        for dp, dn, fn in os.walk(img_dir):
            if os.path.basename(dp) == 'tab':
                continue
            for f in fn:
                try:
                    os.remove(os.path.join(dp, f))
                    kept += 1
                except OSError:
                    pass
        for dp, dn, fn in os.walk(img_dir, topdown=False):
            if os.path.basename(dp) == 'tab':
                continue
            try:
                os.rmdir(dp)
            except OSError:
                pass
    print('已删除本地大图 %d 个（tab 图标已保留）' % kept)

    # 3) 复算主包体积
    tot = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(PROJECT)
              if '.workbuddy' not in r for f in fs)
    print('当前主包体积: %dKB (%.2fMB)' % (tot // 1024, tot / 1024 / 1024))
    print('切换完成。请到分享面板点「发布」-> 超小包 + 高清远程图。')


if __name__ == '__main__':
    main()
