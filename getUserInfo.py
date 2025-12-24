from flask import Flask, request, jsonify
import re
import requests
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# ====== 配置区 ======
# 替换为你自己的有效 Cookie（从浏览器复制）
COOKIE = "hevc_supported=true; UIFID=973a3fd64dcc46a3490fd9b60d4a8e663b34df4ccc4bbcf97643172fb712d8b0af849bef1014ced93a67391f3e94eae8588e1b42ddf55a3e0acc3751436ace3927fc8c79ec49eec532867b9efbb5b62248d0d42a592d66a69ecbbd5bc6d01b3588badf404161dab873d63372c77881fb0dc4687687a5104e127ead6325556c7848b40c01004032a34f26dfad472b9845195d68854193bced0b6331fa306a7904; bd_ticket_guard_client_web_domain=2; store-region=cn-gz; store-region-src=uid; SelfTabRedDotControl=%5B%5D; my_rd=2; SEARCH_RESULT_LIST_TYPE=%22single%22; xgplayer_device_id=28551481219; live_use_vvc=%22false%22; theme=%22light%22; enter_pc_once=1; fpk1=U2FsdGVkX19tVdrXolUdD7WijZtWBytYvCmzt4vOKYMMdW6u8QUfjMiJR61kMeCmNQb8MdOCnw9nJtxD3UAHwQ==; fpk2=a3f57bbe21c4e30379228ad7788f224d; __live_version__=%221.1.4.539%22; __druidClientInfo=JTdCJTIyY2xpZW50V2lkdGglMjIlM0ExMzc2JTJDJTIyY2xpZW50SGVpZ2h0JTIyJTNBNjc0JTJDJTIyd2lkdGglMjIlM0ExMzc2JTJDJTIyaGVpZ2h0JTIyJTNBNjc0JTJDJTIyZGV2aWNlUGl4ZWxSYXRpbyUyMiUzQTEuMjUlMkMlMjJ1c2VyQWdlbnQlMjIlM0ElMjJNb3ppbGxhJTJGNS4wJTIwKFdpbmRvd3MlMjBOVCUyMDEwLjAlM0IlMjBXaW42NCUzQiUyMHg2NCklMjBBcHBsZVdlYktpdCUyRjUzNy4zNiUyMChLSFRNTCUyQyUyMGxpa2UlMjBHZWNrbyklMjBDaHJvbWUlMkYxNDAuMC4wLjAlMjBTYWZhcmklMkY1MzcuMzYlMjIlN0Q=; passport_csrf_token=6d4478db894a507fa53c9e9fe0473b37; passport_csrf_token_default=6d4478db894a507fa53c9e9fe0473b37; dy_swidth=1536; dy_sheight=864; is_dash_user=1; xgplayer_user_id=82377755329; s_v_web_id=verify_mj2ias9d_egPq4j92_mihB_4V5s_9tlX_5njB62ldN8Fk; passport_mfa_token=CjdKBgTkUXDDmRwed12FR55eo5FqujnYdwEmF75MgG0moVbHUJIMku1L3HkAb2Va3O6vu0WQRLx0GkoKPAAAAAAAAAAAAABP0g6biwGh7J4NbJoN4U7F%2B5QoqEf6kVcDlqzgqOkhOfA3lWTars2W3OEsctlRP7B8vBDH%2B4MOGPax0WwgAiIBAzjvQpk%3D; d_ticket=37ebc73090fc101741276f13e1674e949ceca; n_mh=XPrGlncfCwvX48AijwWOz7NPclXMq_x49jQE-05HlAg; session_tlb_tag_bk=sttt%7C19%7CvE_AtpzHIG1x0qUDz4RNYv________-dLBcHY_H75Ldhos8yUd9hCngP1NJM54rAONzOXlvUr9A%3D; __security_server_data_status=1; __security_mc_1_s_sdk_crypt_sdk=cec82b4e-44bd-af6f; __security_mc_1_s_sdk_cert_key=0d7f4670-4c71-9e14; download_guide=%223%2F20251217%2F0%22; volume_info=%7B%22isUserMute%22%3Atrue%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.875%7D; __ac_nonce=0694a92b100c0fbd7d900; __ac_signature=_02B4Z6wo00f015YAtHQAAIDCJ-AKbIx2wEuWILDAAIzTc8; strategyABtestKey=%221766494919.293%22; is_staff_user=false; publish_badge_show_info=%220%2C0%2C0%2C1766494932201%22; gulu_source_res=eyJwX2luIjoiMzRlYjBiNWI5YTNlY2RkMjY3ZGQzOTBkNjhjMjk1MGIzMjY2YmUyMDc3MWViYmZlMTIzNDM4ZDMxZmNkYTVjOCJ9; feed_cache_data=%7B%22uuid%22%3A%2234384835224%22%2C%22scmVersion%22%3A%221.0.8.2024%22%2C%22date%22%3A1766495959826%2C%22dyQ%22%3A%221766495930%22%2C%22awemeId%22%3A%227575515727310884115%22%2C%22awemeInfoVersion%22%3A%223.0%22%7D; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A1%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a68605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277f6b5a666475273f2763646976602729277672715a646971273f27636469766027292771273f2734373c363c34333c3133333234272927676c715a75776a716a666a666c6a6b5a7666776c7571273f2763646976602778; bit_env=9kQlMfjpUO_iQttu2A3ZniKiYC7JPmuq7M0Mjs-6YaR03DtDmG8CqnUkQySoziLQSIS7rulCPl7HXereoh4FgcoLb-Es1ECvmXckWcx9maNEJ3pfnQY5XL0gjblrolVvMXJgOx8qGEB-7AWWXb-2Zkmt53UeqgtiArVodK4d9gDaZfPn_xGSebEYdzlUfyOxYaxpOYJXwfzhwpdgcwWH4OqcEpI53dfxwc_fKjWRfjrEE6VEe7FNtxsxzs8r6mX98fQuVH8nzICFkFDZTeTCw_CtsshvKlvSMI86xcMXre7Gxr3Rov-_bxdvqzxU-a0VSP-RwSb9VjH0HKf-4llbep-Nzrh8Uz4utjP2FcWjFc42eVkGzQNttF5cOw9bdg9SA-2Ey_LXAzFvJQ18lwsJ36vZIXkG6327TApHOfdu1vvseAnHukDTuTn7WXQFsNywhzFxXIKRJ1-i4i24Q9sM4hcE9yq3OCEnGzbdy-jBcU32RPv6aFOyxo7xK5ek8UUN; passport_auth_mix_state=4welyn97bw19fmmk52116p9g3s4dzyv9tljl9x2r3ud98o5a; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1536%2C%5C%22screen_height%5C%22%3A864%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A150%7D%22; ttwid=1%7C-FAWbE-c8cN-vq6Dx502LM41mDVSGMxsMDU1HaFM9rw%7C1766496310%7Cf2f3d3f82bb0de6368edbef180c9e5c586eb0836c2bf245d8175d1e704aa9593; passport_assist_user=CkEKzWgXNoMGl_27qzgahMW85Ro6WkFHi7C_6PVX7laEcVhXo9a9XC8g1yS5ag-QLvqTs_vAhuGhsAWeVM0GCDEZGRpKCjwAAAAAAAAAAAAAT90m9zRuWZH7CQXSejXuNSiIIdqrhFFHq_2VgTcQTf3xay0dV77p6qV9XdfC3Yupl0wQk_uEDhiJr9ZUIAEiAQMjjC2Q; sid_guard=0e7f2a8ef37cd0cc080bca6c1cb397cb%7C1766496312%7C5184000%7CSat%2C+21-Feb-2026+13%3A25%3A12+GMT; uid_tt=f6e70850789536affb4e1c4f0b005398; uid_tt_ss=f6e70850789536affb4e1c4f0b005398; sid_tt=0e7f2a8ef37cd0cc080bca6c1cb397cb; sessionid=0e7f2a8ef37cd0cc080bca6c1cb397cb; sessionid_ss=0e7f2a8ef37cd0cc080bca6c1cb397cb; session_tlb_tag=sttt%7C7%7CDn8qjvN80MwIC8psHLOXy__________PCMN93DUqd4eEo44Ma4FuR-YFMIphmuXIuAQUQsUbHH4%3D; sid_ucp_v1=1.0.0-KDUyZjk5YmU0ZmY0ZDA0NWQ1NWQwMjRkMmIxYzA4NGM2OGI1ZmEyNWEKIQjToPDdu6ziBxC4sKrKBhjvMSAMMKb27skGOAVA-wdIBBoCbHEiIDBlN2YyYThlZjM3Y2QwY2MwODBiY2E2YzFjYjM5N2Ni; ssid_ucp_v1=1.0.0-KDUyZjk5YmU0ZmY0ZDA0NWQ1NWQwMjRkMmIxYzA4NGM2OGI1ZmEyNWEKIQjToPDdu6ziBxC4sKrKBhjvMSAMMKb27skGOAVA-wdIBBoCbHEiIDBlN2YyYThlZjM3Y2QwY2MwODBiY2E2YzFjYjM5N2Ni; __security_mc_1_s_sdk_sign_data_key_web_protect=f6352649-45cc-adb6; login_time=1766496325194; biz_trace_id=fb9041f6; _bd_ticket_crypt_cookie=1188bc8c0188b21e7961573f3fc4496c; IsDouyinActive=false; home_can_add_dy_2_desktop=%220%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSkJ1THFNZmxFYmVqa1hTbGU5bE5DcnpYTHkxcDd3dmRoQ1hFejJERWFLc01Lc3pGdWJ4TkpOa2Q3OHN3M3A5QVkyK3NPVTVGUTlkSHE4cHdCZGtUZ0E9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJKQnVMcU1mbEViZWprWFNsZTlsTkNyelhMeTFwN3d2ZGhDWEV6MkRFYUtzTUtzekZ1YnhOSk5rZDc4c3czcDlBWTIrc09VNUZROWRIcThwd0Jka1RnQT0iLCJ0c19zaWduIjoidHMuMi45ODVkZTNmNGQwZmI1YTEzYWQ3ODhjMDE2NzNkZDc4OTM3NzEzMjllODYyMWQ2MzFmYWZhNzRiNjFiZjQ2MDlmYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJhSlJGT05zVmV0OU1EOXpUK3V3TE1iU1NQUzduS3BTTGdEaG5LRG1sN2kwPSIsInNlY190cyI6IiM1TXhucDduS0VDcDkwWnE1dStjc1h3bDRTKzJVRlY2bEFMQTV0WGxwOTJxZ0xxMFJDQTl3SHNKcnl0QU0ifQ%3D%3D; odin_tt=fda1c2e005adadfa0a508b99b6331817713d8e67b7e3b22b1d5c7a218b3a908db6abdc76a08098afdce9636473efb2d0c8bc41777ae49aef4e8b318c73aa24e3831dde1e1fc01dc1ede654f93945fc3c"

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "cache-control": "no-cache",
    "origin": "https://www.douyin.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "x-secsdk-csrf-token": "DOWNGRADE"
}




