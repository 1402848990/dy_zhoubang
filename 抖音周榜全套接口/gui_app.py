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
import requests
import base64
import os
import re
from pathlib import Path
from urllib.parse import quote
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


API_BASE_DEFAULT = "http://localhost:5000"
MAX_WORKERS_DEFAULT = 5  # 并发处理链接数量

# 配置文件路径
CONFIG_FILE = "gui_config.json"


class DouyinGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("DY周榜【作者tg：maotai8866】")
        self.style = ttk.Style("litera")
        self.api_base = ttk.StringVar(value=API_BASE_DEFAULT)
        self.rank_type = ttk.StringVar(value="1")  # 1:本周榜 2:上周榜 3:今年榜
        self.max_workers = ttk.IntVar(value=MAX_WORKERS_DEFAULT)
        self.cookie_input = ttk.StringVar(value="")  # 统一 Cookie 输入
        self.poll_interval = ttk.IntVar(value=60)  # 轮询间隔时间（秒），默认60秒
        self.is_polling = False  # 轮询状态标志
        self.poll_thread = None  # 轮询线程
        self.url_to_author_id = {}  # URL 到 author_id 的映射缓存

        # 加载保存的配置
        self.load_config()

        self._build_ui()

        # 绑定窗口关闭事件，保存配置
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _build_ui(self):
        # 顶部配置区域
        frm_top = ttk.Frame(self.master, padding=10)
        frm_top.pack(fill=X)

        ttk.Label(frm_top, text="接口基址:").grid(
            row=0, column=0, sticky=W, padx=(0, 5))
        ttk.Entry(frm_top, textvariable=self.api_base, width=45).grid(
            row=0, column=1, sticky=W
        )

        # rank_type 隐藏，默认使用 "1"（本周榜）
        # ttk.Label(frm_top, text="rank_type:").grid(row=0, column=2, sticky=W, padx=(10, 5))
        # ttk.Combobox(...).grid(row=0, column=3, sticky=W)

        ttk.Label(frm_top, text="并发数:").grid(
            row=0, column=2, sticky=W, padx=(10, 5))
        ttk.Spinbox(
            frm_top,
            from_=1,
            to=20,
            textvariable=self.max_workers,
            width=5,
        ).grid(row=0, column=3, sticky=W)

        # 保存目录配置
        ttk.Label(frm_top, text="保存目录:").grid(
            row=0, column=4, sticky=W, padx=(10, 5))
        self.save_dir = ttk.StringVar(value="qrcodes")  # 默认保存目录
        ttk.Entry(frm_top, textvariable=self.save_dir, width=30).grid(
            row=0, column=5, sticky=W
        )

        # Cookie 配置区域
        frm_cookie = ttk.Labelframe(
            self.master, text="Cookie 配置", padding=10)
        frm_cookie.pack(fill=X, padx=10, pady=5)

        ttk.Label(frm_cookie, text="Cookie:").grid(
            row=0, column=0, sticky=W+N, padx=(0, 5))
        txt_cookie = ttk.Text(frm_cookie, height=3, wrap="word", width=80)
        txt_cookie.grid(row=0, column=1, sticky=W+E, padx=(0, 10))
        frm_cookie.columnconfigure(1, weight=1)

        # 绑定文本变化事件，同步到 StringVar 并自动保存
        def on_cookie_change(event=None):
            self.cookie_input.set(txt_cookie.get("1.0", END).strip())
            self.save_config()
        txt_cookie.bind('<KeyRelease>', on_cookie_change)
        txt_cookie.bind('<Button-1>', on_cookie_change)
        self.txt_cookie = txt_cookie

        # 输入区域
        frm_input = ttk.Labelframe(
            self.master, text="DY主页链接（每行一个）", padding=10)
        frm_input.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # 创建滚动条
        scrollbar_urls = ttk.Scrollbar(frm_input)
        scrollbar_urls.pack(side=RIGHT, fill=Y)

        self.txt_urls = ttk.Text(frm_input, height=10, wrap="word", yscrollcommand=scrollbar_urls.set)
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

        ttk.Button(frm_btn, text="开始运行", bootstyle=SUCCESS, command=self.start_task).pack(
            side=LEFT
        )
        ttk.Button(frm_btn, text="清空日志", bootstyle=SECONDARY, command=self.clear_log).pack(
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
            frm_poll, text="开始监听", bootstyle=INFO, command=self.start_polling
        )
        self.btn_start_poll.pack(side=LEFT, padx=(0, 5))
        
        self.btn_stop_poll = ttk.Button(
            frm_poll, text="停止监听", bootstyle=DANGER, command=self.stop_polling, state=DISABLED
        )
        self.btn_stop_poll.pack(side=LEFT)

        # 日志输出
        frm_log = ttk.Labelframe(self.master, text="日志", padding=10)
        frm_log.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        # 创建滚动条
        scrollbar_log = ttk.Scrollbar(frm_log)
        scrollbar_log.pack(side=RIGHT, fill=Y)

        self.txt_log = ttk.Text(frm_log, height=20, wrap="word", yscrollcommand=scrollbar_log.set)
        self.txt_log.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 关联滚动条和文本框
        scrollbar_log.config(command=self.txt_log.yview)

        # 回填保存的配置数据
        if hasattr(self, '_saved_urls') and self._saved_urls:
            self.txt_urls.insert("1.0", self._saved_urls)
        if hasattr(self, '_saved_save_dir'):
            self.save_dir.set(self._saved_save_dir)
        # Cookie 已经在 load_config 中设置了
        if self.cookie_input.get():
            self.txt_cookie.insert("1.0", self.cookie_input.get())

    def log(self, msg: str):
        """线程安全的日志输出"""
        def _append():
            self.txt_log.insert(END, msg + "\n")
            self.txt_log.see(END)

        self.txt_log.after(0, _append)

    def clear_log(self):
        self.txt_log.delete("1.0", END)

    def load_config(self):
        """从本地文件加载配置"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'cookie' in config:
                        self.cookie_input.set(config['cookie'])
                    if 'urls' in config:
                        # 保存到临时变量，在 _build_ui 后设置
                        self._saved_urls = config['urls']
                    if 'api_base' in config:
                        self.api_base.set(config['api_base'])
                    if 'save_dir' in config:
                        # 保存到临时变量，在 _build_ui 后设置
                        self._saved_save_dir = config['save_dir']
                    if 'poll_interval' in config:
                        self.poll_interval.set(config['poll_interval'])
                    if 'url_to_author_id' in config:
                        # 加载 author_id 缓存
                        self.url_to_author_id = config['url_to_author_id']
                        cache_count = len(self.url_to_author_id)
                        if cache_count > 0:
                            print(f"已加载 {cache_count} 个 URL 的 author_id 缓存")
                            # 保存缓存数量，用于后续显示
                            self._loaded_cache_count = cache_count
        except Exception as e:
            print(f"加载配置失败: {e}")

    def save_config(self):
        """保存配置到本地文件"""
        try:
            config = {
                'cookie': self.cookie_input.get(),
                'urls': self.txt_urls.get("1.0", END).strip() if hasattr(self, 'txt_urls') else "",
                'api_base': self.api_base.get(),
                'save_dir': self.save_dir.get() if hasattr(self, 'save_dir') else "qrcodes",
                'poll_interval': self.poll_interval.get(),
                'url_to_author_id': self.url_to_author_id  # 保存 author_id 缓存
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
            
            # 保存配置
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存 author_id 缓存失败: {e}")

    def on_closing(self):
        """窗口关闭时保存配置"""
        # 停止轮询
        if self.is_polling:
            self.stop_polling()
            # 等待轮询线程结束
            if self.poll_thread and self.poll_thread.is_alive():
                self.poll_thread.join(timeout=2)
        self.save_config()
        self.master.destroy()

    def split_cookie(self, cookie_str: str):
        """
        根据 Cookie 特征自动拆分为移动端和 Web 端 Cookie

        Args:
            cookie_str: 用户输入的 Cookie 字符串

        Returns:
            tuple: (cookie_subscribe, cookie_web)
        """
        if not cookie_str or not cookie_str.strip():
            return "", ""

        cookie_str = cookie_str.strip()

        # Web 端 Cookie 特征
        web_features = [
            'hevc_supported',
            'UIFID',
            'bd_ticket_guard_client_web_domain',
            's_v_web_id',
            'SelfTabRedDotControl',
            'xgplayer_device_id',
            'live_use_vvc',
            'enter_pc_once',
            '__live_version__',
            '__druidClientInfo',
            'dy_swidth',
            'dy_sheight',
            'is_dash_user',
            'xgplayer_user_id',
        ]

        # 移动端 Cookie 特征
        mobile_features = [
            'multi_sids',
            'odin_tt',  # 注意：Web 端也有 odin_tt，但格式可能不同
            'passport_assist_user',
            'n_mh',
            'sid_guard',
            'uid_tt',
            'uid_tt_ss',
            'sid_tt',
            'sessionid',
            'sessionid_ss',
            'session_tlb_tag',
        ]

        # 检查 Cookie 类型
        has_web_features = any(
            feature in cookie_str for feature in web_features)
        has_mobile_features = any(
            feature in cookie_str for feature in mobile_features)

        # 如果同时包含两种特征，都使用同一个 Cookie
        # 如果只包含一种特征，只用于对应端
        # 如果都不包含，默认用于 Web 端（因为用户提供的示例是 Web 端）

        if has_web_features and has_mobile_features:
            # 同时包含两种特征，都使用
            return cookie_str, cookie_str
        elif has_web_features:
            # 只包含 Web 端特征
            return "", cookie_str
        elif has_mobile_features:
            # 只包含移动端特征
            return cookie_str, ""
        else:
            # 都不包含，默认用于 Web 端
            return "", cookie_str

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
        """
        try:
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
                self.log(f"[缓存] rank={rank} nickname={nickname} 二维码已存在，跳过下载")
                return

            # 保存二维码
            if qr_url:
                # 从 URL 下载图片，重试2次
                max_retries = 2
                retry_count = 0
                success = False
                while retry_count <= max_retries and not success:
                    try:
                        resp = requests.get(qr_url, timeout=30, verify=False)
                        resp.raise_for_status()
                        png_path.write_bytes(resp.content)
                        self.log(
                            f"[保存] rank={rank} nickname={nickname} 二维码已保存: {png_path}")
                        success = True
                    except Exception as e:
                        retry_count += 1
                        if retry_count <= max_retries:
                            self.log(
                                f"[保存失败] rank={rank} nickname={nickname} URL下载失败，重试 {retry_count}/{max_retries}: {e}")
                        else:
                            self.log(
                                f"[保存失败] rank={rank} nickname={nickname} URL下载失败，已重试 {max_retries} 次: {e}")
            elif qr_base64:
                # 将 base64 解码为图片并保存
                try:
                    # 解码 base64 数据
                    img_data = base64.b64decode(qr_base64)
                    # 保存为 PNG 图片
                    png_path.write_bytes(img_data)
                    self.log(
                        f"[保存] rank={rank} nickname={nickname} 二维码(base64转图片)已保存: {png_path}")
                except Exception as e:
                    self.log(
                        f"[保存失败] rank={rank} nickname={nickname} base64解码失败: {e}")
        except Exception as e:
            self.log(f"[保存失败] rank={rank} nickname={nickname} 保存失败: {e}")

    # 开始任务
    def start_task(self):
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

        api_base = self.api_base.get().rstrip("/")
        rank_type = "1"  # 固定使用本周榜

        # 获取用户输入的 Cookie 并自动拆分
        cookie_input = self.cookie_input.get().strip()
        cookie_subscribe, cookie_web = self.split_cookie(cookie_input)

        if cookie_input:
            if cookie_subscribe and cookie_web:
                self.log(f"检测到 C 同时适用")
            elif cookie_subscribe:
                self.log(f"检测到m c，将用于 s")
            elif cookie_web:
                self.log(f"检测到 w c，将用于 q u")
        else:
            self.log("未输入 Cookie，将使用默认 Cookie")

        threading.Thread(
            target=self.run_workflow,
            args=(api_base, rank_type, url_list, cookie_subscribe, cookie_web),
            daemon=True
        ).start()

    def start_polling(self):
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
        self.log(f"开始定时轮询，间隔 {interval} 秒")
        
        # 启动轮询线程
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
        api_base = self.api_base.get().rstrip("/")
        rank_type = "1"  # 固定使用本周榜
        
        # 获取用户输入的 Cookie 并自动拆分
        cookie_input = self.cookie_input.get().strip()
        cookie_subscribe, cookie_web = self.split_cookie(cookie_input)
        
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
                    self.log("检测到本地缓存，使用缓存的 author_id，跳过 userinfo 请求")
                elif round_count > 1:
                    self.log("使用缓存的 author_id，跳过 userinfo 请求")
            
            # 执行一次完整的任务流程
            self.run_workflow(api_base, rank_type, url_list, cookie_subscribe, cookie_web, skip_userinfo=skip_userinfo)
            
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

    def run_workflow(self, api_base: str, rank_type: str, url_list: list[str], cookie_subscribe: str, cookie_web: str, skip_userinfo: bool = False):
        # 并发处理每个链接（单个链接内部仍串行）
        max_workers = max(1, min(self.max_workers.get(), 20))
        
        # 检查缓存情况
        cached_count = sum(1 for url in url_list if url in self.url_to_author_id)
        if cached_count > 0:
            self.log(f"检测到 {cached_count}/{len(url_list)} 个链接有缓存，将优先使用缓存")
        
        if skip_userinfo:
            self.log(f"开始处理 {len(url_list)} 个链接（轮询模式，跳过 userinfo 请求），最大并发 {max_workers}")
        else:
            self.log(f"开始处理 {len(url_list)} 个链接，最大并发 {max_workers}")

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
                    self.log(f"[警告] URL {user_url} 在缓存中不存在，但要求跳过 userinfo 请求")
                
                futures.append(
                    executor.submit(self.process_single_url, idx, user_url,
                                    api_base, rank_type, cookie_subscribe, cookie_web,
                                    cached_author_id, cached_author_nickname)
                )

            for _ in as_completed(futures):
                # 结果已在 process_single_url 中记录日志
                pass

        if self.is_polling:
            self.log("本轮处理完毕。\n")
        else:
            self.log("全部链接处理完毕。\n")

    def process_single_url(self, idx: int, user_url: str, api_base: str, rank_type: str, cookie_subscribe: str, cookie_web: str, cached_author_id: str = None, cached_author_nickname: str = None):
        self.log(f"------ 开始处理第 {idx} 个链接 ------")
        self.log(f"输入 URL: {user_url}")

        # 1) 调用 userinfo（如果提供了缓存的 author_id，则跳过）
        if cached_author_id and cached_author_nickname:
            author_id = cached_author_id
            author_nickname = cached_author_nickname
            self.log(f"[用户信息] 使用缓存的 author_id={author_id}, 博主昵称={author_nickname}（跳过 userinfo 请求）")
        else:
            userinfo_url = f"{api_base}/userinfo"
            try:
                params = {"url": user_url}
                if cookie_web:
                    params["cookie_web"] = cookie_web
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
            author_nickname = user_data.get("data", {}).get("nickname", "unknown")
            self.log(f"[用户信息] author_id={author_id}, 博主昵称={author_nickname}")
            print(f"[用户信息] author_id={author_id}")

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
        subscribe_url = f"{api_base}/subscribe"
        try:
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
        self.log(f"[榜单] 获取到 {len(rank_list)} 条榜单数据")
        print(f"[榜单] 获取到 {len(rank_list)} 条榜单数据")

        # 3) 遍历 rank_list 调用 qrcode_url（并发执行，减少长队列等待）
        qrcode_url_api = f"{api_base}/qrcode_url"
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
                    f"[缓存] rank={rank_no} nickname={nickname} 二维码已存在，跳过请求")
                return

            # 请求 qrcode_url 接口，重试2次
            max_retries = 2
            retry_count = 0
            qr_data = None
            while retry_count <= max_retries and qr_data is None:
                try:
                    params = {"sec_user_id": sec_uid}
                    if cookie_web:
                        params["cookie_web"] = cookie_web
                    resp_qr = requests.get(
                        qrcode_url_api,
                        params=params,
                        timeout=30,
                        verify=False,
                    )
                    qr_data = resp_qr.json()
                except Exception as e:
                    retry_count += 1
                    if retry_count <= max_retries:
                        self.log(
                            f"[qrcode_url] 请求失败 sec_uid={sec_uid}，重试 {retry_count}/{max_retries}: {e}")
                    else:
                        self.log(
                            f"[qrcode_url] 请求失败 sec_uid={sec_uid}，已重试 {max_retries} 次: {e}")
                        return
            
            if qr_data is None:
                return
            
            # 从 qrcode_url 接口获取完整的 nickname
            full_nickname = qr_data.get("user", {}).get("nickname") if isinstance(qr_data, dict) else None
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
                    f"[qrcode_url] rank={rank_no} nickname={display_nickname} sec_uid={sec_uid} 二维码链接: {qr_url}")
                # 保存二维码，使用完整的 nickname
                self.save_qrcode(author_nickname, rank_no or 0,
                                 display_nickname, qr_url=qr_url)
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
                                f"[qrcode_url] rank={rank_no} nickname={display_nickname} sec_uid={sec_uid} 二维码base64(前50字符): {qr_preview}...")
                            # 保存二维码 base64，使用完整的 nickname
                            self.save_qrcode(
                                author_nickname, rank_no or 0, display_nickname, qr_base64=qr_base64)
                        except Exception as gen_e:
                            gen_retry_count += 1
                            if gen_retry_count <= max_gen_retries:
                                self.log(
                                    f"[qrcode_url] rank={rank_no} nickname={display_nickname} sec_uid={sec_uid} 生成二维码失败，重试 {gen_retry_count}/{max_gen_retries}: {gen_e}")
                            else:
                                self.log(
                                    f"[qrcode_url] rank={rank_no} nickname={display_nickname} sec_uid={sec_uid} 生成二维码失败，已重试 {max_gen_retries} 次: {gen_e}")
                else:
                    self.log(
                        f"[qrcode_url] rank={rank_no} nickname={display_nickname} sec_uid={sec_uid} 未返回二维码链接和share_url，原始字段: {qr_obj}")

        with ThreadPoolExecutor(max_workers=max_rank_workers) as inner_executor:
            for item in rank_list:
                inner_executor.submit(fetch_qr, item)

        self.log(f"------ 完成第 {idx} 个链接 ------\n")


def main():
    root = ttk.Window(themename="litera")
    app = DouyinGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
