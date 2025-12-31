#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
抖音用户信息查询
使用方法：
qrcode_url.py?sec_user_id=MS4wLjABAAAABBfmGuCLPobQCxEFBH7R7yCG94Gu19wQklcbTz6Q8Do

参数说明：
sec_user_id: 抖音用户sec_user_id
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)  # 允许所有来源的跨域请求

# Cookie 配置
COOKIE = "hevc_supported=true; __live_version__=%221.1.2.6176%22; live_use_vvc=%22false%22; enter_pc_once=1; passport_csrf_token=0b26ede85105c515a5b4fbcb65a52b6d; passport_csrf_token_default=0b26ede85105c515a5b4fbcb65a52b6d; bd_ticket_guard_client_web_domain=2; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; SEARCH_RESULT_LIST_TYPE=%22single%22; is_dash_user=1; SEARCH_UN_LOGIN_PV_CURR_DAY=%7B%22date%22%3A1766307748914%2C%22count%22%3A1%7D; passport_assist_user=CkCQlepd8gK75WsUuS-9VGWeoO30pBqIbqe2lOYA7IyJmD8jvDsalC41TOq3TywTbSBLj1lsrPLZbOrXQkwDtaxpGkoKPAAAAAAAAAAAAABP3ARWqntpvn8s7aJ_d_uT85wi6mBbgyzIrCGwYA708gTs2KkOH9NF9yNmt5nwMlNVRxDf8IQOGImv1lQgASIBAyNkr9Y%3D; n_mh=VOVHx91KKF_1NlJfn2x3GEYxBoWuVoca4GJNiWuS1No; sid_guard=90953c491ad4f59ddd1e36716267e787%7C1766408306%7C5184000%7CFri%2C+20-Feb-2026+12%3A58%3A26+GMT; uid_tt=dec9aa8d99264241d4f077cd37324834; uid_tt_ss=dec9aa8d99264241d4f077cd37324834; sid_tt=90953c491ad4f59ddd1e36716267e787; sessionid=90953c491ad4f59ddd1e36716267e787; sessionid_ss=90953c491ad4f59ddd1e36716267e787; session_tlb_tag=sttt%7C2%7CkJU8SRrU9Z3dHjZxYmfnh__________6-R0YUUWZuTeCqtpG-OGYBZn-sBZRJs3WyrjQKGg6SYA%3D; is_staff_user=false; sid_ucp_v1=1.0.0-KGQ1NmQyNTNlYWM2YTU2ZjQyZTk1YmMwMmM2NzAxMmI2YzA5N2YwODcKIAi9nLCTpfRFEPKApcoGGO8xIAww5c2U8QU4B0D0B0gEGgJsZiIgOTA5NTNjNDkxYWQ0ZjU5ZGRkMWUzNjcxNjI2N2U3ODc; ssid_ucp_v1=1.0.0-KGQ1NmQyNTNlYWM2YTU2ZjQyZTk1YmMwMmM2NzAxMmI2YzA5N2YwODcKIAi9nLCTpfRFEPKApcoGGO8xIAww5c2U8QU4B0D0B0gEGgJsZiIgOTA5NTNjNDkxYWQ0ZjU5ZGRkMWUzNjcxNjI2N2U3ODc; _bd_ticket_crypt_cookie=05c6fdb2acffab5d0ebd60c81db01115; __security_mc_1_s_sdk_sign_data_key_web_protect=3a0c5f5d-40a1-9d8a; __security_mc_1_s_sdk_cert_key=001a20d8-452b-89a3; __security_mc_1_s_sdk_crypt_sdk=4ed2115b-48c9-a7f4; __security_server_data_status=1; login_time=1766408311496; UIFID=e92777d2cb4cf0f94a981760c14554e8d3208daf0443679909dcdbe8e735b0617ff4d91647f82403cd4b0f15a3bdc9554733eff2438ed9042aa27cbc1b8331add2f1b5c2bb689833c02e7003167886afc5d0f4658d70a1d6cf0e0197956c7a904998ecc75f15bb511020314790430661d18379988fb148a201a6964dc6204c45eed3ed275f4e1537c7394ea6e6f4aaf360747e28685627ef1c12da7636e6d559; SelfTabRedDotControl=%5B%5D; publish_badge_show_info=%220%2C0%2C0%2C1766408318733%22; download_guide=%223%2F20251222%2F0%22; my_rd=2; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A2195%2C%5C%22screen_height%5C%22%3A1235%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A0%7D%22; strategyABtestKey=%221766739271.777%22; ttwid=1%7COOcZ0189cfvj_EQWojjwK__0J79Bc_8iB3zB--5gRd0%7C1766739264%7C2924d7758573170bcb4f764abb5c8b0597c2cc304cb42c65b7591bb146bcb48a; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAA-8Qj7oxba1TAj5cQIbHHvbtARRy3KlmvllNAc0VIxtU%2F1766764800000%2F0%2F1766739347464%2F0%22; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAA-8Qj7oxba1TAj5cQIbHHvbtARRy3KlmvllNAc0VIxtU%2F1766764800000%2F0%2F1766743301723%2F0%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSGp4U0dUWTRPaHBNc3JOcUFFMU9oRFczbkJsRjhMU2JGTkxGU014b0hpQXE4QnkxTTVzNFlRbmx1bFJiVHJ5ZCtDTXI4VGhQUnN1WFg1VmRSUWpRT009IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; home_can_add_dy_2_desktop=%221%22; odin_tt=dd008bdd3218cb72e2a8922915a1fd953781cd8abdb0e69fd112fd6e36ee4a09c0cb6c671f1172e719b3dca20afbeabe78e42312be32c503f4373ea867a7029b; biz_trace_id=5e3beac9; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f273634353137353c313233333234272927676c715a75776a716a666a69273f2763646976602778; bit_env=2EXMZAU6KsIV7THLjv78BTHZ7AuT081LKz3GcYtV7x06nXU3ICD1Yn9zx8mFtnlBe8Wrg1yzbF_OdET8oUYNd6P_ZkoF-M4nLmY36K06rWRfT82dZaO4soCmkKURvdaxVBAG01BDmtjdDrQ4SS-P4iHcavGnREcEXIvRR0LJ1cRIhgtv7tm-wU0xGOusrkooK05UtS9TK-rouSOxkRXHrr1jASilCC836xr20ztEZCP2C0XWDYwFLq4E9ijakfkfZVz4NGdrIzA5k6a0Eg4wSLSMw90ledA-W0t54DBUr6HfOfu8HvnHI4cj40cnJAoSrVLQKo0gv_-8iVRaARgxWzEVO7kyVpuM47ADfhliLRJCcAOnBEVoH-ujfUSA-Eg0zePZTSIPCRm7Sy0IxqOQIqgyU6mcinHalgioynCE2Eiwd2Dwb4gydOlT1VpsrosbdgkPMFmxGHynl9IhWt9UqVYdfXECKTNamG5L790zs1lGcwIgOgqcHP8OAgZ-8JXx; gulu_source_res=eyJwX2luIjoiMzRlYjBiNWI5YTNlY2RkMjY3ZGQzOTBkNjhjMjk1MGIzMjY2YmUyMDc3MWViYmZlMTIzNDM4ZDMxZmNkYTVjOCJ9; passport_auth_mix_state=n9imdppex07o21ry5evlxv5v0o1f5ar5ffrs6682ngkvdw6w; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJIanhTR1RZNE9ocE1zck5xQUUxT2hEVzNuQmxGOExTYkZOTEZTTXhvSGlBcThCeTFNNXM0WVFubHVsUmJUcnlkK0NNcjhUaFBSc3VYWDVWZFJRalFPTT0iLCJ0c19zaWduIjoidHMuMi44NzUzOTc2NDZhYTNhODdiMWQ3MWQzZjVhMmE1ZWQ0N2NmMmJjZWQxMjUxMDc5MjZkZjk1MjIwZGU3NmUwZTJkYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJ4Wmg2QUhXcG1pd0kvOHcvcnNxU1QzcFhHNGRtR0FaS1B1d2RGeTNhaE1JPSIsInNlY190cyI6IiNxT0FjUXNybmRqaEh4ZG5yMXgxZnpoVlZ3WGplQVlvNVl4SnZ5NzVZNEppaVo0TllvRVJJdktuU0xRMWUifQ%3D%3D; IsDouyinActive=true"


