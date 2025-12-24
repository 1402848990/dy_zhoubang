<?php

/**
 * 
 * 抖音用户信息查询
 *
 * 使用方法：
 * subscribe.php?author_id=1805844061108371&rank_type=3
 * 
 * 参数说明：
 * author_id: 抖音用户ID
 * rank_type: 排行类型 1:本周榜 2:上周榜 3:今年榜
 * 
 **/

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept');
header('Access-Control-Max-Age: 86400');
header('Content-Type: application/json; charset=utf-8');
// 关闭错误报告
error_reporting(0);

// 之前的cookie
// $cookie = 'passport_csrf_token=11465e03d160e14d14bb68427cfe8cd9; passport_csrf_token_default=11465e03d160e14d14bb68427cfe8cd9; multi_sids=4229184618762131%3A9de948c68d715b52c852329066720db9; odin_tt=0e565b50494782c846111c8a04a4f092a87221e65e1f648b3f0346f93484f6609d96b9868e5a317b856a3a0c2526c412f1f0793e773c82442b5a8a16961f67d237ecf773a3aac6140399ec4ad079d004; passport_assist_user=Ckuj8_nQce9mLEoRNnDAxpZe7dMp0txdRRb4sTKHX5vuaolZ_Ce0bubPNcpy4Qcn2Qk3kaYnM6OEd_IvjXQbVu4uqCwKUCI8OKoU6ycaSgo8AAAAAAAAAAAAAE_cBFaqe2m-fyzton93-5PznCLqYFuDLMisIbBgDvTyBOzYqQ4f00X3I2a3mfAyU1VHEIrxhA4Yia_WVCABIgEDmqWBFQ%3D%3D; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; sid_guard=9de948c68d715b52c852329066720db9%7C1766413603%7C5184000%7CFri%2C+20-Feb-2026+14%3A26%3A43+GMT; uid_tt=b233129ca4eaf42b86a4250a80fb1bed; uid_tt_ss=b233129ca4eaf42b86a4250a80fb1bed; sid_tt=9de948c68d715b52c852329066720db9; sessionid=9de948c68d715b52c852329066720db9; sessionid_ss=9de948c68d715b52c852329066720db9; session_tlb_tag=sttt%7C12%7CnelIxo1xW1LIUjKQZnINuf________-iC9AAOvyaasawFGoWteos_DMZ6ejz3-I7jx5f9VrTsl4%3D; is_staff_user=false; store-region=cn-gd; store-region-src=did; passport_csrf_token_default=11465e03d160e14d14bb68427cfe8cd9; multi_sids=4229184618762131%3A9de948c68d715b52c852329066720db9; odin_tt=0e565b50494782c846111c8a04a4f092a87221e65e1f648b3f0346f93484f6609d96b9868e5a317b856a3a0c2526c412f1f0793e773c82442b5a8a16961f67d237ecf773a3aac6140399ec4ad079d004; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; sid_guard=9de948c68d715b52c852329066720db9%7C1766413603%7C5184000%7CFri%2C+20-Feb-2026+14%3A26%3A43+GMT; uid_tt=b233129ca4eaf42b86a4250a80fb1bed; sid_tt=9de948c68d715b52c852329066720db9; sessionid=9de948c68d715b52c852329066720db9; is_staff_user=false; store-region=cn-gz; store-region-src=uid';


