#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
抖音周榜全套接口 - Python版本

整合了三个接口：
1. subscribe - 订阅排行榜查询
2. qrcode_url - 用户信息查询（通过sec_user_id）
3. userinfo - 用户信息查询（通过URL或ID）

使用方法：
1. http://localhost:5000/subscribe?author_id=1805844061108371&rank_type=3
2. http://localhost:5000/qrcode_url?sec_user_id=MS4wLjABAAAABBfmGuCLPobQCxEFBH7R7yCG94Gu19wQklcbTz6Q8Do
3. http://localhost:5000/userinfo?url=https://www.douyin.com/user/MS4wLjABAAAAyiUBvOEjnzVYHl3xyIopxDpk1e7ECR-TW10I14EdS80
   http://localhost:5000/userinfo?id=MS4wLjABAAAAyiUBvOEjnzVYHl3xyIopxDpk1e7ECR-TW10I14EdS80
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import re
import urllib.parse
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
CORS(app)  # 允许所有来源的跨域请求

# Cookie 配置
# subscribe 接口使用的 Cookie（移动端）
# COOKIE_SUBSCRIBE = 'passport_csrf_token=11465e03d160e14d14bb68427cfe8cd9; passport_csrf_token_default=11465e03d160e14d14bb68427cfe8cd9; multi_sids=4229184618762131%3A9de948c68d715b52c852329066720db9; odin_tt=0e565b50494782c846111c8a04a4f092a87221e65e1f648b3f0346f93484f6609d96b9868e5a317b856a3a0c2526c412f1f0793e773c82442b5a8a16961f67d237ecf773a3aac6140399ec4ad079d004; passport_assist_user=Ckuj8_nQce9mLEoRNnDAxpZe7dMp0txdRRb4sTKHX5vuaolZ_Ce0bubPNcpy4Qcn2Qk3kaYnM6OEd_IvjXQbVu4uqCwKUCI8OKoU6ycaSgo8AAAAAAAAAAAAAE_cBFaqe2m-fyzton93-5PznCLqYFuDLMisIbBgDvTyBOzYqQ4f00X3I2a3mfAyU1VHEIrxhA4Yia_WVCABIgEDmqWBFQ%3D%3D; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; sid_guard=9de948c68d715b52c852329066720db9%7C1766413603%7C5184000%7CFri%2C+20-Feb-2026+14%3A26%3A43+GMT; uid_tt=b233129ca4eaf42b86a4250a80fb1bed; uid_tt_ss=b233129ca4eaf42b86a4250a80fb1bed; sid_tt=9de948c68d715b52c852329066720db9; sessionid=9de948c68d715b52c852329066720db9; sessionid_ss=9de948c68d715b52c852329066720db9; session_tlb_tag=sttt%7C12%7CnelIxo1xW1LIUjKQZnINuf________-iC9AAOvyaasawFGoWteos_DMZ6ejz3-I7jx5f9VrTsl4%3D; is_staff_user=false; store-region=cn-gd; store-region-src=did; passport_csrf_token_default=11465e03d160e14d14bb68427cfe8cd9; multi_sids=4229184618762131%3A9de948c68d715b52c852329066720db9; odin_tt=0e565b50494782c846111c8a04a4f092a87221e65e1f648b3f0346f93484f6609d96b9868e5a317b856a3a0c2526c412f1f0793e773c82442b5a8a16961f67d237ecf773a3aac6140399ec4ad079d004; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; sid_guard=9de948c68d715b52c852329066720db9%7C1766413603%7C5184000%7CFri%2C+20-Feb-2026+14%3A26%3A43+GMT; uid_tt=b233129ca4eaf42b86a4250a80fb1bed; sid_tt=9de948c68d715b52c852329066720db9; sessionid=9de948c68d715b52c852329066720db9; is_staff_user=false; store-region=cn-gz; store-region-src=uid'
COOKIE_SUBSCRIBE = ""
# qrcode_url 和 userinfo 接口使用的 Cookie（Web端）
# COOKIE_WEB = "hevc_supported=true; UIFID=973a3fd64dcc46a3490fd9b60d4a8e663b34df4ccc4bbcf97643172fb712d8b0af849bef1014ced93a67391f3e94eae8588e1b42ddf55a3e0acc3751436ace3927fc8c79ec49eec532867b9efbb5b62248d0d42a592d66a69ecbbd5bc6d01b3588badf404161dab873d63372c77881fb0dc4687687a5104e127ead6325556c7848b40c01004032a34f26dfad472b9845195d68854193bced0b6331fa306a7904; bd_ticket_guard_client_web_domain=2; store-region=cn-gz; store-region-src=uid; SelfTabRedDotControl=%5B%5D; my_rd=2; SEARCH_RESULT_LIST_TYPE=%22single%22; xgplayer_device_id=28551481219; live_use_vvc=%22false%22; theme=%22light%22; enter_pc_once=1; fpk1=U2FsdGVkX19tVdrXolUdD7WijZtWBytYvCmzt4vOKYMMdW6u8QUfjMiJR61kMeCmNQb8MdOCnw9nJtxD3UAHwQ==; fpk2=a3f57bbe21c4e30379228ad7788f224d; __live_version__=%221.1.4.539%22; __druidClientInfo=JTdCJTIyY2xpZW50V2lkdGglMjIlM0ExMzc2JTJDJTIyY2xpZW50SGVpZ2h0JTIyJTNBNjc0JTJDJTIyd2lkdGglMjIlM0ExMzc2JTJDJTIyaGVpZ2h0JTIyJTNBNjc0JTJDJTIyZGV2aWNlUGl4ZWxSYXRpbyUyMiUzQTEuMjUlMkMlMjJ1c2VyQWdlbnQlMjIlM0ElMjJNb3ppbGxhJTJGNS4wJTIwKFdpbmRvd3MlMjBOVCUyMDEwLjAlM0IlMjBXaW42NCUzQiUyMHg2NCklMjBBcHBsZVdlYktpdCUyRjUzNy4zNiUyMChLSFRNTCUyQyUyMGxpa2UlMjBHZWNrbyklMjBDaHJvbWUlMkYxNDAuMC4wLjAlMjBTYWZhcmklMkY1MzcuMzYlMjIlN0Q=; passport_csrf_token=6d4478db894a507fa53c9e9fe0473b37; passport_csrf_token_default=6d4478db894a507fa53c9e9fe0473b37; dy_swidth=1536; dy_sheight=864; is_dash_user=1; xgplayer_user_id=82377755329; s_v_web_id=verify_mj2ias9d_egPq4j92_mihB_4V5s_9tlX_5njB62ldN8Fk; passport_mfa_token=CjdKBgTkUXDDmRwed12FR55eo5FqujnYdwEmF75MgG0moVbHUJIMku1L3HkAb2Va3O6vu0WQRLx0GkoKPAAAAAAAAAAAAABP0g6biwGh7J4NbJoN4U7F%2B5QoqEf6kVcDlqzgqOkhOfA3lWTars2W3OEsctlRP7B8vBDH%2B4MOGPax0WwgAiIBAzjvQpk%3D; d_ticket=37ebc73090fc101741276f13e1674e949ceca; n_mh=XPrGlncfCwvX48AijwWOz7NPclXMq_x49jQE-05HlAg; session_tlb_tag_bk=sttt%7C19%7CvE_AtpzHIG1x0qUDz4RNYv________-dLBcHY_H75Ldhos8yUd9hCngP1NJM54rAONzOXlvUr9A%3D; __security_server_data_status=1; __security_mc_1_s_sdk_crypt_sdk=cec82b4e-44bd-af6f; __security_mc_1_s_sdk_cert_key=0d7f4670-4c71-9e14; download_guide=%223%2F20251217%2F0%22; volume_info=%7B%22isUserMute%22%3Atrue%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.875%7D; strategyABtestKey=%221766494919.293%22; is_staff_user=false; publish_badge_show_info=%220%2C0%2C0%2C1766494932201%22; feed_cache_data=%7B%22uuid%22%3A%2234384835224%22%2C%22scmVersion%22%3A%221.0.8.2024%22%2C%22date%22%3A1766495959826%2C%22dyQ%22%3A%221766495930%22%2C%22awemeId%22%3A%227575515727310884115%22%2C%22awemeInfoVersion%22%3A%223.0%22%7D; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A1%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; ttwid=1%7C-FAWbE-c8cN-vq6Dx502LM41mDVSGMxsMDU1HaFM9rw%7C1766496310%7Cf2f3d3f82bb0de6368edbef180c9e5c586eb0836c2bf245d8175d1e704aa9593; passport_assist_user=CkEKzWgXNoMGl_27qzgahMW85Ro6WkFHi7C_6PVX7laEcVhXo9a9XC8g1yS5ag-QLvqTs_vAhuGhsAWeVM0GCDEZGRpKCjwAAAAAAAAAAAAAT90m9zRuWZH7CQXSejXuNSiIIdqrhFFHq_2VgTcQTf3xay0dV77p6qV9XdfC3Yupl0wQk_uEDhiJr9ZUIAEiAQMjjC2Q; sid_guard=0e7f2a8ef37cd0cc080bca6c1cb397cb%7C1766496312%7C5184000%7CSat%2C+21-Feb-2026+13%3A25%3A12+GMT; uid_tt=f6e70850789536affb4e1c4f0b005398; uid_tt_ss=f6e70850789536affb4e1c4f0b005398; sid_tt=0e7f2a8ef37cd0cc080bca6c1cb397cb; sessionid=0e7f2a8ef37cd0cc080bca6c1cb397cb; sessionid_ss=0e7f2a8ef37cd0cc080bca6c1cb397cb; session_tlb_tag=sttt%7C7%7CDn8qjvN80MwIC8psHLOXy__________PCMN93DUqd4eEo44Ma4FuR-YFMIphmuXIuAQUQsUbHH4%3D; sid_ucp_v1=1.0.0-KDUyZjk5YmU0ZmY0ZDA0NWQ1NWQwMjRkMmIxYzA4NGM2OGI1ZmEyNWEKIQjToPDdu6ziBxC4sKrKBhjvMSAMMKb27skGOAVA-wdIBBoCbHEiIDBlN2YyYThlZjM3Y2QwY2MwODBiY2E2YzFjYjM5N2Ni; ssid_ucp_v1=1.0.0-KDUyZjk5YmU0ZmY0ZDA0NWQ1NWQwMjRkMmIxYzA4NGM2OGI1ZmEyNWEKIQjToPDdu6ziBxC4sKrKBhjvMSAMMKb27skGOAVA-wdIBBoCbHEiIDBlN2YyYThlZjM3Y2QwY2MwODBiY2E2YzFjYjM5N2Ni; __security_mc_1_s_sdk_sign_data_key_web_protect=f6352649-45cc-adb6; login_time=1766496325194; biz_trace_id=fb9041f6; _bd_ticket_crypt_cookie=1188bc8c0188b21e7961573f3fc4496c; IsDouyinActive=false; home_can_add_dy_2_desktop=%220%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSkJ1THFNZmxFYmVqa1hTbGU5bE5DcnpYTHkxcDd3dmRoQ1hFejJERWFLc01Lc3pGdWJ4TkpOa2Q3OHN3M3A5QVkyK3NPVTVGUTlkSHE4cHdCZGtUZ0E9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJKQnVMcU1mbEViZWprWFNsZTlsTkNyelhMeTFwN3d2ZGhDWEV6MkRFYUtzTUtzekZ1YnhOSk5rZDc4c3czcDlBWTIrc09VNUZROWRIcThwd0Jka1RnQT0iLCJ0c19zaWduIjoidHMuMi45ODVkZTNmNGQwZmI1YTEzYWQ3ODhjMDE2NzNkZDc4OTM3NzEzMjllODYyMWQ2MzFmYWZhNzRiNjFiZjQ2MDlmYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJhSlJGT05zVmV0OU1EOXpUK3V3TE1iU1NQUzduS3BTTGdEaG5LRG1sN2kwPSIsInNlY190cyI6IiM1TXhucDduS0VDcDkwWnE1dStjc1h3bDRTKzJVRlY2bEFMQTV0WGxwOTJxZ0xxMFJDQTl3SHNKcnl0QU0ifQ%3D%3D; odin_tt=fda1c2e005adadfa0a508b99b6331817713d8e67b7e3b22b1d5c7a218b3a908db6abdc76a08098afdce9636473efb2d0c8bc41777ae49aef4e8b318c73aa24e3831dde1e1fc01dc1ede654f93945fc3c"

