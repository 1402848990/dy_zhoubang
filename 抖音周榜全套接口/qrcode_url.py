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
COOKIE = "hevc_supported=true; UIFID=973a3fd64dcc46a3490fd9b60d4a8e663b34df4ccc4bbcf97643172fb712d8b0af849bef1014ced93a67391f3e94eae8588e1b42ddf55a3e0acc3751436ace3927fc8c79ec49eec532867b9efbb5b62248d0d42a592d66a69ecbbd5bc6d01b3588badf404161dab873d63372c77881fb0dc4687687a5104e127ead6325556c7848b40c01004032a34f26dfad472b9845195d68854193bced0b6331fa306a7904; bd_ticket_guard_client_web_domain=2; store-region=cn-gz; store-region-src=uid; SelfTabRedDotControl=%5B%5D; my_rd=2; SEARCH_RESULT_LIST_TYPE=%22single%22; xgplayer_device_id=28551481219; live_use_vvc=%22false%22; theme=%22light%22; enter_pc_once=1; fpk1=U2FsdGVkX19tVdrXolUdD7WijZtWBytYvCmzt4vOKYMMdW6u8QUfjMiJR61kMeCmNQb8MdOCnw9nJtxD3UAHwQ==; fpk2=a3f57bbe21c4e30379228ad7788f224d; __live_version__=%221.1.4.539%22; __druidClientInfo=JTdCJTIyY2xpZW50V2lkdGglMjIlM0ExMzc2JTJDJTIyY2xpZW50SGVpZ2h0JTIyJTNBNjc0JTJDJTIyd2lkdGglMjIlM0ExMzc2JTJDJTIyaGVpZ2h0JTIyJTNBNjc0JTJDJTIyZGV2aWNlUGl4ZWxSYXRpbyUyMiUzQTEuMjUlMkMlMjJ1c2VyQWdlbnQlMjIlM0ElMjJNb3ppbGxhJTJGNS4wJTIwKFdpbmRvd3MlMjBOVCUyMDEwLjAlM0IlMjBXaW42NCUzQiUyMHg2NCklMjBBcHBsZVdlYktpdCUyRjUzNy4zNiUyMChLSFRNTCUyQyUyMGxpa2UlMjBHZWNrbyklMjBDaHJvbWUlMkYxNDAuMC4wLjAlMjBTYWZhcmklMkY1MzcuMzYlMjIlN0Q=; passport_csrf_token=6d4478db894a507fa53c9e9fe0473b37; passport_csrf_token_default=6d4478db894a507fa53c9e9fe0473b37; dy_swidth=1536; dy_sheight=864; is_dash_user=1; xgplayer_user_id=82377755329; s_v_web_id=verify_mj2ias9d_egPq4j92_mihB_4V5s_9tlX_5njB62ldN8Fk; passport_mfa_token=CjdKBgTkUXDDmRwed12FR55eo5FqujnYdwEmF75MgG0moVbHUJIMku1L3HkAb2Va3O6vu0WQRLx0GkoKPAAAAAAAAAAAAABP0g6biwGh7J4NbJoN4U7F%2B5QoqEf6kVcDlqzgqOkhOfA3lWTars2W3OEsctlRP7B8vBDH%2B4MOGPax0WwgAiIBAzjvQpk%3D; d_ticket=37ebc73090fc101741276f13e1674e949ceca; n_mh=XPrGlncfCwvX48AijwWOz7NPclXMq_x49jQE-05HlAg; session_tlb_tag_bk=sttt%7C19%7CvE_AtpzHIG1x0qUDz4RNYv________-dLBcHY_H75Ldhos8yUd9hCngP1NJM54rAONzOXlvUr9A%3D; __security_server_data_status=1; __security_mc_1_s_sdk_crypt_sdk=cec82b4e-44bd-af6f; __security_mc_1_s_sdk_cert_key=0d7f4670-4c71-9e14; download_guide=%223%2F20251217%2F0%22; volume_info=%7B%22isUserMute%22%3Atrue%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.875%7D; strategyABtestKey=%221766494919.293%22; is_staff_user=false; publish_badge_show_info=%220%2C0%2C0%2C1766494932201%22; feed_cache_data=%7B%22uuid%22%3A%2234384835224%22%2C%22scmVersion%22%3A%221.0.8.2024%22%2C%22date%22%3A1766495959826%2C%22dyQ%22%3A%221766495930%22%2C%22awemeId%22%3A%227575515727310884115%22%2C%22awemeInfoVersion%22%3A%223.0%22%7D; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A1%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; ttwid=1%7C-FAWbE-c8cN-vq6Dx502LM41mDVSGMxsMDU1HaFM9rw%7C1766496310%7Cf2f3d3f82bb0de6368edbef180c9e5c586eb0836c2bf245d8175d1e704aa9593; passport_assist_user=CkEKzWgXNoMGl_27qzgahMW85Ro6WkFHi7C_6PVX7laEcVhXo9a9XC8g1yS5ag-QLvqTs_vAhuGhsAWeVM0GCDEZGRpKCjwAAAAAAAAAAAAAT90m9zRuWZH7CQXSejXuNSiIIdqrhFFHq_2VgTcQTf3xay0dV77p6qV9XdfC3Yupl0wQk_uEDhiJr9ZUIAEiAQMjjC2Q; sid_guard=0e7f2a8ef37cd0cc080bca6c1cb397cb%7C1766496312%7C5184000%7CSat%2C+21-Feb-2026+13%3A25%3A12+GMT; uid_tt=f6e70850789536affb4e1c4f0b005398; uid_tt_ss=f6e70850789536affb4e1c4f0b005398; sid_tt=0e7f2a8ef37cd0cc080bca6c1cb397cb; sessionid=0e7f2a8ef37cd0cc080bca6c1cb397cb; sessionid_ss=0e7f2a8ef37cd0cc080bca6c1cb397cb; session_tlb_tag=sttt%7C7%7CDn8qjvN80MwIC8psHLOXy__________PCMN93DUqd4eEo44Ma4FuR-YFMIphmuXIuAQUQsUbHH4%3D; sid_ucp_v1=1.0.0-KDUyZjk5YmU0ZmY0ZDA0NWQ1NWQwMjRkMmIxYzA4NGM2OGI1ZmEyNWEKIQjToPDdu6ziBxC4sKrKBhjvMSAMMKb27skGOAVA-wdIBBoCbHEiIDBlN2YyYThlZjM3Y2QwY2MwODBiY2E2YzFjYjM5N2Ni; ssid_ucp_v1=1.0.0-KDUyZjk5YmU0ZmY0ZDA0NWQ1NWQwMjRkMmIxYzA4NGM2OGI1ZmEyNWEKIQjToPDdu6ziBxC4sKrKBhjvMSAMMKb27skGOAVA-wdIBBoCbHEiIDBlN2YyYThlZjM3Y2QwY2MwODBiY2E2YzFjYjM5N2Ni; __security_mc_1_s_sdk_sign_data_key_web_protect=f6352649-45cc-adb6; login_time=1766496325194; _bd_ticket_crypt_cookie=1188bc8c0188b21e7961573f3fc4496c; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSkJ1THFNZmxFYmVqa1hTbGU5bE5DcnpYTHkxcDd3dmRoQ1hFejJERWFLc01Lc3pGdWJ4TkpOa2Q3OHN3M3A5QVkyK3NPVTVGUTlkSHE4cHdCZGtUZ0E9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; biz_trace_id=ea780aa3; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f273d303337303d36353033333234272927676c715a75776a716a666a69273f2763646976602778; bit_env=Jgo-CcBBsx9JcFWdG8uAdpoav5SYFnX8aWcFoOw-Kj3vD-9xgkddN9oErmN-myoCalGz77Z8OJRKwOgMWfDIEiNx9fLLsZS5E9VLgnhwny5WyWcQpA7sHAr6ZIPBfP3Dr0O12qOs-17QOJZs5_xcoUoOf2Ns1iS2NjtzHRySgkPwVoNNISppQWpPH1XRiYaYyVOpAfJeZaZklE1lRLJovd_9LiApjN6TgTzVTe6iD_00vuWJqXtB6mwjYVpF9k1QjyzWtVJwuF1ds2XmGhW9gxlaoSnr9lQNTiI4qgTXXNBdwPWx1J6iaYuXrfbGPy8JhFyUxgRJryAzAb3ti5uHcbar1TAzrFQAF6wtd_kM9I_Z2tELsVnTFVfU-4Dk8oukOWP9FwJPQGobjKBqT-Hd72J1xO6FoY-J7Q59Zu83Cil9HhZco7V4SIZygUs3X6Y0WjdWBWxYui5acZHBDCJPd3zolknmVkedsB2Nti2sNfgzjIxCKI4Ut-GfiGmsJAiV; gulu_source_res=eyJwX2luIjoiMzRlYjBiNWI5YTNlY2RkMjY3ZGQzOTBkNjhjMjk1MGIzMjY2YmUyMDc3MWViYmZlMTIzNDM4ZDMxZmNkYTVjOCJ9; passport_auth_mix_state=cw2pn44gfoekrz73iknznwonm0j21zr9; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJKQnVMcU1mbEViZWprWFNsZTlsTkNyelhMeTFwN3d2ZGhDWEV6MkRFYUtzTUtzekZ1YnhOSk5rZDc4c3czcDlBWTIrc09VNUZROWRIcThwd0Jka1RnQT0iLCJ0c19zaWduIjoidHMuMi45ODVkZTNmNGQwZmI1YTEzYWQ3ODhjMDE2NzNkZDc4OTM3NzEzMjllODYyMWQ2MzFmYWZhNzRiNjFiZjQ2MDlmYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJOZzRITTZ1bmt3Nzc3ZmRudXA3Wk9scmRQaVM2aW1XNDk0S051R2hYR3BFPSIsInNlY190cyI6IiNDcnVtbUt3di82eGRqMDhhamJPWkNpN21leE5za3B6RVdhZ3BCbTF5Z1h2cXVtWkpDU2xJemxQM0dKNVAifQ%3D%3D; __ac_nonce=0694ab5de00b6b936e8fc; __ac_signature=_02B4Z6wo00f01neAcwwAAIDDxmDNF24xgsJ3oHeAAPS5fa; IsDouyinActive=true; home_can_add_dy_2_desktop=%220%22; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1536%2C%5C%22screen_height%5C%22%3A864%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A150%7D%22; odin_tt=f801ec2c1e9cf82761e9a44d880e9939c9e34ba143f833abcb5bc48e5f2d19c3f084a84f4c58c88fc6b5549793490341dd55a60d27c7a6bfca0547328c5625b2"


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


@app.route('/qrcode_url.py', methods=['GET', 'POST', 'OPTIONS'])
def qrcode_url():
    """
    处理二维码 URL 请求
    """
    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        return '', 200
    
    # 获取请求参数
    sec_user_id = request.args.get('sec_user_id', 'MS4wLjABAAAAKE9hcXbTu7QWueiSlhQc4fuU5l48cjFaCYnXtRPV9Fc').strip()
    
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

