from flask_cors import CORS
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
CORS(app)

# 🔑 直接使用你提供的成功 URL（不要修改任何参数！）
SUCCESS_URL = 'https://webcast26-normal-c-lq.amemv.com/webcast/subscribe/get_contribute_ranklist/?offset=0&count=20&rank_kind=2&author_id=1805844061108371&rank_type=1&live_request_from_jsb=1&webcast_sdk_version=4120&live_sdk_version=370101&gamecp_sdk_version=4120&webcast_language=zh&webcast_locale=zh_CN&webcast_gps_access=1&current_network_quality_info=%7B%22http_rtt%22%3A220%2C%22tcp_rtt%22%3A22%2C%22quic_rtt%22%3A22%2C%22downstream_throughput_kbps%22%3A51574%2C%22net_effective_connection_type%22%3A4%2C%22video_download_speed%22%3A8671%2C%22quic_receive_loss_rate%22%3A-1%2C%22quic_send_loss_rate%22%3A-1%7D&device_score=8.6459&address_book_access=2&user_id=4229184618762131&is_pad=false&is_android_pad=0&is_landscape=false&carrier_region=CN&sec_user_id=MS4wLjABAAAAVD5P6sSrk63XzjJT2n_3SQTzfg6xeHZEtY8q-gOoRaIdWQe1GVc14zkfspecr6YY&sec_author_id=MS4wLjABAAAAQRDbTKq61_DJ9hERWfudv8om5slFVfduB286CRdcnUg&klink_egdi=AAJyNSLZjdt16GBbCmj2905_two1IjVuFtSExcGXQT7r8NFKy0zS1ytB&iid=326986953398496&device_id=4135726972408180&ac=wifi&channel=xiaomi_2329_64_1104&aid=2329&app_name=douyin_lite&version_code=370100&version_name=37.1.0&device_platform=android&os=android&ssmix=a&device_type=M2012K10C&device_brand=Redmi&language=zh&os_api=33&os_version=13&manifest_version_code=370101&resolution=1080*2272&dpi=440&update_version_code=37109900&_rticket=1766413689931&package=com.ss.android.ugc.aweme.lite&gold_container=0&first_launch_timestamp=1757849569&last_deeplink_update_version_code=0&cpu_support64=true&host_abi=arm64-v8a&is_guest_mode=0&app_type=normal&minor_status=0&appTheme=light&is_preinstall=0&need_personal_recommend=1&is_android_fold=0&ts=1766413690&cdid=a4069695-e8a5-4cc8-aa4d-8c2350dc0b7d&md=0'