COOKIE_WEB = ""

# ==================== 辅助函数 ====================


def make_request_subscribe(url, cookie):
    """
    发送 HTTP 请求（subscribe 接口专用）

    Args:
        url: 请求的 URL
        cookie: Cookie 字符串

    Returns:
        响应内容（字符串）或错误信息
    """
    headers = {
        # 明确指定只使用 gzip/deflate，避免返回 br 导致解压失败
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'com.ss.android.ugc.aweme.lite/370101 (Linux; U; Android 13; zh_CN; M2012K10C; Build/TP1A.220624.014; Cronet/TTNetVersion:6f1e308d 2025-12-08 QuicVersion:21ac1950 2025-11-18)',
        'x-security-argus': 'BridgeNetworkRequest/unknown aid/2329/xiaomi_2329_64_1104/Android/37.1.0/lynx/-1 https://lf-webcast-gr-sourcecdn.bytegecko.com/obj/byte-gurd-source-gr/webcast/mono/lynx/vip_common_douyin/pages/vip_rank_list/template.js',
        'hybrid-app-engine': 'lynx',
        'activity_now_client': '1766413692074',
        'x-bd-kmsv': '1',
        'bd-ticket-guard-display-os-version': 'TP1A.220624.014',
        'sdk-version': '2',
        'bd-ticket-guard-version': '3',
        'bd-ticket-guard-ree-public-key': 'BNojMBo3PNc3TWOyeYcAHzvmnbxSTJtx1/LGkPGXYKTudq1i7qkaDpFnPWS8tazKMjFCnoOutR8ZB1XTCntiHdA=',
        'bd-ticket-guard-iteration-version': '3',
        'passport-sdk-version': '601431',
        'token-tlb-tag': 'sttt|17|BJRtfCieQoLgFIF0bZEtdf_________Ltsv6uRGTP8v2Xp6GFjxsR8ZRk2kjiVHXYU8pM2OMxAE=',
        'x-vc-bdturing-sdk-version': '4.1.1.cn',
        'x-tt-store-region': 'cn-gz',
        'x-tt-store-region-src': 'uid',
        'x-tt-request-tag': 's=-1;p=0',
        'x-ss-dp': '2329',
        'Cookie': cookie
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30,
            verify=False  # 关闭 SSL 验证
        )
        response.raise_for_status()
        # 若服务器未返回编码，尝试自动检测，默认回退 utf-8
        if not response.encoding:
            response.encoding = response.apparent_encoding or 'utf-8'
        return response.text
    except requests.exceptions.RequestException as e:
        return f'Request Error: {str(e)}'