$cookie = "hevc_supported=true; __live_version__=%221.1.2.6176%22; live_use_vvc=%22false%22; enter_pc_once=1; passport_csrf_token=0b26ede85105c515a5b4fbcb65a52b6d; passport_csrf_token_default=0b26ede85105c515a5b4fbcb65a52b6d; bd_ticket_guard_client_web_domain=2; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; SEARCH_RESULT_LIST_TYPE=%22single%22; is_dash_user=1; SEARCH_UN_LOGIN_PV_CURR_DAY=%7B%22date%22%3A1766307748914%2C%22count%22%3A1%7D; passport_assist_user=CkCQlepd8gK75WsUuS-9VGWeoO30pBqIbqe2lOYA7IyJmD8jvDsalC41TOq3TywTbSBLj1lsrPLZbOrXQkwDtaxpGkoKPAAAAAAAAAAAAABP3ARWqntpvn8s7aJ_d_uT85wi6mBbgyzIrCGwYA708gTs2KkOH9NF9yNmt5nwMlNVRxDf8IQOGImv1lQgASIBAyNkr9Y%3D; n_mh=VOVHx91KKF_1NlJfn2x3GEYxBoWuVoca4GJNiWuS1No; sid_guard=90953c491ad4f59ddd1e36716267e787%7C1766408306%7C5184000%7CFri%2C+20-Feb-2026+12%3A58%3A26+GMT; uid_tt=dec9aa8d99264241d4f077cd37324834; uid_tt_ss=dec9aa8d99264241d4f077cd37324834; sid_tt=90953c491ad4f59ddd1e36716267e787; sessionid=90953c491ad4f59ddd1e36716267e787; sessionid_ss=90953c491ad4f59ddd1e36716267e787; session_tlb_tag=sttt%7C2%7CkJU8SRrU9Z3dHjZxYmfnh__________6-R0YUUWZuTeCqtpG-OGYBZn-sBZRJs3WyrjQKGg6SYA%3D; is_staff_user=false; sid_ucp_v1=1.0.0-KGQ1NmQyNTNlYWM2YTU2ZjQyZTk1YmMwMmM2NzAxMmI2YzA5N2YwODcKIAi9nLCTpfRFEPKApcoGGO8xIAww5c2U8QU4B0D0B0gEGgJsZiIgOTA5NTNjNDkxYWQ0ZjU5ZGRkMWUzNjcxNjI2N2U3ODc; ssid_ucp_v1=1.0.0-KGQ1NmQyNTNlYWM2YTU2ZjQyZTk1YmMwMmM2NzAxMmI2YzA5N2YwODcKIAi9nLCTpfRFEPKApcoGGO8xIAww5c2U8QU4B0D0B0gEGgJsZiIgOTA5NTNjNDkxYWQ0ZjU5ZGRkMWUzNjcxNjI2N2U3ODc; _bd_ticket_crypt_cookie=05c6fdb2acffab5d0ebd60c81db01115; __security_mc_1_s_sdk_sign_data_key_web_protect=3a0c5f5d-40a1-9d8a; __security_mc_1_s_sdk_cert_key=001a20d8-452b-89a3; __security_mc_1_s_sdk_crypt_sdk=4ed2115b-48c9-a7f4; __security_server_data_status=1; login_time=1766408311496; UIFID=e92777d2cb4cf0f94a981760c14554e8d3208daf0443679909dcdbe8e735b0617ff4d91647f82403cd4b0f15a3bdc9554733eff2438ed9042aa27cbc1b8331add2f1b5c2bb689833c02e7003167886afc5d0f4658d70a1d6cf0e0197956c7a904998ecc75f15bb511020314790430661d18379988fb148a201a6964dc6204c45eed3ed275f4e1537c7394ea6e6f4aaf360747e28685627ef1c12da7636e6d559; SelfTabRedDotControl=%5B%5D; publish_badge_show_info=%220%2C0%2C0%2C1766408318733%22; download_guide=%223%2F20251222%2F0%22; strategyABtestKey=%221766514910.929%22; ttwid=1%7COOcZ0189cfvj_EQWojjwK__0J79Bc_8iB3zB--5gRd0%7C1766514907%7Ce5e39a5ee2913fee2bc22de35ced5ef51dd5eeafaa3d553e5a193e25b73763fe; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAA-8Qj7oxba1TAj5cQIbHHvbtARRy3KlmvllNAc0VIxtU%2F1766592000000%2F0%2F1766565413933%2F0%22; feed_cache_data=%7B%22uuid%22%3A%22yigechengxuy88%22%2C%22scmVersion%22%3A%221.0.8.2275%22%2C%22date%22%3A1766566483690%2C%22dyQ%22%3A%221766566475%22%2C%22awemeId%22%3A%227580624218304433471%22%2C%22awemeInfoVersion%22%3A%223.0%22%7D; my_rd=2; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f273234343532333c323033333234272927676c715a75776a716a666a69273f2763646976602778; bit_env=Fh1PFuE3u65i0_mWiBNr6zSrk4Fq88hvFwWyDieCzSlIF8iqdzU8PQY6tKIjZUJAKIjlrwwtJRtnw_R6ZrbotFK-xddQ3wym18l-AhXw1TYoyvfHomlobFhlAiw9PTL8taqwRZLcr6Ejt03pFezELuMOehyf_I0YbhgaCBp58YPu8DfSOoXWG4XNYndsd4dUFwIEw6QxEaetkmJSmWDAZwICzbKLqiru-tMj3pk-BV8-cJvKvEJKR2ZJW-2auv6QHe4z0H0dHgzrDHgsYwjlrnsMGVZd6JCgI4ZKfrN8TT-lr43sb05bAVlx5Qa2fCZcj78GzCC4Q74B8p-D8qGvht5yyZENovth9K5yiMCEKM4rF5QD5QlSsndVSIWRMdAjV_yAzRs-AxzjWglFzEKHcoy_dIRz6UwXCVbzxOWe1PBOgL8IcXuCdbWWERajRsmhdp4M3m4Alzi9aefdFfTjgaiPt-r84tnGY9mwZJyZ1Jx0dgHQez62pIFowyTbQE_Q; gulu_source_res=eyJwX2luIjoiMzRlYjBiNWI5YTNlY2RkMjY3ZGQzOTBkNjhjMjk1MGIzMjY2YmUyMDc3MWViYmZlMTIzNDM4ZDMxZmNkYTVjOCJ9; passport_auth_mix_state=rhidksg9o68c2mbodu4p577w9z0uo42fvx5gdzhw49wlfevq; IsDouyinActive=true; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A2195%2C%5C%22screen_height%5C%22%3A1235%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A0%7D%22; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAA-8Qj7oxba1TAj5cQIbHHvbtARRy3KlmvllNAc0VIxtU%2F1766592000000%2F0%2F0%2F1766580469090%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSGp4U0dUWTRPaHBNc3JOcUFFMU9oRFczbkJsRjhMU2JGTkxGU014b0hpQXE4QnkxTTVzNFlRbmx1bFJiVHJ5ZCtDTXI4VGhQUnN1WFg1VmRSUWpRT009IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; home_can_add_dy_2_desktop=%221%22; biz_trace_id=c063a698; odin_tt=909ccf8b10d967676748a448a002d92350f599f62317899123eb45778da5a1e3fcbc73c45cb66d8d4f24fce782729f7ca869383386e89ece58c1dade65712338; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJIanhTR1RZNE9ocE1zck5xQUUxT2hEVzNuQmxGOExTYkZOTEZTTXhvSGlBcThCeTFNNXM0WVFubHVsUmJUcnlkK0NNcjhUaFBSc3VYWDVWZFJRalFPTT0iLCJ0c19zaWduIjoidHMuMi44NzUzOTc2NDZhYTNhODdiMWQ3MWQzZjVhMmE1ZWQ0N2NmMmJjZWQxMjUxMDc5MjZkZjk1MjIwZGU3NmUwZTJkYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiIvV2NEclBzMUFSMDBHSW1xa1BPZXRkNjBvdE53WEVia2pQVXlUZ3pXc2FjPSIsInNlY190cyI6IiNaL2VxYXVVa2xQaGRXY01hQXpNYVN0ZGVmdmpSTUFZaCs2NzUya1I4VXhaTStWK2FFbVhQcldMOUFiUjYifQ%3D%3D";


