from flask import Flask, request, jsonify
import re
import requests
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# 全局 Cookie（注意：Cookie 有效期有限，需定期更新）
COOKIE_PC = "hevc_supported=true; UIFID=973a3fd64dcc46a3490fd9b60d4a8e663b34df4ccc4bbcf97643172fb712d8b0af849bef1014ced93a67391f3e94eae8588e1b42ddf55a3e0acc3751436ace3927fc8c79ec49eec532867b9efbb5b62248d0d42a592d66a69ecbbd5bc6d01b3588badf404161dab873d63372c77881fb0dc4687687a5104e127ead6325556c7848b40c01004032a34f26dfad472b9845195d68854193bced0b6331fa306a7904; ...（其余省略，保留你原始 cookie）"

COOKIE_MOBILE = 'passport_csrf_token=11465e03d160e14d14bb68427cfe8cd9; ...（其余省略）'

HEADERS_PC = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'uifid': '973a3fd64dcc46a3490fd9b60d4a8e663b34df4ccc4bbcf97643172fb712d8b0af849bef1014ced93a67391f3e94eae8588e1b42ddf55a3e0acc3751436ace3927fc8c79ec49eec532867b9efbb5b62248d0d42a592d66a69ecbbd5bc6d01b3588badf404161dab873d63372c77881fb0dc4687687a5104e127ead6325556c7848b40c01004032a34f26dfad472b9845195d68854193bced0b6331fa306a7904',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'zh-CN,zh;q=0.9',
    'priority': 'u=1, i',
}

HEADERS_MOBILE = {
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
}

def get_sec_user_id_from_url(url):
    """从抖音 URL 中提取 sec_user_id"""
    if not url:
        return None
    parsed = urlparse(url)
    if 'v.douyin.com' in parsed.netloc:
        # 短链重定向
        try:
            resp = requests.head(url, allow_redirects=True, timeout=10)
            url = resp.url
        except:
            return None
    # 尝试从 query 提取 sec_uid
    query = parse_qs(parsed.query)
    if 'sec_uid' in query:
        return query['sec_uid'][0]
    # 尝试从路径提取
    path_match = re.search(r'/user/([A-Za-z0-9_-]+)', url)
    if path_match:
        return path_match.group(1)
    return None