def get_sec_user_id(url: str) -> str:
    """从 URL 中提取 sec_user_id"""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if 'sec_uid' in query:
        return query['sec_uid'][0]

    # 尝试从路径 /user/xxx 提取
    path = parsed.path
    if '/user/' in path:
        user_part = path.split('/user/')[-1].split('?')[0]
        return user_part

    return None


def resolve_redirect(url: str) -> str:
    """解析 v.douyin.com 短链接，返回最终 URL"""
    try:
        resp = requests.head(url, allow_redirects=True, timeout=10)
        return resp.url
    except Exception as e:
        print(f"Redirect resolve error: {e}")
        return url


def fetch_user_info(sec_user_id: str):
    """调用抖音接口获取用户信息"""
    api_url = "https://www.douyin.com/aweme/v1/web/im/user/info/"
    data = f'sec_user_ids=["{sec_user_id}"]'
    headers = HEADERS.copy()
    headers["cookie"] = COOKIE
    headers["referer"] = f"https://www.douyin.com/user/{sec_user_id}?showTab=like"

    try:
        resp = requests.post(api_url, data=data, headers=headers, timeout=10)
        result = resp.json()
        if result.get("status_code") != 0:
            return None, "API 返回错误"
        user = result["data"][0]
        return {
            "id": sec_user_id,
            "nickname": user.get("nickname"),
            "enterprise_verify_reason": user.get("enterprise_verify_reason", ""),
            "author_id": user.get("uid"),
            "unique_id": user.get("unique_id"),
            "avatar": user["avatar_thumb"]["url_list"][0],
            "avatar_small": user["avatar_small"]["url_list"][0],
            "short_id": user.get("short_id", ""),
            "signature": user.get("signature", "")
        }, None
    except Exception as e:
        return None, str(e)


@app.route('/userinfo', methods=['GET'])
def userinfo():
    url_or_id = request.args.get('url') or request.args.get('id')
    if not url_or_id:
        return jsonify({"code": 400, "msg": "缺少参数 url 或 id"}), 400

    # 解码 URL（兼容前端 encodeURI）
    import urllib.parse
    url_or_id = urllib.parse.unquote(url_or_id)

    # 判断是否是 URL
    if url_or_id.startswith(('http://', 'https://')):
        if 'v.douyin.com' in url_or_id:
            final_url = resolve_redirect(url_or_id)
        else:
            final_url = url_or_id
        sec_user_id = get_sec_user_id(final_url)
    else:
        sec_user_id = url_or_id.strip()

    if not sec_user_id:
        return jsonify({"code": 400, "msg": "无法提取有效的 sec_user_id"}), 400

    user_info, error = fetch_user_info(sec_user_id)
    if error:
        return jsonify({"code": 500, "msg": f"请求失败: {error}"}), 500

    return jsonify({
        "code": 200,
        "msg": "解析成功",
        "sec_uid": sec_user_id,
        "data": user_info
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)