$author_id = isset($_REQUEST['author_id']) ? trim($_REQUEST['author_id']) : '2645904866702676';
$rank_type = isset($_REQUEST['rank_type']) ? trim($_REQUEST['rank_type']) : '1'; // 1:本周榜 2:上周榜 3:今年

$url = 'https://webcast26-normal-c-lq.amemv.com/webcast/subscribe/get_contribute_ranklist/?offset=0&count=20&rank_kind=2&author_id=' . $author_id . '&rank_type=' . $rank_type . '&live_request_from_jsb=1&webcast_sdk_version=4120&live_sdk_version=370101&gamecp_sdk_version=4120&webcast_language=zh&webcast_locale=zh_CN&webcast_gps_access=1&current_network_quality_info=%7B%22http_rtt%22%3A220%2C%22tcp_rtt%22%3A22%2C%22quic_rtt%22%3A22%2C%22downstream_throughput_kbps%22%3A51574%2C%22net_effective_connection_type%22%3A4%2C%22video_download_speed%22%3A8671%2C%22quic_receive_loss_rate%22%3A-1%2C%22quic_send_loss_rate%22%3A-1%7D&device_score=8.6459&address_book_access=2&user_id=4229184618762131&is_pad=false&is_android_pad=0&is_landscape=false&carrier_region=CN&sec_user_id=MS4wLjABAAAAVD5P6sSrk63XzjJT2n_3SQTzfg6xeHZEtY8q-gOoRaIdWQe1GVc14zkfspecr6YY&sec_author_id=MS4wLjABAAAAQRDbTKq61_DJ9hERWfudv8om5slFVfduB286CRdcnUg&klink_egdi=AAJyNSLZjdt16GBbCmj2905_two1IjVuFtSExcGXQT7r8NFKy0zS1ytB&iid=326986953398496&device_id=4135726972408180&ac=wifi&channel=xiaomi_2329_64_1104&aid=2329&app_name=douyin_lite&version_code=370100&version_name=37.1.0&device_platform=android&os=android&ssmix=a&device_type=M2012K10C&device_brand=Redmi&language=zh&os_api=33&os_version=13&manifest_version_code=370101&resolution=1080*2272&dpi=440&update_version_code=37109900&_rticket=1766413689931&package=com.ss.android.ugc.aweme.lite&gold_container=0&first_launch_timestamp=1757849569&last_deeplink_update_version_code=0&cpu_support64=true&host_abi=arm64-v8a&is_guest_mode=0&app_type=normal&minor_status=0&appTheme=light&is_preinstall=0&need_personal_recommend=1&is_android_fold=0&ts=1766413690&cdid=a4069695-e8a5-4cc8-aa4d-8c2350dc0b7d&md=0';