# ------------------ API 1: 用户主页信息 ------------------
@app.route('/api/user/profile')
def user_profile():
    sec_user_id = request.args.get('sec_user_id', '').strip()
    if not sec_user_id:
        return jsonify({"error": "Missing sec_user_id"}), 400

    url = (
        f"https://www.douyin.com/aweme/v1/web/user/profile/other/"
        f"?device_platform=webapp&aid=6383&channel=channel_pc_web&publish_video_strategy_type=2"
        f"&source=channel_pc_web&sec_user_id={sec_user_id}&personal_center_strategy=1"
        f"&profile_other_record_enable=1&land_to=1&update_version_code=170400&pc_client_type=1"
        f"&pc_libra_divert=Windows&support_h265=1&support_dash=1&cpu_core_num=12&version_code=170400"
        f"&version_name=17.4.0&cookie_enabled=true&screen_width=1536&screen_height=864"
        f"&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome"
        f"&browser_version=143.0.0.0&browser_online=true&engine_name=Blink&engine_version=143.0.0.0"
        f"&os_name=Windows&os_version=10&device_memory=8&platform=PC&downlink=10&effective_type=4g"
        f"&round_trip_time=150&webid=7498378399590024719"
    )

    headers = HEADERS_PC.copy()
    headers['cookie'] = COOKIE_PC
    headers['referer'] = f'https://www.douyin.com/user/{sec_user_id}'

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ API 2: 贡献榜 ------------------
@app.route('/api/user/ranklist')
def user_ranklist():
    author_id = request.args.get('author_id', '').strip()
    rank_type = request.args.get('rank_type', '1').strip()  # 1:本周 2:上周 3:今年

    if not author_id:
        return jsonify({"error": "Missing author_id"}), 400

    url = (
        f"https://webcast26-normal-c-lq.amemv.com/webcast/subscribe/get_contribute_ranklist/"
        f"?offset=0&count=20&rank_kind=2&author_id={author_id}&rank_type={rank_type}"
        f"&live_request_from_jsb=1&webcast_sdk_version=4120&live_sdk_version=370101"
        f"&gamecp_sdk_version=4120&webcast_language=zh&webcast_locale=zh_CN"
        f"&webcast_gps_access=1&current_network_quality_info=%7B%22http_rtt%22%3A220%2C%22tcp_rtt%22%3A22%2C%22quic_rtt%22%3A22%2C%22downstream_throughput_kbps%22%3A51574%2C%22net_effective_connection_type%22%3A4%2C%22video_download_speed%22%3A8671%2C%22quic_receive_loss_rate%22%3A-1%2C%22quic_send_loss_rate%22%3A-1%7D"
        f"&device_score=8.6459&address_book_access=2&user_id=4229184618762131&is_pad=false"
        f"&is_android_pad=0&is_landscape=false&carrier_region=CN"
        f"&sec_user_id=MS4wLjABAAAAVD5P6sSrk63XzjJT2n_3SQTzfg6xeHZEtY8q-gOoRaIdWQe1GVc14zkfspecr6YY"
        f"&sec_author_id=MS4wLjABAAAAQRDbTKq61_DJ9hERWfudv8om5slFVfduB286CRdcnUg"
        f"&klink_egdi=AAJyNSLZjdt16GBbCmj2905_two1IjVuFtSExcGXQT7r8NFKy0zS1ytB"
        f"&iid=326986953398496&device_id=4135726972408180&ac=wifi&channel=xiaomi_2329_64_1104"
        f"&aid=2329&app_name=douyin_lite&version_code=370100&version_name=37.1.0"
        f"&device_platform=android&os=android&ssmix=a&device_type=M2012K10C"
        f"&device_brand=Redmi&language=zh&os_api=33&os_version=13"
        f"&manifest_version_code=370101&resolution=1080*2272&dpi=440"
        f"&update_version_code=37109900&_rticket=1766413689931"
        f"&package=com.ss.android.ugc.aweme.lite&gold_container=0"
        f"&first_launch_timestamp=1757849569&last_deeplink_update_version_code=0"
        f"&cpu_support64=true&host_abi=arm64-v8a&is_guest_mode=0&app_type=normal"
        f"&minor_status=0&appTheme=light&is_preinstall=0&need_personal_recommend=1"
        f"&is_android_fold=0&ts=1766413690&cdid=a4069695-e8a5-4cc8-aa4d-8c2350dc0b7d&md=0"
    )

    headers = HEADERS_MOBILE.copy()
    headers['cookie'] = COOKIE_MOBILE

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        return jsonify(data.get('data', {}))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ API 3: 用户详细信息 ------------------
@app.route('/api/user/info')
def user_info():
    url_or_id = request.args.get('url') or request.args.get('id', '')
    sec_user_id = get_sec_user_id_from_url(url_or_id) or url_or_id.strip()

    if not sec_user_id:
        return jsonify({"error": "Invalid URL or ID"}), 400

    post_data = f'sec_user_ids=["{sec_user_id}"]'
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "origin": "https://www.douyin.com",
        "referer": f"https://www.douyin.com/user/{sec_user_id}?showTab=like",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "cookie": COOKIE_PC,
        "x-secsdk-csrf-token": "DOWNGRADE"
    }

    try:
        resp = requests.post(
            "https://www.douyin.com/aweme/v1/web/im/user/info/",
            data=post_data,
            headers=headers,
            timeout=10
        )
        result = resp.json()
        if not result.get('data'):
            return jsonify({"error": "User not found"}), 404

        item = result['data'][0]
        return jsonify({
            "code": 200,
            "msg": "解析成功",
            "sec_uid": sec_user_id,
            "data": {
                'id': sec_user_id,
                'nickname': item.get('nickname'),
                'enterprise_verify_reason': item.get('enterprise_verify_reason', ''),
                'author_id': item.get('uid'),
                'unique_id': item.get('unique_id'),
                'avatar': item.get('avatar_thumb', {}).get('url_list', [''])[0],
                'avatar_small': item.get('avatar_small', {}).get('url_list', [''])[0],
                'short_id': item.get('short_id'),
                'signature': item.get('signature'),
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ 启动 ------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)