def make_request(url, cookie):
    """
    发送 HTTP 请求

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

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30,
            verify=False  # 关闭 SSL 验证，对应 PHP 中的 CURLOPT_SSL_VERIFYPEER => false
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f'Request Error: {str(e)}'


@app.route('/qrcode_url', methods=['GET', 'POST', 'OPTIONS'])
def qrcode_url():
    """
    处理二维码 URL 请求
    """
    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        return '', 200

    # 获取请求参数
    sec_user_id = request.args.get(
        'sec_user_id', 'MS4wLjABAAAAKE9hcXbTu7QWueiSlhQc4fuU5l48cjFaCYnXtRPV9Fc').strip()

    # 构建请求 URL
    url = f'https://www.douyin.com/aweme/v1/web/user/profile/other/?device_platform=webapp&aid=6383&channel=channel_pc_web&publish_video_strategy_type=2&source=channel_pc_web&sec_user_id={sec_user_id}&personal_center_strategy=1&profile_other_record_enable=1&land_to=1&update_version_code=170400&pc_client_type=1&pc_libra_divert=Windows&support_h265=1&support_dash=1&cpu_core_num=12&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1536&screen_height=864&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=143.0.0.0&browser_online=true&engine_name=Blink&engine_version=143.0.0.0&os_name=Windows&os_version=10&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=150&webid=7498378399590024719'

    # 发送请求
    response_text = make_request(url, COOKIE)

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


if __name__ == '__main__':
    # 禁用 SSL 警告（因为关闭了 SSL 验证）
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # 运行 Flask 应用
    app.run(host='0.0.0.0', port=5000, debug=False)