def make_request_web(url, cookie, useProxies):
    """
    发送 HTTP 请求（Web端接口专用）

    Args:
        url: 请求的 URL
        cookie: Cookie 字符串

    Returns:
        响应内容（字符串）或错误信息
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'uifid': '973a3fd64dcc46a3490fd9b60d4a8e663b34df4ccc4bbcf97643172fb712d8b0af849bef1014ced93a67391f3e94eae8588e1b42ddf55a3e0acc3751436ace3927fc8c79ec49eec532867b9efbb5b62248d0d42a592d66a69ecbbd5bc6d01b3588badf404161dab873d63372c77881fb0dc4687687a5104e127ead6325556c7848b40c01004032a34f26dfad472b9845195d68854193bced0b6331fa306a7904',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.douyin.com/user/MS4wLjABAAAAKE9hcXbTu7QWueiSlhQc4fuU5l48cjFaCYnXtRPV9Fc',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i',
        'Cookie': cookie
    }

    # 隧道域名:端口号
    tunnel = "y686.kdltps.com:15818"

    # 用户名密码方式
    username = "t16668608982735"
    password = "fiq6dowg"
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
    }

    try:
        # print('proxies',proxies)
        # 判断是否使用代理
        if useProxies:
            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                verify=False,  # 关闭 SSL 验证
                proxies=proxies
            )
        else:
            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                verify=False,  # 关闭 SSL 验证
            )
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f'Request Error: {str(e)}'


def get_userid(url):
    """
    从抖音分享链接中提取用户ID（优先获取sec_uid，不存在则获取user/后的ID）

    Args:
        url: 抖音分享链接

    Returns:
        用户ID，如果提取失败则返回None
    """
    if not url:
        return None

    # 1. 首先尝试从URL参数中获取sec_uid
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    if 'sec_uid' in query_params:
        return query_params['sec_uid'][0]

    # 2. 如果sec_uid不存在，则尝试从路径中提取user/后的内容
    path = parsed_url.path
    if 'user/' in path:
        parts = path.split('user/')
        if len(parts) > 1:
            user_part = parts[1].split('?')[0]  # 去除可能存在的后续参数
            return user_part

    # 3. 如果以上方式都失败，返回None
    return None


def douyin_get_redirect_url(url):
    """
    获取抖音接口重定向后的链接

    Args:
        url: 需要重定向的URL

    Returns:
        重定向后的最终URL
    """
    try:
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=30,
            verify=False
        )
        return response.url
    except requests.exceptions.RequestException:
        return url


def http_request(url, data, headers=None):
    """
    发起HTTP POST请求

    Args:
        url: 请求URL
        data: POST数据
        headers: HTTP头

    Returns:
        响应内容（字符串）
    """
    if headers is None:
        headers = {}

    try:
        response = requests.post(
            url,
            data=data,
            headers=headers,
            timeout=30,
            verify=False  # 关闭 SSL 验证
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f'Request Error: {str(e)}'


# ==================== 接口路由 ====================

@app.route('/subscribe', methods=['GET', 'POST', 'OPTIONS'])
def subscribe():
    """
    订阅排行榜查询接口

    参数说明：
    author_id: 抖音用户ID
    rank_type: 排行类型 1:本周榜 2:上周榜 3:今年榜
    """
    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        return '', 200

    # 获取请求参数
    author_id = request.args.get('author_id', '').strip()
    rank_type = request.args.get('rank_type', '1').strip()  # 1:本周榜 2:上周榜 3:今年榜
    # 获取 Cookie 参数，如果提供则使用，否则使用默认值
    cookie_subscribe = request.args.get(
        'cookie_subscribe', '').strip() or COOKIE_SUBSCRIBE

    # 构建请求 URL
    url = f'https://webcast26-normal-c-lq.amemv.com/webcast/subscribe/get_contribute_ranklist/?offset=0&count=20&rank_kind=2&author_id={author_id}&rank_type={rank_type}&live_request_from_jsb=1&webcast_sdk_version=4120&live_sdk_version=370101&gamecp_sdk_version=4120&webcast_language=zh&webcast_locale=zh_CN&webcast_gps_access=1&current_network_quality_info=%7B%22http_rtt%22%3A220%2C%22tcp_rtt%22%3A22%2C%22quic_rtt%22%3A22%2C%22downstream_throughput_kbps%22%3A51574%2C%22net_effective_connection_type%22%3A4%2C%22video_download_speed%22%3A8671%2C%22quic_receive_loss_rate%22%3A-1%2C%22quic_send_loss_rate%22%3A-1%7D&device_score=8.6459&address_book_access=2&user_id=4229184618762131&is_pad=false&is_android_pad=0&is_landscape=false&carrier_region=CN&sec_user_id=MS4wLjABAAAAVD5P6sSrk63XzjJT2n_3SQTzfg6xeHZEtY8q-gOoRaIdWQe1GVc14zkfspecr6YY&sec_author_id=MS4wLjABAAAAQRDbTKq61_DJ9hERWfudv8om5slFVfduB286CRdcnUg&klink_egdi=AAJyNSLZjdt16GBbCmj2905_two1IjVuFtSExcGXQT7r8NFKy0zS1ytB&iid=326986953398496&device_id=4135726972408180&ac=wifi&channel=xiaomi_2329_64_1104&aid=2329&app_name=douyin_lite&version_code=370100&version_name=37.1.0&device_platform=android&os=android&ssmix=a&device_type=M2012K10C&device_brand=Redmi&language=zh&os_api=33&os_version=13&manifest_version_code=370101&resolution=1080*2272&dpi=440&update_version_code=37109900&_rticket=1766413689931&package=com.ss.android.ugc.aweme.lite&gold_container=0&first_launch_timestamp=1757849569&last_deeplink_update_version_code=0&cpu_support64=true&host_abi=arm64-v8a&is_guest_mode=0&app_type=normal&minor_status=0&appTheme=light&is_preinstall=0&need_personal_recommend=1&is_android_fold=0&ts=1766413690&cdid=a4069695-e8a5-4cc8-aa4d-8c2350dc0b7d&md=0'

    # 发送请求
    response_text = make_request_subscribe(url, cookie_subscribe)

    try:
        # 解析 JSON 响应
        response_data = json.loads(response_text)

        # 返回 data 字段的内容
        if 'data' in response_data:
            return jsonify(response_data['data']), 200, {
                'Content-Type': 'application/json; charset=utf-8'
            }
        else:
            return jsonify(response_data), 200, {
                'Content-Type': 'application/json; charset=utf-8'
            }
    except json.JSONDecodeError:
        # 如果响应不是有效的 JSON，直接返回原始响应
        return response_text, 200, {
            'Content-Type': 'application/json; charset=utf-8'
        }


@app.route('/qrcode_url', methods=['GET', 'POST', 'OPTIONS'])
def qrcode_url():
    """
    用户信息查询接口（通过sec_user_id）

    参数说明：
    sec_user_id: 抖音用户sec_user_id
    """
    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        return '', 200

    # 获取请求参数
    sec_user_id = request.args.get('sec_user_id', '').strip()
    # 获取 Cookie 参数，如果提供则使用，否则使用默认值
    cookie_web = request.args.get('cookie_web', '').strip() or COOKIE_WEB

    # 构建请求 URL
    url = f'https://www.douyin.com/aweme/v1/web/user/profile/other/?device_platform=webapp&aid=6383&channel=channel_pc_web&publish_video_strategy_type=2&source=channel_pc_web&sec_user_id={sec_user_id}&personal_center_strategy=1&profile_other_record_enable=1&land_to=1&update_version_code=170400&pc_client_type=1&pc_libra_divert=Windows&support_h265=1&support_dash=1&cpu_core_num=12&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1536&screen_height=864&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=143.0.0.0&browser_online=true&engine_name=Blink&engine_version=143.0.0.0&os_name=Windows&os_version=10&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=150&webid=7498378399590024719'

    # 发送请求
    response_text = make_request_web(url, cookie_web, True)

    try:
        # 解析 JSON 响应
        response_data = json.loads(response_text)

        # 返回整个响应（与 PHP 版本一致）
        return jsonify(response_data), 200, {
            'Content-Type': 'application/json; charset=utf-8'
        }
    except json.JSONDecodeError:
        # 如果响应不是有效的 JSON，直接返回原始响应
        return response_text, 200, {
            'Content-Type': 'application/json; charset=utf-8'
        }


@app.route('/userinfo', methods=['GET', 'POST', 'OPTIONS'])
def userinfo():
    """
    用户信息查询接口（通过URL或ID）

    参数说明：
    id: 抖音用户sec_user_id
    url: 抖音用户主页链接
    """
    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        return '', 200

    # 获取请求参数（优先使用url，其次使用id）
    url_param = request.args.get('url', '') or request.args.get('id', '')
    url_param = urllib.parse.unquote(url_param).strip()
    # 获取 Cookie 参数，如果提供则使用，否则使用默认值
    cookie_web = request.args.get('cookie_web', '').strip() or COOKIE_WEB

    if not url_param:
        return jsonify({
            "code": 400,
            "msg": "参数错误，请提供url或id参数"
        }), 400

    # 使用正则匹配URL
    url_match = re.search(r'(https?://[^\s]+)', url_param)
    if url_match:
        url = url_match.group(1)
    else:
        url = url_param

    # 根据URL类型提取sec_user_id
    sec_user_id = None
    if 'www.douyin.com' in url:
        # 提取函数获取用户id
        sec_user_id = get_userid(url)
    elif 'v.douyin.com' in url:
        # 先重定向后再获取用户id
        redirect_url = douyin_get_redirect_url(url)
        # 提取函数获取用户id
        sec_user_id = get_userid(redirect_url)
    else:
        # 其他情况处理（可能是直接的sec_user_id）
        sec_user_id = url_param

    if not sec_user_id:
        return jsonify({
            "code": 400,
            "msg": "无法从URL中提取用户ID"
        }), 400

    # 发送POST请求获取用户信息
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://www.douyin.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": f"https://www.douyin.com/user/{sec_user_id}?showTab=like",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": cookie_web,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "x-secsdk-csrf-token": "DOWNGRADE"
    }

    post_data = f'sec_user_ids=["{sec_user_id}"]'

    response_text = http_request(
        "https://www.douyin.com/aweme/v1/web/im/user/info/",
        post_data,
        headers
    )

    try:
        # 解析JSON响应
        response_data = json.loads(response_text)

        # 检查响应数据
        if 'data' not in response_data or not response_data['data'] or len(response_data['data']) == 0:
            return jsonify({
                "code": 404,
                "msg": "未找到用户信息"
            }), 404

        item = response_data['data'][0]

        # 返回格式化的数据
        return jsonify({
            "code": 200,
            "msg": "解析成功",
            "sec_uid": sec_user_id,
            "data": {
                'id': sec_user_id,
                'nickname': item.get('nickname', ''),
                'enterprise_verify_reason': item.get('enterprise_verify_reason', ''),
                'author_id': item.get('uid', ''),
                'unique_id': item.get('unique_id', ''),
                'avatar': item.get('avatar_thumb', {}).get('url_list', [''])[0] if item.get('avatar_thumb') else '',
                'avatar_small': item.get('avatar_small', {}).get('url_list', [''])[0] if item.get('avatar_small') else '',
                'short_id': item.get('short_id', ''),
                'signature': item.get('signature', ''),
            }
        }), 200, {
            'Content-Type': 'application/json; charset=utf-8'
        }
    except json.JSONDecodeError:
        return jsonify({
            "code": 500,
            "msg": "响应解析失败",
            "raw_response": response_text
        }), 500
    except (KeyError, IndexError) as e:
        return jsonify({
            "code": 500,
            "msg": f"数据解析错误: {str(e)}",
            "raw_response": response_text
        }), 500


if __name__ == '__main__':
    # 禁用 SSL 警告（因为关闭了 SSL 验证）
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # 运行 Flask 应用
    print("=" * 60)
    print("服务已启动")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=False)