# 必须包含的 Headers（从 PHP cURL 中提取）
HEADERS = {
    "User-Agent": "com.ss.android.ugc.aweme.lite/370101 (Linux; U; Android 13; zh_CN; M2012K10C; Build/TP1A.220624.014; Cronet/TTNetVersion:6f1e308d 2025-12-08 QuicVersion:21ac1950 2025-11-18)",
    "x-security-argus": "BridgeNetworkRequest/unknown aid/2329/xiaomi_2329_64_1104/Android/37.1.0/lynx/-1 https://lf-webcast-gr-sourcecdn.bytegecko.com/obj/byte-gurd-source-gr/webcast/mono/lynx/vip_common_douyin/pages/vip_rank_list/template.js",
    "hybrid-app-engine": "lynx",
    "activity_now_client": "1766413692074",
    "x-bd-kmsv": "1",
    "bd-ticket-guard-display-os-version": "TP1A.220624.014",
    "sdk-version": "2",
    "bd-ticket-guard-version": "3",
    "bd-ticket-guard-ree-public-key": "BNojMBo3PNc3TWOyeYcAHzvmnbxSTJtx1/LGkPGXYKTudq1i7qkaDpFnPWS8tazKMjFCnoOutR8ZB1XTCntiHdA=",
    "bd-ticket-guard-iteration-version": "3",
    "passport-sdk-version": "601431",
    "token-tlb-tag": "sttt|17|BJRtfCieQoLgFIF0bZEtdf_________Ltsv6uRGTP8v2Xp6GFjxsR8ZRk2kjiVHXYU8pM2OMxAE=",
    "x-vc-bdturing-sdk-version": "4.1.1.cn",
    "x-tt-store-region": "cn-gz",
    "x-tt-store-region-src": "uid",
    "x-tt-request-tag": "s=-1;p=0",
    "x-ss-dp": "2329",
    "Cookie": "passport_csrf_token=11465e03d160e14d14bb68427cfe8cd9; passport_csrf_token_default=11465e03d160e14d14bb68427cfe8cd9; multi_sids=4229184618762131%3A9de948c68d715b52c852329066720db9; odin_tt=0e565b50494782c846111c8a04a4f092a87221e65e1f648b3f0346f93484f6609d96b9868e5a317b856a3a0c2526c412f1f0793e773c82442b5a8a16961f67d237ecf773a3aac6140399ec4ad079d004; passport_assist_user=Ckuj8_nQce9mLEoRNnDAxpZe7dMp0txdRRb4sTKHX5vuaolZ_Ce0bubPNcpy4Qcn2Qk3kaYnM6OEd_IvjXQbVu4uqCwKUCI8OKoU6ycaSgo8AAAAAAAAAAAAAE_cBFaqe2m-fyzton93-5PznCLqYFuDLMisIbBgDvTyBOzYqQ4f00X3I2a3mfAyU1VHEIrxhA4Yia_WVCABIgEDmqWBFQ%3D%3D; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; sid_guard=9de948c68d715b52c852329066720db9%7C1766413603%7C5184000%7CFri%2C+20-Feb-2026+14%3A26%3A43+GMT; uid_tt=b233129ca4eaf42b86a4250a80fb1bed; uid_tt_ss=b233129ca4eaf42b86a4250a80fb1bed; sid_tt=9de948c68d715b52c852329066720db9; sessionid=9de948c68d715b52c852329066720db9; sessionid_ss=9de948c68d715b52c852329066720db9; session_tlb_tag=sttt%7C12%7CnelIxo1xW1LIUjKQZnINuf________-iC9AAOvyaasawFGoWteos_DMZ6ejz3-I7jx5f9VrTsl4%3D; is_staff_user=false; store-region=cn-gd; store-region-src=did; passport_csrf_token_default=11465e03d160e14d14bb68427cfe8cd9; multi_sids=4229184618762131%3A9de948c68d715b52c852329066720db9; odin_tt=0e565b50494782c846111c8a04a4f092a87221e65e1f648b3f0346f93484f6609d96b9868e5a317b856a3a0c2526c412f1f0793e773c82442b5a8a16961f67d237ecf773a3aac6140399ec4ad079d004; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; sid_guard=9de948c68d715b52c852329066720db9%7C1766413603%7C5184000%7CFri%2C+20-Feb-2026+14%3A26%3A43+GMT; uid_tt=b233129ca4eaf42b86a4250a80fb1bed; sid_tt=9de948c68d715b52c852329066720db9; sessionid=9de948c68d715b52c852329066720db9; is_staff_user=false; store-region=cn-gz; store-region-src=uid"
}


@app.route('/subscribe', methods=['GET'])
def get_ranklist():
    try:
        # 直接使用成功 URL（不拼接！）
        response = requests.get(
            SUCCESS_URL,
            headers=HEADERS,
            verify=False,  # 忽略 SSL（仅测试）
            timeout=10
        )

        # 调试：打印状态和前500字符
        print("Status Code:", response.status_code)
        print("Response Preview:", response.text[:500])

        # 尝试解析 JSON
        json_data = response.json()
        return jsonify(json_data.get('data', {}))

    except Exception as e:
        return jsonify({
            "error": str(e),
            "status_code": response.status_code if 'response' in locals() else None,
            "raw_response": response.text[:500] if 'response' in locals() else "No response"
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