$response  = curl($url, $cookie);
$response = json_decode($response, true);
exit(json_encode($response['data'], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
function curl($url, $cookie)
{
    $author_id = isset($_REQUEST['author_id']) ? trim($_REQUEST['author_id']) : '';
    // 打印调试信息（仅用于开发）
    error_log("REQUEST URL: " . $url);
    error_log("REQUEST COOKIE: " . $cookie);
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
        //   关闭ssl
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_CUSTOMREQUEST => 'GET',
        CURLOPT_COOKIE => $cookie,
        CURLOPT_HTTPHEADER => [
            'User-Agent: com.ss.android.ugc.aweme.lite/370101 (Linux; U; Android 13; zh_CN; M2012K10C; Build/TP1A.220624.014; Cronet/TTNetVersion:6f1e308d 2025-12-08 QuicVersion:21ac1950 2025-11-18)',
            'x-security-argus: BridgeNetworkRequest/unknown aid/2329/xiaomi_2329_64_1104/Android/37.1.0/lynx/-1 https://lf-webcast-gr-sourcecdn.bytegecko.com/obj/byte-gurd-source-gr/webcast/mono/lynx/vip_common_douyin/pages/vip_rank_list/template.js',
            'hybrid-app-engine: lynx',
            // 'x-tt-dt: AAA6JMYDC5M2737OPMYV54XXYP25NYALG2DLBYP76QHJ4PBYAGC2LTCPTN2H2FKKEDVXYBP5ODZXUWNE6W2N5CHCWIMKS6EMZPDDES5HVIS4GE6BUALJ4OV5S7RFG',
            'activity_now_client: 1766413692074',
            'x-bd-kmsv: 1',
            // 'bd-ticket-guard-client-data: eyJyZXFfY29udGVudCI6InRpY2tldCxwYXRoLHRpbWVzdGFtcCIsInRpbWVzdGFtcCI6MTc2NjQxMzY4OSwidHNfc2lnbiI6IiIsInRzX3NpZ25fcmVlIjoidHMuMS5hNDJiNTlkNzc2Mzk3ZTJlMjBjY2Q1OTE2YTRmZDEyMmUxNzc1NjI0ZmUwNjc3MjRkNzBiZmQ5MWI2MmNmZjM5YzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9zaWduIjoiIiwicmVxX3NpZ25fcmVlIjoib0FVQ3VMUERxdytZWTZ3eGY5QjYwd1luUi85bVFnQmxUVm9lOC8xdjJPWT0ifQ==',
            'bd-ticket-guard-display-os-version: TP1A.220624.014',
            'sdk-version: 2',
            // 'session-tlb-tag: sttt|12|nelIxo1xW1LIUjKQZnINuf________-iC9AAOvyaasawFGoWteos_DMZ6ejz3-I7jx5f9VrTsl4=',
            'bd-ticket-guard-version: 3',
            'bd-ticket-guard-ree-public-key: BNojMBo3PNc3TWOyeYcAHzvmnbxSTJtx1/LGkPGXYKTudq1i7qkaDpFnPWS8tazKMjFCnoOutR8ZB1XTCntiHdA=',
            'bd-ticket-guard-iteration-version: 3',
            // 'x-tt-passport-mfa-token: Cja39CcFkstMZxTvCHWT4zQgE3+fObeRNgsJPe9Cqlz3hvjPWNdbDFj63thjhpxHWNTQU0NhZO0aSgo8AAAAAAAAAAAAAE/SDpuLAaHsng1smg3hTsX7lCioR/qRVwOWrOCo6SE58DeVZNquzZbc4Sxy2VE/sHy8EPH8gw4Y9rHRbCACIgED8JYIwg==',
            // 'x-tt-token: 009de948c68d715b52c852329066720db90265f1ea9e3f3f31b670815aed00590a49023d4d576af5da557cd27acc8a3a40b46d7568829b6c513a74b53b25892e87c2117cba4d1785bf7d1d623557c099de527fb4c412aa81239301035c145c6b903a2--0a490a2035d840c3aad3e9f030e2a4a65eab0f3d6afd2fcddb504a32457dbde068db6ca312206fadf1af597fecbb96070ca78b530574d1fd0b19f46c76accd986ab758d89b4518f6b4d309-3.0.1',
            // 'x-tt-token-supplement: 05e51bb04f46fb6ffd5ab976ad23103910af9c5c6aece7ef5ee8bf82a60aef6fdc830a0457877abf13af472629f406bd0532450f91ec70154b381fc916f932ea5fa',
            'passport-sdk-version: 601431',
            'token-tlb-tag: sttt|17|BJRtfCieQoLgFIF0bZEtdf_________Ltsv6uRGTP8v2Xp6GFjxsR8ZRk2kjiVHXYU8pM2OMxAE=',
            'x-vc-bdturing-sdk-version: 4.1.1.cn',
            'x-tt-store-region: cn-gz',
            'x-tt-store-region-src: uid',
            'x-tt-request-tag: s=-1;p=0',
            'x-ss-dp: 2329',
        ],
    ]);
    $response = curl_exec($curl);
    $err = curl_error($curl);
    if (PHP_VERSION_ID < 80500) {
        curl_close($curl);
    }
    if ($err) {
        return 'cURL Error #:' . $err;
    } else {
        echo $response;
        return $response;
    }
}
