#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DY周榜 GUI 客户端

功能：
- 输入DY主页链接（支持多行，一行一个）
- 逐条调用 douyin_api 的 /userinfo 接口，提取 author_id
- 用 author_id 调用 /subscribe 获取 rank_list
- 遍历 rank_list，提取 sec_uid 调用 /qrcode_url
- 将结果在界面日志中逐步输出

依赖：
- requests
- ttkbootstrap（litera 主题）

运行：
python gui_app.py
"""

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from tkinter import messagebox
from tkinter import PhotoImage
import requests
import base64
import os
import re
import random
import uuid
from pathlib import Path
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
from urllib.parse import quote, urlparse, parse_qs
import urllib.parse
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib3
from PJYSDK import *

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API 基址（写死）
API_BASE = "http://localhost:5000"
MAX_WORKERS_DEFAULT = 5  # 并发处理链接数量

# 配置文件路径
CONFIG_FILE = "gui_config.json"

# ==================== Flask API 服务 ====================

# 创建 Flask 应用
flask_app = Flask(__name__)
CORS(flask_app)  # 允许所有来源的跨域请求

# Cookie 配置（默认值，实际使用时会从 GUI 传入）
COOKIE_SUBSCRIBE = ""
COOKIE_WEB = ""

IS_ACCESS = False

# 初始化 app_key 和 app_secret 在开发者后台新建软件获取
pjysdk = PJYSDK(app_key='d57buh3dqusrp4bkn3hg',
                app_secret='8t5R7Bk7wGe1sRnJLhtgPFn9u7PWWj13')
pjysdk.debug = False

# 心跳失败回调


def on_heartbeat_failed(hret):
    print(hret.message)
    if hret.code == 10214:
        os._exit(1)  # 退出脚本
    print("心跳失败，尝试重登...")
    login_ret = pjysdk.card_login()
    if login_ret.code == 0:
        print("重登成功")
    else:
        print(login_ret.message)  # 重登失败
        os._exit(1)  # 退出脚本



def make_request_subscribe(url, cookie):
    """发送 HTTP 请求（subscribe 接口专用）"""
    headers = {
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
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        if not response.encoding:
            response.encoding = response.apparent_encoding or 'utf-8'
        return response.text
    except requests.exceptions.RequestException as e:
        return f'Request Error: {str(e)}'


def make_request_web(url, cookie, useProxies):
    """发送 HTTP 请求（Web端接口专用）"""
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
    tunnel = "e673.kdltps.com:15818"
    username = "t16682184900584"
    password = "vnd14jep"
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
    }
    try:
        if useProxies:
            response = requests.get(url, headers=headers, timeout=30, verify=False, proxies=proxies)
        else:
            response = requests.get(url, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f'Request Error: {str(e)}'


def get_userid(url):
    """从抖音分享链接中提取用户ID"""
    if not url:
        return None
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    if 'sec_uid' in query_params:
        return query_params['sec_uid'][0]
    path = parsed_url.path
    if 'user/' in path:
        parts = path.split('user/')
        if len(parts) > 1:
            user_part = parts[1].split('?')[0]
            return user_part
    return None


def douyin_get_redirect_url(url):
    """获取抖音接口重定向后的链接"""
    try:
        response = requests.get(url, allow_redirects=True, timeout=30, verify=False)
        return response.url
    except requests.exceptions.RequestException:
        return url


def http_request(url, data, headers=None):
    """发起HTTP POST请求"""
    if headers is None:
        headers = {}
    try:
        response = requests.post(url, data=data, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f'Request Error: {str(e)}'


@flask_app.route('/subscribe', methods=['GET', 'POST', 'OPTIONS'])
def subscribe():
    """订阅排行榜查询接口"""
    if request.method == 'OPTIONS':
        return '', 200
    author_id = request.args.get('author_id', '').strip()
    rank_type = request.args.get('rank_type', '1').strip()
    cookie_subscribe = request.args.get('cookie_subscribe', '').strip() or COOKIE_SUBSCRIBE
    url = f'https://webcast26-normal-c-lq.amemv.com/webcast/subscribe/get_contribute_ranklist/?offset=0&count=20&rank_kind=2&author_id={author_id}&rank_type={rank_type}&live_request_from_jsb=1&webcast_sdk_version=4120&live_sdk_version=370101&gamecp_sdk_version=4120&webcast_language=zh&webcast_locale=zh_CN&webcast_gps_access=1&current_network_quality_info=%7B%22http_rtt%22%3A220%2C%22tcp_rtt%22%3A22%2C%22quic_rtt%22%3A22%2C%22downstream_throughput_kbps%22%3A51574%2C%22net_effective_connection_type%22%3A4%2C%22video_download_speed%22%3A8671%2C%22quic_receive_loss_rate%22%3A-1%2C%22quic_send_loss_rate%22%3A-1%7D&device_score=8.6459&address_book_access=2&user_id=4229184618762131&is_pad=false&is_android_pad=0&is_landscape=false&carrier_region=CN&sec_user_id=MS4wLjABAAAAVD5P6sSrk63XzjJT2n_3SQTzfg6xeHZEtY8q-gOoRaIdWQe1GVc14zkfspecr6YY&sec_author_id=MS4wLjABAAAAQRDbTKq61_DJ9hERWfudv8om5slFVfduB286CRdcnUg&klink_egdi=AAJyNSLZjdt16GBbCmj2905_two1IjVuFtSExcGXQT7r8NFKy0zS1ytB&iid=326986953398496&device_id=4135726972408180&ac=wifi&channel=xiaomi_2329_64_1104&aid=2329&app_name=douyin_lite&version_code=370100&version_name=37.1.0&device_platform=android&os=android&ssmix=a&device_type=M2012K10C&device_brand=Redmi&language=zh&os_api=33&os_version=13&manifest_version_code=370101&resolution=1080*2272&dpi=440&update_version_code=37109900&_rticket=1766413689931&package=com.ss.android.ugc.aweme.lite&gold_container=0&first_launch_timestamp=1757849569&last_deeplink_update_version_code=0&cpu_support64=true&host_abi=arm64-v8a&is_guest_mode=0&app_type=normal&minor_status=0&appTheme=light&is_preinstall=0&need_personal_recommend=1&is_android_fold=0&ts=1766413690&cdid=a4069695-e8a5-4cc8-aa4d-8c2350dc0b7d&md=0'
    response_text = make_request_subscribe(url, cookie_subscribe)
    try:
        response_data = json.loads(response_text)
        if 'data' in response_data:
            return jsonify(response_data['data']), 200, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            return jsonify(response_data), 200, {'Content-Type': 'application/json; charset=utf-8'}
    except json.JSONDecodeError:
        return response_text, 200, {'Content-Type': 'application/json; charset=utf-8'}


@flask_app.route('/qrcode_url', methods=['GET', 'POST', 'OPTIONS'])
def qrcode_url():
    """用户信息查询接口（通过sec_user_id）"""
    if request.method == 'OPTIONS':
        return '', 200
    sec_user_id = request.args.get('sec_user_id', '').strip()
    cookie_web = request.args.get('cookie_web', '').strip() or COOKIE_WEB
    url = f'https://www.douyin.com/aweme/v1/web/user/profile/other/?device_platform=webapp&aid=6383&channel=channel_pc_web&publish_video_strategy_type=2&source=channel_pc_web&sec_user_id={sec_user_id}&personal_center_strategy=1&profile_other_record_enable=1&land_to=1&update_version_code=170400&pc_client_type=1&pc_libra_divert=Windows&support_h265=1&support_dash=1&cpu_core_num=12&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1536&screen_height=864&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=143.0.0.0&browser_online=true&engine_name=Blink&engine_version=143.0.0.0&os_name=Windows&os_version=10&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=150&webid=7498378399590024719'
    response_text = make_request_web(url, cookie_web, True)
    try:
        response_data = json.loads(response_text)
        return jsonify(response_data), 200, {'Content-Type': 'application/json; charset=utf-8'}
    except json.JSONDecodeError:
        return response_text, 200, {'Content-Type': 'application/json; charset=utf-8'}


@flask_app.route('/userinfo', methods=['GET', 'POST', 'OPTIONS'])
def userinfo():
    """用户信息查询接口（通过URL或ID）"""
    if request.method == 'OPTIONS':
        return '', 200
    url_param = request.args.get('url', '') or request.args.get('id', '')
    url_param = urllib.parse.unquote(url_param).strip()
    cookie_web = request.args.get('cookie_web', '').strip() or COOKIE_WEB
    if not url_param:
        return jsonify({"code": 400, "msg": "参数错误，请提供url或id参数"}), 400
    url_match = re.search(r'(https?://[^\s]+)', url_param)
    if url_match:
        url = url_match.group(1)
    else:
        url = url_param
    sec_user_id = None
    if 'www.douyin.com' in url:
        sec_user_id = get_userid(url)
    elif 'v.douyin.com' in url:
        redirect_url = douyin_get_redirect_url(url)
        sec_user_id = get_userid(redirect_url)
    else:
        sec_user_id = url_param
    if not sec_user_id:
        return jsonify({"code": 400, "msg": "无法从URL中提取用户ID"}), 400
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
    response_text = http_request("https://www.douyin.com/aweme/v1/web/im/user/info/", post_data, headers)
    try:
        response_data = json.loads(response_text)
        if 'data' not in response_data or not response_data['data'] or len(response_data['data']) == 0:
            return jsonify({"code": 404, "msg": "未找到用户信息"}), 404
        item = response_data['data'][0]
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
        }), 200, {'Content-Type': 'application/json; charset=utf-8'}
    except json.JSONDecodeError:
        return jsonify({"code": 500, "msg": "响应解析失败", "raw_response": response_text}), 500
    except (KeyError, IndexError) as e:
        return jsonify({"code": 500, "msg": f"数据解析错误: {str(e)}", "raw_response": response_text}), 500


def start_flask_server():
    """在后台线程中启动 Flask 服务器"""
    flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ==================== GUI 应用 ====================


class DouyinGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("DY周榜【作者tg：maotai8866】")
        # 设置窗口图标
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")
            if os.path.exists(icon_path):
                self.master.iconbitmap(icon_path)
        except Exception as e:
            print(f"设置图标失败: {e}")
        self.style = ttk.Style("litera")
        self.rank_type = ttk.StringVar(value="1")  # 1:本周榜 2:上周榜 3:今年榜
        self.max_workers = ttk.IntVar(value=MAX_WORKERS_DEFAULT)
        self.cookie_input1 = ttk.StringVar(value="")  # Cookie 1
        self.cookie_input2 = ttk.StringVar(value="")  # Cookie 2
        self.cookie_input3 = ttk.StringVar(value="")  # Cookie 3
        self.cookie_input4 = ttk.StringVar(value="")  # Cookie 4
        self.auth_code = ttk.StringVar(value="")  # 授权码
        self.poll_interval = ttk.IntVar(value=60)  # 轮询间隔时间（秒），默认60秒
        self.is_polling = False  # 轮询状态标志
        self.poll_thread = None  # 轮询线程
        self.url_to_author_id = {}  # URL 到 author_id 的映射缓存
        self.processed_sec_uids = set()  # 已处理过的 sec_uid 集合
        self.is_running_task = False  # 任务运行状态标志
        self.user_list_data = []  # 用户列表数据，格式: [{"序号": 1, "用户昵称": "...", "所属博主": "...", "获取时间": "..."}, ...]
        self.user_list_counter = 0  # 用户列表序号计数器
        self.master.geometry("1600x1000")
        
        # 代理请求频率限制（每秒最多5次）
        self.proxy_request_lock = threading.Lock()
        self.proxy_request_times = []  # 记录最近请求的时间戳

        # 启动 Flask 服务器（后台线程）
        flask_thread = threading.Thread(target=start_flask_server, daemon=True)
        flask_thread.start()
        time.sleep(1)  # 等待服务器启动

        # 加载保存的配置
        self.load_config()

        self._build_ui()

        # 绑定窗口关闭事件，保存配置
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _build_ui(self):
        # 顶部配置区域
        frm_top = ttk.Frame(self.master, padding=10)
        frm_top.pack(fill=X)

        ttk.Label(frm_top, text="并发数:").grid(
            row=0, column=0, sticky=W, padx=(0, 5))
        ttk.Spinbox(
            frm_top,
            from_=1,
            to=20,
            textvariable=self.max_workers,
            width=5,
        ).grid(row=0, column=1, sticky=W)

        # 保存目录配置
        ttk.Label(frm_top, text="二维码保存目录:").grid(
            row=0, column=2, sticky=W, padx=(10, 5))
        self.save_dir = ttk.StringVar(value="qrcodes")  # 默认保存目录
        ttk.Entry(frm_top, textvariable=self.save_dir, width=30).grid(
            row=0, column=3, sticky=W
        )
        
        # 授权码配置
        ttk.Label(frm_top, text="授权码:").grid(
            row=0, column=4, sticky=W, padx=(10, 5))
        entry_auth_code = ttk.Entry(frm_top, textvariable=self.auth_code, width=30)
        entry_auth_code.grid(row=0, column=5, sticky=W)
        # 绑定文本变化事件，自动保存
        entry_auth_code.bind('<KeyRelease>', lambda e: self.save_config())

        # Cookie 配置区域
        frm_cookie = ttk.Labelframe(
            self.master, text="Cookie 配置（每行一个，随机选择）", padding=10)
        frm_cookie.pack(fill=X, padx=10, pady=5)

        # Cookie 1
        ttk.Label(frm_cookie, text="Cookie 1:").grid(
            row=0, column=0, sticky=W+N, padx=(0, 5))
        txt_cookie1 = ttk.Text(frm_cookie, height=3, wrap="none", width=45)  # 禁用自动换行，减少重绘计算
        txt_cookie1.grid(row=0, column=1, sticky=W+E, padx=(0, 10))
        
        # Cookie 2
        ttk.Label(frm_cookie, text="Cookie 2:").grid(
            row=0, column=2, sticky=W+N, padx=(0, 5))
        txt_cookie2 = ttk.Text(frm_cookie, height=3, wrap="none", width=45)  # 禁用自动换行，减少重绘计算
        txt_cookie2.grid(row=0, column=3, sticky=W+E, padx=(0, 10))
        
        # Cookie 3
        ttk.Label(frm_cookie, text="Cookie 3:").grid(
            row=0, column=4, sticky=W+N, padx=(0, 5))
        txt_cookie3 = ttk.Text(frm_cookie, height=3, wrap="none", width=45)  # 禁用自动换行，减少重绘计算
        txt_cookie3.grid(row=0, column=5, sticky=W+E, padx=(0, 10))
        
        # Cookie 4
        ttk.Label(frm_cookie, text="Cookie 4:").grid(
            row=0, column=6, sticky=W+N, padx=(0, 5))
        txt_cookie4 = ttk.Text(frm_cookie, height=3, wrap="none", width=45)  # 禁用自动换行，减少重绘计算
        txt_cookie4.grid(row=0, column=7, sticky=W+E, padx=(0, 10))
        
        # 优化：设置固定列宽比例，减少重绘计算
        # 使用 uniform 参数让列均匀分配，减少重绘时的计算量
        frm_cookie.columnconfigure(1, weight=1, uniform="cookie_col")
        frm_cookie.columnconfigure(3, weight=1, uniform="cookie_col")
        frm_cookie.columnconfigure(5, weight=1, uniform="cookie_col")
        frm_cookie.columnconfigure(7, weight=1, uniform="cookie_col")

        # 绑定文本变化事件，自动保存
        def on_cookie1_change(event=None):
            self.cookie_input1.set(txt_cookie1.get("1.0", END).strip())
            self.save_config()
        def on_cookie2_change(event=None):
            self.cookie_input2.set(txt_cookie2.get("1.0", END).strip())
            self.save_config()
        def on_cookie3_change(event=None):
            self.cookie_input3.set(txt_cookie3.get("1.0", END).strip())
            self.save_config()
        def on_cookie4_change(event=None):
            self.cookie_input4.set(txt_cookie4.get("1.0", END).strip())
            self.save_config()
        
        txt_cookie1.bind('<KeyRelease>', on_cookie1_change)
        txt_cookie2.bind('<KeyRelease>', on_cookie2_change)
        txt_cookie3.bind('<KeyRelease>', on_cookie3_change)
        txt_cookie4.bind('<KeyRelease>', on_cookie4_change)
        
        self.txt_cookie1 = txt_cookie1
        self.txt_cookie2 = txt_cookie2
        self.txt_cookie3 = txt_cookie3
        self.txt_cookie4 = txt_cookie4

        # 输入区域
        frm_input = ttk.Labelframe(
            self.master, text="DY主页链接（每行一个）", padding=10)
        frm_input.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # 创建滚动条
        scrollbar_urls = ttk.Scrollbar(frm_input)
        scrollbar_urls.pack(side=RIGHT, fill=Y)

        self.txt_urls = ttk.Text(
            frm_input, height=10, wrap="none", yscrollcommand=scrollbar_urls.set)  # 禁用自动换行，减少重绘计算
        self.txt_urls.pack(side=LEFT, fill=BOTH, expand=True)

        # 关联滚动条和文本框
        scrollbar_urls.config(command=self.txt_urls.yview)

        # 绑定输入框变化事件，自动保存配置
        def on_urls_change(event=None):
            self.save_config()
        self.txt_urls.bind('<KeyRelease>', on_urls_change)

        # 控制按钮
        frm_btn = ttk.Frame(self.master, padding=10)
        frm_btn.pack(fill=X)

        ttk.Button(frm_btn, text="开始运行", bootstyle=SUCCESS, command=self.start_task, padding=(15, 8)).pack(
            side=LEFT
        )
        ttk.Button(frm_btn, text="清空日志", bootstyle=SECONDARY, command=self.clear_log, padding=(15, 8)).pack(
            side=LEFT, padx=(10, 0)
        )

        # 轮询控制区域
        frm_poll = ttk.Frame(frm_btn)
        frm_poll.pack(side=LEFT, padx=(20, 0))

        ttk.Label(frm_poll, text="轮询间隔(秒):").pack(side=LEFT, padx=(0, 5))
        ttk.Spinbox(
            frm_poll,
            from_=10,
            to=3600,
            textvariable=self.poll_interval,
            width=8,
        ).pack(side=LEFT, padx=(0, 10))

        self.btn_start_poll = ttk.Button(
            frm_poll, text="开始监听", bootstyle=INFO, command=self.start_polling, padding=(15, 8)
        )
        self.btn_start_poll.pack(side=LEFT, padx=(0, 5))

        self.btn_stop_poll = ttk.Button(
            frm_poll, text="停止监听", bootstyle=DANGER, command=self.stop_polling, state=DISABLED, padding=(15, 8)
        )
        self.btn_stop_poll.pack(side=LEFT, padx=(0, 20))
        
        # 退出按钮
        ttk.Button(
            frm_btn, text="退出", bootstyle=DANGER, command=self.quit_application, padding=(15, 8)
        ).pack(side=RIGHT, padx=(10, 0))

        # 创建左右分栏容器
        frm_content = ttk.Frame(self.master)
        frm_content.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        # 左侧：用户列表
        frm_user_list = ttk.Labelframe(frm_content, text="用户列表", padding=10)
        frm_user_list.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))

        # 用户列表表格
        columns = ("序号", "用户昵称", "所属博主", "获取时间")
        self.tree_user_list = ttk.Treeview(frm_user_list, columns=columns, show="headings", height=15)
        
        # 设置列标题和宽度
        self.tree_user_list.heading("序号", text="序号")
        self.tree_user_list.heading("用户昵称", text="用户昵称")
        self.tree_user_list.heading("所属博主", text="所属博主")
        self.tree_user_list.heading("获取时间", text="获取时间")
        
        self.tree_user_list.column("序号", width=80, anchor="center")
        self.tree_user_list.column("用户昵称", width=200, anchor="w")
        self.tree_user_list.column("所属博主", width=200, anchor="w")
        self.tree_user_list.column("获取时间", width=180, anchor="center")

        # 用户列表滚动条
        scrollbar_user_list = ttk.Scrollbar(frm_user_list, orient=VERTICAL, command=self.tree_user_list.yview)
        self.tree_user_list.configure(yscrollcommand=scrollbar_user_list.set)
        
        self.tree_user_list.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar_user_list.pack(side=RIGHT, fill=Y)
        
        # 绑定双击事件
        self.tree_user_list.bind("<Double-1>", self._on_user_double_click)

        # 右侧：日志输出
        frm_log = ttk.Labelframe(frm_content, text="日志", padding=10)
        frm_log.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))

        # 创建滚动条
        scrollbar_log = ttk.Scrollbar(frm_log)
        scrollbar_log.pack(side=RIGHT, fill=Y)

        # 限制日志最大行数，避免窗口缩放时卡顿
        self.max_log_lines = 3000  # 最大保留5000行日志
        
        self.txt_log = ttk.Text(
            frm_log, height=20, wrap="none", yscrollcommand=scrollbar_log.set)  # 禁用自动换行，减少重绘计算
        self.txt_log.pack(side=LEFT, fill=BOTH, expand=True)

        # 关联滚动条和文本框
        scrollbar_log.config(command=self.txt_log.yview)

        # 回填保存的配置数据
        if hasattr(self, '_saved_urls') and self._saved_urls:
            self.txt_urls.insert("1.0", self._saved_urls)
        if hasattr(self, '_saved_save_dir'):
            self.save_dir.set(self._saved_save_dir)
        # Cookie 已经在 load_config 中设置了
        if self.cookie_input1.get():
            self.txt_cookie1.insert("1.0", self.cookie_input1.get())
        if self.cookie_input2.get():
            self.txt_cookie2.insert("1.0", self.cookie_input2.get())
        if self.cookie_input3.get():
            self.txt_cookie3.insert("1.0", self.cookie_input3.get())
        if self.cookie_input4.get():
            self.txt_cookie4.insert("1.0", self.cookie_input4.get())
        
        # 初始化用户列表显示（在UI创建完成后）
        self.master.update_idletasks()  # 确保UI完全创建
        self._refresh_user_list()
    
    def _get_qrcode_path(self, nickname: str, author_nickname: str, rank: int = 0) -> Path:
        """根据用户信息获取二维码文件路径"""
        base_dir = Path(self.save_dir.get().strip() or "qrcodes")
        author_dir = base_dir / self.clean_filename(author_nickname)
        clean_nickname = self.clean_filename(nickname)
        # 统一使用 rank_nickname 格式，即使rank为0也加上前缀（与save_qrcode保持一致）
        filename = f"{rank}_{clean_nickname}"
        return author_dir / f"{filename}.png"
    
    def _find_qrcode_file(self, nickname: str, author_nickname: str, rank: int = 0) -> Path:
        """查找二维码文件（从实际文件名中匹配，不依赖rank参数）"""
        base_dir = Path(self.save_dir.get().strip() or "qrcodes")
        author_dir = base_dir / self.clean_filename(author_nickname)
        clean_nickname = self.clean_filename(nickname)
        
        # 如果目录不存在，返回默认路径
        if not author_dir.exists():
            return author_dir / f"{rank}_{clean_nickname}.png"
        
        # 扫描目录中所有匹配的文件
        # 匹配模式：{任意数字}_{clean_nickname}.png 或 {clean_nickname}.png
        import re
        pattern = re.compile(rf"^(\d+_){re.escape(clean_nickname)}\.png$|^{re.escape(clean_nickname)}\.png$")
        
        matched_files = []
        for png_file in author_dir.glob("*.png"):
            if pattern.match(png_file.name):
                matched_files.append(png_file)
        
        # 如果找到匹配的文件，优先返回与rank匹配的，否则返回第一个
        if matched_files:
            # 优先返回与rank匹配的文件
            for png_file in matched_files:
                # 从文件名中提取rank
                match = re.match(rf"^(\d+_){re.escape(clean_nickname)}\.png$", png_file.name)
                if match:
                    file_rank = int(match.group(1).rstrip('_'))
                    if file_rank == rank:
                        return png_file
            # 如果没有找到匹配的rank，返回第一个匹配的文件
            return matched_files[0]
        
        # 如果没找到匹配的文件，尝试标准格式
        possible_paths = [
            author_dir / f"{rank}_{clean_nickname}.png",  # rank_nickname格式
            author_dir / f"{clean_nickname}.png",  # 只有nickname格式
        ]
        
        # 返回第一个存在的文件路径
        for path in possible_paths:
            if path.exists():
                return path
        
        # 如果都不存在，返回默认路径（用于显示错误信息）
        return possible_paths[0]
    
    def _on_user_double_click(self, event):
        """双击用户列表项时打开二维码查看窗口"""
        selection = self.tree_user_list.selection()
        if not selection:
            return
        
        item = self.tree_user_list.item(selection[0])
        values = item['values']
        if len(values) < 3:
            return
        
        # 获取用户信息
        seq = values[0]
        nickname = values[1]
        author_nickname = values[2]
        
        # 从数据中找到对应的rank
        rank = 0
        for user_item in self.user_list_data:
            if user_item.get('序号') == seq:
                rank = user_item.get('排名', 0)
                break
        
        # 打开查看窗口
        self._show_qrcode_window(nickname, author_nickname, rank, seq)
    
    def _show_qrcode_window(self, nickname: str, author_nickname: str, rank: int, current_seq: int):
        """显示二维码查看窗口"""
        # 创建新窗口（缩小窗口尺寸，但二维码会更大）
        qr_window = ttk.Toplevel(self.master)
        qr_window.title(f"二维码查看 - {nickname}")
        qr_window.geometry("700x880")
        
        # 获取当前二维码路径（尝试查找文件）
        current_path = self._find_qrcode_file(nickname, author_nickname, rank)
        
        # 获取所有用户列表数据，用于切换
        sorted_data = sorted(self.user_list_data, key=lambda x: x.get('序号', 0))
        current_index = -1
        for idx, item in enumerate(sorted_data):
            if item.get('序号') == current_seq:
                current_index = idx
                break
        
        # 图片显示区域（最小padding，让二维码占据更多空间）
        frm_image = ttk.Frame(qr_window, padding=2)
        frm_image.pack(fill=BOTH, expand=True)
        
        # 信息显示（放在顶部，最小padding，使用更小的字体，一行两条）
        info_label = ttk.Label(
            frm_image, 
            text=f"用户: {nickname}    博主: {author_nickname}\n排名: {rank if rank else '无'}    序号: {current_seq}",
            font=("微软雅黑", 14),
            justify="left"
        )
        info_label.pack(pady=(0, 2))
        
        # 图片标签（居中显示，占据主要空间）
        img_label = ttk.Label(frm_image, text="加载中...", anchor="center")
        img_label.pack(expand=True, fill=BOTH)
        
        # 控制按钮区域（增加padding确保按钮完整显示）
        frm_controls = ttk.Frame(qr_window, padding=8)
        frm_controls.pack(fill=X, side=BOTTOM)
        
        def load_image(index: int):
            """加载指定索引的二维码图片"""
            nonlocal current_index, current_path, nickname, author_nickname, rank
            
            if index < 0 or index >= len(sorted_data):
                return
            
            current_index = index
            item_data = sorted_data[current_index]
            nickname = item_data.get('用户昵称', '')
            author_nickname = item_data.get('所属博主', '')
            rank = item_data.get('排名', 0)
            seq = item_data.get('序号', 0)
            
            # 更新窗口标题
            qr_window.title(f"二维码查看 - {nickname} ({current_index + 1}/{len(sorted_data)})")
            
            # 获取文件路径（尝试查找文件）
            current_path = self._find_qrcode_file(nickname, author_nickname, rank)
            
            # 从实际文件名中提取rank（如果文件存在）
            actual_rank = rank
            if current_path.exists():
                import re
                clean_nickname = self.clean_filename(nickname)
                match = re.match(rf"^(\d+_){re.escape(clean_nickname)}\.png$", current_path.name)
                if match:
                    actual_rank = int(match.group(1).rstrip('_'))
            
            # 更新信息显示（使用实际的rank，一行两条）
            info_label.config(
                text=f"用户: {nickname}    博主: {author_nickname}\n排名: {actual_rank if actual_rank else '无'}    序号: {seq}"
            )
            
            # 加载并显示图片
            if current_path.exists():
                try:
                    if PIL_AVAILABLE:
                        # 使用PIL加载图片
                        img = Image.open(current_path)
                        # 调整图片大小以适应窗口（增大二维码显示尺寸）
                        # 窗口宽度700，减去最小padding和按钮区域，二维码可以显示到约680x680
                        target_size = 680
                        # 获取原图尺寸
                        original_width, original_height = img.size
                        # 计算缩放比例（取较大的边）
                        max_dimension = max(original_width, original_height)
                        
                        if max_dimension < target_size:
                            # 如果原图小于目标尺寸，放大到目标尺寸
                            scale = target_size / max_dimension
                            new_width = int(original_width * scale)
                            new_height = int(original_height * scale)
                            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        else:
                            # 如果原图大于目标尺寸，缩小到目标尺寸
                            img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
                        
                        photo = ImageTk.PhotoImage(img)
                        img_label.config(image=photo, text="", anchor="center")
                        img_label.image = photo  # 保持引用
                    else:
                        # 如果没有PIL，尝试使用PhotoImage（仅支持GIF和PGM，PNG可能不支持）
                        try:
                            photo = PhotoImage(file=str(current_path))
                            img_label.config(image=photo, text="")
                            img_label.image = photo
                        except Exception as e:
                            img_label.config(text=f"无法加载图片（需要安装Pillow库）:\n{str(e)}")
                except Exception as e:
                    img_label.config(text=f"加载图片失败: {e}\n文件路径: {current_path}")
            else:
                # 显示更详细的错误信息
                base_dir = Path(self.save_dir.get().strip() or "qrcodes")
                author_dir = base_dir / self.clean_filename(author_nickname)
                error_msg = f"文件不存在:\n{current_path}\n\n"
                error_msg += f"查找目录: {author_dir}\n"
                if author_dir.exists():
                    # 列出目录中的所有PNG文件
                    png_files = list(author_dir.glob("*.png"))
                    if png_files:
                        error_msg += f"\n目录中的PNG文件:\n"
                        for png_file in png_files[:10]:  # 最多显示10个
                            error_msg += f"  - {png_file.name}\n"
                        if len(png_files) > 10:
                            error_msg += f"  ... 还有 {len(png_files) - 10} 个文件\n"
                    else:
                        error_msg += "\n目录中没有任何PNG文件\n"
                else:
                    error_msg += f"\n目录不存在\n"
                img_label.config(text=error_msg)
        
        # 更新按钮状态的函数
        def update_buttons():
            btn_prev.config(state=DISABLED if current_index <= 0 else NORMAL)
            btn_next.config(state=DISABLED if current_index >= len(sorted_data) - 1 else NORMAL)
        
        # 修改load_image函数，添加按钮更新
        original_load_image = load_image
        def load_image_with_update(index: int):
            original_load_image(index)
            update_buttons()
        
        # 上一张按钮
        def prev_image():
            if current_index > 0:
                load_image_with_update(current_index - 1)
        
        # 下一张按钮
        def next_image():
            if current_index < len(sorted_data) - 1:
                load_image_with_update(current_index + 1)
        
        btn_prev = ttk.Button(
            frm_controls, 
            text="上一张", 
            command=prev_image,
            width=12,
            
        )
        btn_prev.pack(side=LEFT, padx=5, pady=2)
        
        btn_next = ttk.Button(
            frm_controls, 
            text="下一张", 
            command=next_image,
            width=12
        )
        btn_next.pack(side=LEFT, padx=5, pady=2)
        
        # 关闭按钮
        btn_close = ttk.Button(
            frm_controls, 
            text="关闭", 
            command=qr_window.destroy,
            width=12
        )
        btn_close.pack(side=RIGHT, padx=5, pady=2)
        
        # 初始加载
        if current_index >= 0:
            load_image_with_update(current_index)
        else:
            if len(sorted_data) > 0:
                load_image_with_update(0)

    def log(self, msg: str):
        """线程安全的日志输出"""
        def _append():
            # 限制日志行数，避免窗口缩放时卡顿
            line_count = int(self.txt_log.index(END).split('.')[0])
            if line_count > self.max_log_lines:
                # 删除最前面的旧日志，保留最新的（批量删除，减少操作次数）
                delete_count = line_count - self.max_log_lines + 100  # 多删除100行，减少频繁删除
                self.txt_log.delete("1.0", f"{delete_count}.0")
            
            self.txt_log.insert(END, msg + "\n")
            self.txt_log.see(END)

        self.txt_log.after(0, _append)

    def clear_log(self):
        self.txt_log.delete("1.0", END)
    
    def _refresh_user_list(self):
        """刷新用户列表显示（线程安全）"""
        if not hasattr(self, 'tree_user_list'):
            return
        
        def _update():
            # 清空现有数据
            for item in self.tree_user_list.get_children():
                self.tree_user_list.delete(item)
            # 按序号排序后添加
            sorted_data = sorted(self.user_list_data, key=lambda x: x.get('序号', 0))
            for item_data in sorted_data:
                self.tree_user_list.insert("", END, values=(
                    item_data.get('序号', ''),
                    item_data.get('用户昵称', ''),
                    item_data.get('所属博主', ''),
                    item_data.get('获取时间', '')
                ))
            # 滚动到底部
            if self.tree_user_list.get_children():
                self.tree_user_list.see(self.tree_user_list.get_children()[-1])
        
        # 检查是否在主线程（Tkinter主线程）
        import threading
        if threading.current_thread() is threading.main_thread():
            # 主线程直接执行
            _update()
        else:
            # 其他线程使用after
            self.tree_user_list.after(0, _update)
    
    def _add_user_to_list(self, nickname: str, author_nickname: str, rank: int = 0):
        """添加用户到列表（线程安全）"""
        from datetime import datetime
        self.user_list_counter += 1
        user_item = {
            '序号': self.user_list_counter,
            '用户昵称': nickname,
            '所属博主': author_nickname,
            '排名': rank,
            '获取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.user_list_data.append(user_item)
        # 更新GUI显示
        self._refresh_user_list()
        # 保存配置
        self.save_config()

    def load_config(self):
        """从本地文件加载配置"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'cookie1' in config:
                        self.cookie_input1.set(config['cookie1'])
                    if 'cookie2' in config:
                        self.cookie_input2.set(config['cookie2'])
                    if 'cookie3' in config:
                        self.cookie_input3.set(config['cookie3'])
                    if 'cookie4' in config:
                        self.cookie_input4.set(config['cookie4'])
                    if 'urls' in config:
                        # 保存到临时变量，在 _build_ui 后设置
                        self._saved_urls = config['urls']
                    if 'save_dir' in config:
                        # 保存到临时变量，在 _build_ui 后设置
                        self._saved_save_dir = config['save_dir']
                    if 'poll_interval' in config:
                        self.poll_interval.set(config['poll_interval'])
                    if 'auth_code' in config:
                        self.auth_code.set(config['auth_code'])
                    if 'url_to_author_id' in config:
                        # 加载 author_id 缓存
                        self.url_to_author_id = config['url_to_author_id']
                        cache_count = len(self.url_to_author_id)
                        if cache_count > 0:
                            print(f"已加载 {cache_count} 个 URL 的 author_id 缓存")
                            # 保存缓存数量，用于后续显示
                            self._loaded_cache_count = cache_count
                    if 'processed_sec_uids' in config:
                        # 加载已处理的 sec_uid 缓存
                        self.processed_sec_uids = set(config['processed_sec_uids'])
                        qr_cache_count = len(self.processed_sec_uids)
                        if qr_cache_count > 0:
                            print(f"已加载 {qr_cache_count} 个已处理的 sec_uid 缓存")
                    if 'user_list_data' in config:
                        # 加载用户列表数据
                        self.user_list_data = config['user_list_data']
                        if self.user_list_data:
                            # 计算最大序号
                            max_seq = max([item.get('序号', 0) for item in self.user_list_data], default=0)
                            print(f"已加载 {len(self.user_list_data)} 条用户列表记录")
                    if 'user_list_counter' in config:
                        # 加载序号计数器
                        self.user_list_counter = config.get('user_list_counter', 0)
                    else:
                        # 如果没有保存的计数器，从数据中计算
                        if self.user_list_data:
                            self.user_list_counter = max([item.get('序号', 0) for item in self.user_list_data], default=0)
        except Exception as e:
            print(f"加载配置失败: {e}")

    def save_config(self):
        """保存配置到本地文件"""
        try:
            config = {
                'cookie1': self.cookie_input1.get(),
                'cookie2': self.cookie_input2.get(),
                'cookie3': self.cookie_input3.get(),
                'cookie4': self.cookie_input4.get(),
                'urls': self.txt_urls.get("1.0", END).strip() if hasattr(self, 'txt_urls') else "",
                'save_dir': self.save_dir.get() if hasattr(self, 'save_dir') else "qrcodes",
                'poll_interval': self.poll_interval.get(),
                'auth_code': self.auth_code.get() if hasattr(self, 'auth_code') else "",
                'url_to_author_id': self.url_to_author_id,  # 保存 author_id 缓存
                'processed_sec_uids': list(self.processed_sec_uids),  # 保存已处理的 sec_uid 列表
                'user_list_data': self.user_list_data,  # 保存用户列表数据
                'user_list_counter': self.user_list_counter  # 保存序号计数器
            }
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def _save_author_id_cache(self):
        """快速保存 author_id 缓存到本地文件"""
        try:
            # 读取现有配置
            config = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)

            # 更新缓存部分
            config['url_to_author_id'] = self.url_to_author_id
            config['processed_sec_uids'] = list(self.processed_sec_uids)

            # 保存配置
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存 author_id 缓存失败: {e}")
    
    def _save_sec_uid_cache(self):
        """快速保存已处理的 sec_uid 缓存到本地文件"""
        try:
            # 读取现有配置
            config = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)

            # 更新缓存部分
            config['processed_sec_uids'] = list(self.processed_sec_uids)

            # 保存配置
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存 sec_uid 缓存失败: {e}")

    def quit_application(self):
        """退出应用程序，停止所有任务"""
        self.log("正在停止所有任务并退出...")
        
        # 停止轮询
        if self.is_polling:
            self.is_polling = False
            self.btn_start_poll.config(state=NORMAL)
            self.btn_stop_poll.config(state=DISABLED)
            if self.poll_thread and self.poll_thread.is_alive():
                self.log("正在停止轮询任务...")
                self.poll_thread.join(timeout=2)
        
        # 标记任务停止
        self.is_running_task = False
        
        # 保存配置
        try:
            self.save_config()
        except Exception as e:
            print(f"保存配置失败: {e}")
        
        # 关闭窗口
        self.master.quit()
        self.master.destroy()
    
    def on_closing(self):
        """窗口关闭时保存配置"""
        self.quit_application()

    def test_cookie_validity(self, cookie: str) -> bool:
        """
        测试 Cookie 是否有效
        
        Args:
            cookie: Cookie 字符串
            
        Returns:
            bool: True 表示有效，False 表示无效
        """
        if not cookie or not cookie.strip():
            return False
        
        try:
            test_url = f"{API_BASE}/qrcode_url"
            params = {
                "sec_user_id": "MS4wLjABAAAAcTVO3R6q-OTLfoqHdrZR4o_uysUnAQDVwlfBnUxoEFA",
                "cookie_web": cookie.strip()
            }
            resp = requests.get(test_url, params=params, timeout=10, verify=False)
            if resp.status_code == 200:
                data = resp.json()
                # 检查返回数据是否有效（有user字段或status_code为0表示成功）
                if isinstance(data, dict) and ('user' in data or data.get('status_code') == 0):
                    return True
            return False
        except Exception:
            return False
    
    def validate_cookies(self):
        """
        验证所有 Cookie 的有效性，过滤掉无效的 Cookie
        
        Returns:
            list: 有效的 Cookie 列表
        """
        self.log("开始验证 Cookie 有效性...")
        
        # 获取所有 Cookie（合并所有输入框）
        all_cookies = []
        cookie_sources = [
            ("Cookie 1", self.cookie_input1),
            ("Cookie 2", self.cookie_input2),
            ("Cookie 3", self.cookie_input3),
            ("Cookie 4", self.cookie_input4),
        ]
        
        for source_name, cookie_var in cookie_sources:
            cookies = [line.strip() for line in cookie_var.get().strip().splitlines() if line.strip()]
            for cookie in cookies:
                all_cookies.append((source_name, cookie))
        
        if not all_cookies:
            self.log("未输入任何 Cookie")
            return []
        
        # 测试所有 cookies
        valid_cookies = []
        invalid_cookies = []
        
        for idx, (source_name, cookie) in enumerate(all_cookies, 1):
            self.log(f"测试 {source_name} ({idx}/{len(all_cookies)})...")
            if self.test_cookie_validity(cookie):
                valid_cookies.append((source_name, cookie))
            else:
                invalid_cookies.append((source_name, idx))
                self.log(f"[警告] {source_name} 第 {idx} 行无效，已移除")
        
        # 按来源分组有效的 Cookie
        valid_by_source = {"Cookie 1": [], "Cookie 2": [], "Cookie 3": [], "Cookie 4": []}
        for source_name, cookie in valid_cookies:
            valid_by_source[source_name].append(cookie)
        
        # 更新 Cookie 输入框，只保留有效的
        self.cookie_input1.set("\n".join(valid_by_source["Cookie 1"]))
        self.cookie_input2.set("\n".join(valid_by_source["Cookie 2"]))
        self.cookie_input3.set("\n".join(valid_by_source["Cookie 3"]))
        self.cookie_input4.set("\n".join(valid_by_source["Cookie 4"]))
        
        self.txt_cookie1.delete("1.0", END)
        self.txt_cookie2.delete("1.0", END)
        self.txt_cookie3.delete("1.0", END)
        self.txt_cookie4.delete("1.0", END)
        
        if valid_by_source["Cookie 1"]:
            self.txt_cookie1.insert("1.0", "\n".join(valid_by_source["Cookie 1"]))
        if valid_by_source["Cookie 2"]:
            self.txt_cookie2.insert("1.0", "\n".join(valid_by_source["Cookie 2"]))
        if valid_by_source["Cookie 3"]:
            self.txt_cookie3.insert("1.0", "\n".join(valid_by_source["Cookie 3"]))
        if valid_by_source["Cookie 4"]:
            self.txt_cookie4.insert("1.0", "\n".join(valid_by_source["Cookie 4"]))
        
        # 输出统计信息
        self.log(f"\nCookie 验证完成:")
        self.log(f"  Cookie 1: {len(valid_by_source['Cookie 1'])} 个有效")
        self.log(f"  Cookie 2: {len(valid_by_source['Cookie 2'])} 个有效")
        self.log(f"  Cookie 3: {len(valid_by_source['Cookie 3'])} 个有效")
        self.log(f"  Cookie 4: {len(valid_by_source['Cookie 4'])} 个有效")
        self.log(f"  总计: {len(valid_cookies)}/{len(all_cookies)} 个有效")
        
        if invalid_cookies:
            self.log(f"[提示] 已自动移除无效的 Cookie，请检查配置")
        
        # 返回所有有效的 Cookie（扁平化列表）
        return [cookie for _, cookie in valid_cookies]
    
    def get_random_cookie(self) -> str:
        """
        从所有 Cookie 输入框中随机选择一个

        Returns:
            str: 随机选择的 Cookie 字符串，如果没有则返回空字符串
        """
        # 收集所有 Cookie（从所有输入框）
        all_cookies = []
        for cookie_var in [self.cookie_input1, self.cookie_input2, self.cookie_input3, self.cookie_input4]:
            cookie_str = cookie_var.get().strip()
            if cookie_str:
                cookies = [line.strip() for line in cookie_str.splitlines() if line.strip()]
                all_cookies.extend(cookies)
        
        if not all_cookies:
            return ""
        
        # 随机选择一个
        return random.choice(all_cookies)

    def clean_filename(self, filename: str) -> str:
        """
        清理文件名，移除文件系统不支持的字符

        Args:
            filename: 原始文件名

        Returns:
            清理后的文件名
        """
        # 移除或替换文件系统不支持的字符
        invalid_chars = r'[<>:"/\\|?*]'
        filename = re.sub(invalid_chars, '_', filename)
        # 移除首尾空格和点
        filename = filename.strip(' .')
        # 限制长度（Windows 文件名最大 255 字符）
        if len(filename) > 200:
            filename = filename[:200]
        return filename or "unknown"

    def save_qrcode(self, author_nickname: str, rank: int, nickname: str, qr_url: str = None, qr_base64: str = None):
        """
        保存二维码图片到本地

        Args:
            author_nickname: 博主昵称（用于创建文件夹）
            rank: 排名
            nickname: 用户昵称（用于文件名）
            qr_url: 二维码图片 URL
            qr_base64: 二维码 base64 数据

        Returns:
            bool: 是否成功保存了新图片（True表示新增，False表示已存在或失败）
        """
        try:
            global proxies
            # 创建保存目录
            base_dir = Path(self.save_dir.get().strip() or "qrcodes")
            author_dir = base_dir / self.clean_filename(author_nickname)
            author_dir.mkdir(parents=True, exist_ok=True)

            # 清理文件名
            clean_nickname = self.clean_filename(nickname)
            filename = f"{rank}_{clean_nickname}"

            # 检查是否已存在（缓存检查）
            png_path = author_dir / f"{filename}.png"

            if png_path.exists():
                self.log(f"[缓存] 排名={rank} nickname={nickname} 二维码已存在，跳过下载")
                return False  # 已存在，不是新增

            # 保存二维码
            if qr_url:
                # 从 URL 下载图片，重试2次
                max_retries = 3
                retry_count = 0
                success = False
                while retry_count <= max_retries and not success:
                    try:
                        resp = requests.get(
                            qr_url, timeout=30, verify=False)
                        resp.raise_for_status()
                        png_path.write_bytes(resp.content)
                        self.log(
                            f"[保存] 排名={rank} 昵称={nickname} 二维码已保存: {png_path}")
                        success = True
                        # 添加到用户列表
                        self._add_user_to_list(nickname, author_nickname, rank)
                        return True  # 成功保存新图片
                    except Exception as e:
                        retry_count += 1
                        if retry_count <= max_retries:
                            self.log(
                                f"[保存失败] rank={rank} 昵称={nickname} URL下载失败，重试 {retry_count}/{max_retries}: {e}")
                            time.sleep(5)
                        else:
                            self.log(
                                f"[保存失败] rank={rank} 昵称={nickname} URL下载失败，已重试 {max_retries} 次: {e}")
                return False  # 保存失败
            elif qr_base64:
                # 将 base64 解码为图片并保存
                try:
                    # 解码 base64 数据
                    img_data = base64.b64decode(qr_base64)
                    # 保存为 PNG 图片
                    png_path.write_bytes(img_data)
                    self.log(
                        f"[保存] 排名={rank} nickname={nickname} 二维码(base64转图片)已保存: {png_path}")
                    # 添加到用户列表
                    self._add_user_to_list(nickname, author_nickname, rank)
                    return True  # 成功保存新图片
                except Exception as e:
                    self.log(
                        f"[保存失败] rank={rank} nickname={nickname} base64解码失败: {e}")
                    return False  # 保存失败
            return False  # 没有提供有效的二维码数据
        except Exception as e:
            self.log(f"[保存失败] rank={rank} nickname={nickname} 保存失败: {e}")
            return False  # 保存失败

    # 开始任务
    def start_task(self):
        
        
        auth_code = self.auth_code.get().strip()
        print(
            auth_code
        )
        pjysdk.on_heartbeat_failed = on_heartbeat_failed  # 设置心跳失败回调函数
        mac_num = hex(uuid.getnode()).replace('0x', '').upper()
        mac_address = ':'.join(mac_num[i: i + 2] for i in range(0, 12, 2))
        print(mac_address)
        pjysdk.set_device_id(mac_address)  # 设置设备唯一ID
        pjysdk.set_card(auth_code)  # 设置卡密

        ret = pjysdk.card_login()  # 卡密登录
        # print("登录结果:", ret.code, ret.message)
        # 安全判断：ret 可能是 dict 或对象
        if isinstance(ret, dict):
            code = ret.get('code')
            message = ret.get('message', '未知错误')
        else:
            # 假设是对象
            code = getattr(ret, 'code', -1)
            message = getattr(ret, 'message', '未知错误')
        print(f"登录结果: {code} {message}")
        if code != 0:  # 登录失败
            print("❌ 登录失败")
            print(message)
            is_access = False
            # os._exit(1)  # 退出脚本
        else:
            is_access = True
            print("✅ 登录成功")

        if not is_access:
            messagebox.showerror(
                    "错误", f"❌ {is_access}无权限，请联系✈️:maotai8866")
            return      
        
        if self.is_running_task:
            self.log("任务正在运行中，请等待完成或点击退出停止")
            return
            
        urls_raw = self.txt_urls.get("1.0", END).strip()
        if not urls_raw:
            self.log("请先输入DY主页链接，每行一个")
            return

        # 输入的连接数组
        url_list = [line.strip()
                    for line in urls_raw.splitlines() if line.strip()]
        if not url_list:
            self.log("未检测到有效链接")
            return

        rank_type = "1"  # 固定使用本周榜

        # 在后台线程中验证 Cookie 有效性，避免阻塞GUI
        self.is_running_task = True
        threading.Thread(
            target=self._validate_and_start_task,
            args=(rank_type, url_list),
            daemon=True
        ).start()

    def _validate_and_start_task(self, rank_type: str, url_list: list):
        """在后台线程中验证Cookie并启动任务"""
        # 验证 Cookie 有效性
        valid_cookies = self.validate_cookies()
        
        if not valid_cookies:
            self.log("[错误] 没有有效的 Cookie，无法继续运行")
            self.is_running_task = False
            return

        # Cookie验证完成，启动工作流
        self.run_workflow(rank_type, url_list)

    def start_polling(self):
        
        
        auth_code = self.auth_code.get().strip()
        print(
            auth_code
        )
        pjysdk.on_heartbeat_failed = on_heartbeat_failed  # 设置心跳失败回调函数
        mac_num = hex(uuid.getnode()).replace('0x', '').upper()
        mac_address = ':'.join(mac_num[i: i + 2] for i in range(0, 12, 2))
        print(mac_address)
        pjysdk.set_device_id(mac_address)  # 设置设备唯一ID
        pjysdk.set_card(auth_code)  # 设置卡密

        ret = pjysdk.card_login()  # 卡密登录
        # print("登录结果:", ret.code, ret.message)
        # 安全判断：ret 可能是 dict 或对象
        if isinstance(ret, dict):
            code = ret.get('code')
            message = ret.get('message', '未知错误')
        else:
            # 假设是对象
            code = getattr(ret, 'code', -1)
            message = getattr(ret, 'message', '未知错误')
        print(f"登录结果: {code} {message}")
        if code != 0:  # 登录失败
            print("❌ 登录失败")
            print(message)
            is_access = False
            # os._exit(1)  # 退出脚本
        else:
            is_access = True
            print("✅ 登录成功")

        if not is_access:
            messagebox.showerror(
                    "错误", f"❌ {is_access}无权限，请联系✈️:maotai8866")
            return         
        
        """开始定时轮询"""
        urls_raw = self.txt_urls.get("1.0", END).strip()
        if not urls_raw:
            self.log("请先输入DY主页链接，每行一个")
            return

        url_list = [line.strip()
                    for line in urls_raw.splitlines() if line.strip()]
        if not url_list:
            self.log("未检测到有效链接")
            return

        if self.is_polling:
            self.log("轮询已在运行中")
            return

        self.is_polling = True
        self.btn_start_poll.config(state=DISABLED)
        self.btn_stop_poll.config(state=NORMAL)

        interval = max(10, self.poll_interval.get())  # 最少10秒
        self.log(f"开始验证 Cookie，验证完成后将开始定时轮询，间隔 {interval} 秒")

        # 在后台线程中验证Cookie并启动轮询，避免阻塞GUI
        threading.Thread(
            target=self._validate_and_start_polling,
            args=(url_list, interval),
            daemon=True
        ).start()

    def _validate_and_start_polling(self, url_list: list, interval: int):
        """在后台线程中验证Cookie并启动轮询"""
        # 验证 Cookie 有效性
        valid_cookies = self.validate_cookies()
        
        if not valid_cookies:
            self.log("[错误] 没有有效的 Cookie，无法继续运行")
            self.is_polling = False
            self.btn_start_poll.config(state=NORMAL)
            self.btn_stop_poll.config(state=DISABLED)
            return

        # Cookie验证完成，启动轮询
        self.log(f"Cookie 验证完成，开始定时轮询，间隔 {interval} 秒")
        self.poll_thread = threading.Thread(
            target=self._polling_loop,
            args=(url_list, interval),
            daemon=True
        )
        self.poll_thread.start()

    def stop_polling(self):
        """停止定时轮询"""
        if not self.is_polling:
            return

        self.is_polling = False
        self.btn_start_poll.config(state=NORMAL)
        self.btn_stop_poll.config(state=DISABLED)
        self.log("已停止定时轮询")

    def _polling_loop(self, url_list: list[str], interval: int):
        """轮询循环"""
        rank_type = "1"  # 固定使用本周榜

        round_count = 0
        while self.is_polling:
            round_count += 1
            self.log(f"\n========== 第 {round_count} 轮轮询开始 ==========")

            # 如果缓存中有数据，直接使用缓存；否则第一次轮询需要请求 userinfo 获取 author_id
            # 后续轮询都使用缓存，跳过 userinfo 请求
            has_cache = any(url in self.url_to_author_id for url in url_list)
            skip_userinfo = (round_count > 1) or has_cache
            if skip_userinfo:
                if has_cache and round_count == 1:
                    self.log("检测到本地缓存，使用缓存的 a_i，跳过 uinfo")
                elif round_count > 1:
                    self.log("使用缓存的 a_i，跳过 uinfo")

            # 执行一次完整的任务流程
            self.run_workflow(rank_type, url_list, skip_userinfo=skip_userinfo)

            if not self.is_polling:
                break

            # 等待指定间隔时间
            self.log(f"等待 {interval} 秒后进行下一轮轮询...")
            for _ in range(interval):
                if not self.is_polling:
                    break
                threading.Event().wait(1)  # 每秒检查一次状态

        self.log("轮询循环已结束")

    # 主要的任务处理

    def run_workflow(self, rank_type: str, url_list: list[str], skip_userinfo: bool = False):
        # 检查是否应该停止
        if not self.is_running_task and not self.is_polling:
            return
            
        # 并发处理每个链接（单个链接内部仍串行）
        max_workers = max(1, min(self.max_workers.get(), 20))

        # 检查缓存情况
        cached_count = sum(
            1 for url in url_list if url in self.url_to_author_id)
        if cached_count > 0:
            self.log(f"检测到 {cached_count}/{len(url_list)} 个链接有缓存，将优先使用缓存")

        if skip_userinfo:
            self.log(
                f"开始处理 {len(url_list)} 个链接（轮询模式），最大并发 {max_workers}")
        else:
            self.log(f"开始处理 {len(url_list)} 个链接，最大并发 {max_workers}")

        # 创建线程安全的统计字典
        author_new_images = {}
        stats_lock = threading.Lock()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for idx, user_url in enumerate(url_list, 1):
                # 优先使用缓存的 author_id（如果存在）
                cached_author_id = None
                cached_author_nickname = None
                if user_url in self.url_to_author_id:
                    cached_data = self.url_to_author_id[user_url]
                    cached_author_id = cached_data.get('author_id')
                    cached_author_nickname = cached_data.get('author_nickname')
                elif skip_userinfo:
                    # 如果要求跳过 userinfo 但缓存中没有，记录警告
                    self.log(f"[警告] URL {user_url} 在缓存中不存在，但要求跳过 uinfo")

                futures.append(
                    executor.submit(self.process_single_url, idx, user_url,
                                    rank_type,
                                    cached_author_id, cached_author_nickname,
                                    author_new_images, stats_lock)
                )

            for future in as_completed(futures):
                # 检查是否应该停止
                if not self.is_running_task and not self.is_polling:
                    self.log("任务已停止")
                    # 取消未完成的任务
                    for f in futures:
                        if not f.done():
                            f.cancel()
                    break
                # 结果已在 process_single_url 中记录日志
                pass

        # 输出统计信息
        self.log("\n========== 本轮新增图片统计 ==========")
        if author_new_images:
            for author_nickname, count in sorted(author_new_images.items()):
                self.log(f"博主 {author_nickname}: 新增 {count} 张图片")
        else:
            self.log("本轮未新增图片")
        self.log("=====================================\n")

        self.is_running_task = False
        if self.is_polling:
            self.log("本轮处理完毕。\n")
        else:
            self.log("全部链接处理完毕。\n")

    def process_single_url(self, idx: int, user_url: str, rank_type: str, cached_author_id: str = None, cached_author_nickname: str = None, author_new_images: dict = None, stats_lock: threading.Lock = None):
        # 检查是否应该停止
        if not self.is_running_task and not self.is_polling:
            return
            
        self.log(f"------ 开始处理第 {idx} 个链接 ------")
        self.log(f"执行URL: {user_url}")

        # 1) 调用 userinfo（如果提供了缓存的 author_id，则跳过）
        if cached_author_id and cached_author_nickname:
            author_id = cached_author_id
            author_nickname = cached_author_nickname
            self.log(
                f"[用户信息] 使用缓存的 a_i={author_id}, 博主昵称={author_nickname}")
        else:
            userinfo_url = f"{API_BASE}/userinfo"
            try:
                # 随机选择一个 cookie
                cookie_userinfo = self.get_random_cookie()
                params = {"url": user_url}
                if cookie_userinfo:
                    params["cookie_web"] = cookie_userinfo
                resp_user = requests.get(
                    userinfo_url,
                    params=params,
                    timeout=30,
                    verify=False,
                )
                user_data = resp_user.json()
            except Exception as e:
                self.log(f"[用户信息] 请求失败: {e}")
                return

            if user_data.get("code") != 200:
                self.log(f"[用户信息] 接口返回错误: {user_data}")
                return

            author_id = user_data.get("data", {}).get("author_id")
            author_nickname = user_data.get(
                "data", {}).get("nickname", "unknown")
            self.log(f"[用户信息] a_i={author_id}, 博主昵称={author_nickname}")
            print(f"[用户信息] a_i={author_id}")

            if not author_id:
                self.log("[用户信息] 未获取到 author_id，跳过此链接")
                return

            # 保存到缓存
            self.url_to_author_id[user_url] = {
                'author_id': author_id,
                'author_nickname': author_nickname
            }
            # 立即保存缓存到本地文件
            self._save_author_id_cache()

        # 2) 调用 subscribe
        subscribe_url = f"{API_BASE}/subscribe"
        try:
            # 随机选择一个 cookie
            cookie_subscribe = self.get_random_cookie()
            params = {"author_id": author_id, "rank_type": rank_type}
            if cookie_subscribe:
                params["cookie_subscribe"] = cookie_subscribe
            resp_sub = requests.get(
                subscribe_url,
                params=params,
                timeout=30,
                verify=False,
            )
            sub_data = resp_sub.json()
        except Exception as e:
            self.log(f"[榜单] 请求失败: {e}")
            return

        rank_list = sub_data.get("rank_list", [])
        self.log(f"[榜单] 博主{author_nickname}-获取到 {len(rank_list)} 条榜单数据")
        print(f"[榜单] 博主{author_nickname}获取到 {len(rank_list)} 条榜单数据")

        # 3) 遍历 rank_list 调用 qrcode_url（并发执行，减少长队列等待）
        qrcode_url_api = f"{API_BASE}/qrcode_url"
        max_rank_workers = min(5, len(rank_list)) or 1

        def fetch_qr(item):

            # print('====itrm====', item.get("user", {}))

            sec_uid = (
                item.get("user", {}).get("sec_uid")
                if isinstance(item, dict)
                else None
            )
            rank_no = item.get("rank") if isinstance(item, dict) else None
            nickname = (
                item.get("user", {}).get("nickname")
                if isinstance(item, dict)
                else None
            )
            print(f"[榜单] rank={rank_no} nickname={nickname} sec_uid={sec_uid}")

            if not sec_uid:
                return

            # 检查缓存
            base_dir = Path(self.save_dir.get().strip() or "qrcodes")
            author_dir = base_dir / self.clean_filename(author_nickname)
            clean_nickname = self.clean_filename(
                nickname) if nickname else "unknown"
            filename = f"{rank_no}_{clean_nickname}" if rank_no else clean_nickname
            png_path = author_dir / f"{filename}.png"

            if png_path.exists():
                self.log(
                    f"[缓存] 排名={rank_no} nickname={nickname} 二维码已存在，跳过请求")
                return

            # 检查 sec_uid 是否已处理过
            if sec_uid in self.processed_sec_uids:
                # 已处理过，直接跳过
                # self.log(
                #     f"[缓存] 博主{author_nickname} s_u={sec_uid} 已处理过")
                return

            # 请求 qrcode_url 接口，获取用户信息，重试2次
            max_retries = 4
            retry_count = 0
            qr_data = None
            while retry_count <= max_retries and qr_data is None:
                try:
                    # 随机选择一个 cookie
                    cookie_qrcode = self.get_random_cookie()
                    params = {"sec_user_id": sec_uid}
                    if cookie_qrcode:
                        params["cookie_web"] = cookie_qrcode
                    resp_qr = requests.get(
                        qrcode_url_api,
                        params=params,
                        timeout=30,
                        verify=False,
                    )
                    qr_data = resp_qr.json()
                    # 接口调用成功，将 sec_uid 添加到已处理集合
                    self.processed_sec_uids.add(sec_uid)
                    # 立即保存缓存到本地文件
                    self._save_sec_uid_cache()
                except Exception as e:
                    retry_count += 1
                    if retry_count <= max_retries:
                        self.log(
                            f"[榜单用户] 博主：{author_nickname} 请求失败 s_u={sec_uid}，重试 {retry_count}/{max_retries}: {e}")
                        time.sleep(2)
                    else:
                        self.log(
                            f"[榜单用户] 博主：{author_nickname} 请求失败 s_u={sec_uid}，已重试 {max_retries} 次: {e}")
                        return

            if qr_data is None:
                return

            # 从 qrcode_url 接口获取完整的 nickname
            full_nickname = qr_data.get("user", {}).get(
                "nickname") if isinstance(qr_data, dict) else None
            # 如果获取不到，则使用原来的 nickname 作为后备
            display_nickname = full_nickname or nickname or "unknown"

            share_info = qr_data.get("user", {}).get(
                "share_info", {}) if isinstance(qr_data, dict) else {}
            qr_obj = share_info.get("share_qrcode_url", {}) if isinstance(
                share_info, dict) else {}
            url_list = qr_obj.get("url_list") if isinstance(
                qr_obj, dict) else None
            qr_url = url_list[0] if url_list and len(url_list) > 0 else qr_obj.get(
                "url") if isinstance(qr_obj, dict) else None

            if qr_url:
                self.log(
                    f"[榜单用户] 博主{author_nickname} 排名={rank_no} 昵称={display_nickname} s_u={sec_uid} 二维码: {qr_url}")
                # 保存二维码，使用完整的 nickname
                is_new = self.save_qrcode(author_nickname, rank_no or 0,
                                         display_nickname, qr_url=qr_url)
                # 统计新增图片
                if is_new and author_new_images is not None and stats_lock is not None:
                    with stats_lock:
                        author_new_images[author_nickname] = author_new_images.get(author_nickname, 0) + 1
            else:
                # 如果 url_list 为空，尝试使用 share_url 生成二维码
                share_url = share_info.get("share_url") if isinstance(
                    share_info, dict) else None
                if share_url:
                    # 请求二维码生成接口，重试2次
                    max_gen_retries = 3
                    gen_retry_count = 0
                    qr_base64 = None
                    while gen_retry_count <= max_gen_retries and qr_base64 is None:
                        try:
                            # 请求二维码生成接口，对 data 参数进行 URL 编码
                            data_url = f"https://{share_url}"
                            encoded_data = quote(data_url, safe='')
                            qr_gen_url = f"https://api.2dcode.biz/v1/create-qr-code?data={encoded_data}"
                            resp_qr_gen = requests.get(
                                qr_gen_url, timeout=30, verify=False)
                            resp_qr_gen.raise_for_status()
                            # 将二进制图片数据转换为 base64
                            qr_base64 = base64.b64encode(
                                resp_qr_gen.content).decode('utf-8')
                            # 打印前50个字符
                            qr_preview = qr_base64[:50] if len(
                                qr_base64) > 50 else qr_base64
                            self.log(
                                f"[榜单用户] 博主{author_nickname} 排名={rank_no} 昵称={display_nickname} s_u={sec_uid} 二维码base64(前50字符): {qr_preview}...")
                            # 保存二维码 base64，使用完整的 nickname
                            is_new = self.save_qrcode(
                                author_nickname, rank_no or 0, display_nickname, qr_base64=qr_base64)
                            # 统计新增图片
                            if is_new and author_new_images is not None and stats_lock is not None:
                                with stats_lock:
                                    author_new_images[author_nickname] = author_new_images.get(author_nickname, 0) + 1
                        except Exception as gen_e:
                            gen_retry_count += 1
                            if gen_retry_count <= max_gen_retries:
                                self.log(
                                    f"[榜单用户] 博主{author_nickname} 排名={rank_no} 昵称={display_nickname} s_u={sec_uid} 生成二维码失败，重试 {gen_retry_count}/{max_gen_retries}: {gen_e}")
                            else:
                                self.log(
                                    f"[榜单用户] 博主{author_nickname} 排名={rank_no} 昵称={display_nickname} s_u={sec_uid} 生成二维码失败，已重试 {max_gen_retries} 次: {gen_e}")
                else:
                    self.log(
                        f"[榜单用户] 博主{author_nickname} 排名={rank_no} 昵称={display_nickname} s_u={sec_uid} 未返回二维码链接和share_url，原始字段: {qr_obj}")

        with ThreadPoolExecutor(max_workers=max_rank_workers) as inner_executor:
            for item in rank_list:
                inner_executor.submit(fetch_qr, item)

        self.log(f"------ 完成第 {idx} 个链接 ------\n")


def main():

    from datetime import datetime
    current_date = datetime.now()
    expiry_date = datetime(2026, 3, 31, 23, 59, 59)
    if current_date > expiry_date:
        os._exit(0)
    
    root = ttk.Window(themename="litera")
    app = DouyinGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
