<?php

/**
 * 
 * 抖音用户信息查询
 * 
 * 使用方法：
 * userinfo.php?url=https://www.douyin.com/user/MS4wLjABAAAAyiUBvOEjnzVYHl3xyIopxDpk1e7ECR-TW10I14EdS80
 * userinfo.php?id=MS4wLjABAAAAyiUBvOEjnzVYHl3xyIopxDpk1e7ECR-TW10I14EdS80
 * 
 * 参数说明：
 * id: 抖音用户sec_user_id
 * url: 抖音用户主页链接
 * 
 **/

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept');
header('Access-Control-Max-Age: 86400');
header('Content-Type: application/json; charset=utf-8');
// 关闭错误报告
error_reporting(0);

// $cookie = "hevc_supported=true; UIFID=973a3fd64dcc46a3490fd9b60d4a8e663b34df4ccc4bbcf97643172fb712d8b0af849bef1014ced93a67391f3e94eae8588e1b42ddf55a3e0acc3751436ace3927fc8c79ec49eec532867b9efbb5b62248d0d42a592d66a69ecbbd5bc6d01b3588badf404161dab873d63372c77881fb0dc4687687a5104e127ead6325556c7848b40c01004032a34f26dfad472b9845195d68854193bced0b6331fa306a7904; bd_ticket_guard_client_web_domain=2; store-region=cn-gz; store-region-src=uid; SelfTabRedDotControl=%5B%5D; my_rd=2; SEARCH_RESULT_LIST_TYPE=%22single%22; xgplayer_device_id=28551481219; live_use_vvc=%22false%22; theme=%22light%22; enter_pc_once=1; fpk1=U2FsdGVkX19tVdrXolUdD7WijZtWBytYvCmzt4vOKYMMdW6u8QUfjMiJR61kMeCmNQb8MdOCnw9nJtxD3UAHwQ==; fpk2=a3f57bbe21c4e30379228ad7788f224d; __live_version__=%221.1.4.539%22; __druidClientInfo=JTdCJTIyY2xpZW50V2lkdGglMjIlM0ExMzc2JTJDJTIyY2xpZW50SGVpZ2h0JTIyJTNBNjc0JTJDJTIyd2lkdGglMjIlM0ExMzc2JTJDJTIyaGVpZ2h0JTIyJTNBNjc0JTJDJTIyZGV2aWNlUGl4ZWxSYXRpbyUyMiUzQTEuMjUlMkMlMjJ1c2VyQWdlbnQlMjIlM0ElMjJNb3ppbGxhJTJGNS4wJTIwKFdpbmRvd3MlMjBOVCUyMDEwLjAlM0IlMjBXaW42NCUzQiUyMHg2NCklMjBBcHBsZVdlYktpdCUyRjUzNy4zNiUyMChLSFRNTCUyQyUyMGxpa2UlMjBHZWNrbyklMjBDaHJvbWUlMkYxNDAuMC4wLjAlMjBTYWZhcmklMkY1MzcuMzYlMjIlN0Q=; passport_csrf_token=6d4478db894a507fa53c9e9fe0473b37; passport_csrf_token_default=6d4478db894a507fa53c9e9fe0473b37; dy_swidth=1536; dy_sheight=864; is_dash_user=1; xgplayer_user_id=82377755329; s_v_web_id=verify_mj2ias9d_egPq4j92_mihB_4V5s_9tlX_5njB62ldN8Fk; passport_mfa_token=CjdKBgTkUXDDmRwed12FR55eo5FqujnYdwEmF75MgG0moVbHUJIMku1L3HkAb2Va3O6vu0WQRLx0GkoKPAAAAAAAAAAAAABP0g6biwGh7J4NbJoN4U7F%2B5QoqEf6kVcDlqzgqOkhOfA3lWTars2W3OEsctlRP7B8vBDH%2B4MOGPax0WwgAiIBAzjvQpk%3D; d_ticket=37ebc73090fc101741276f13e1674e949ceca; n_mh=XPrGlncfCwvX48AijwWOz7NPclXMq_x49jQE-05HlAg; session_tlb_tag_bk=sttt%7C19%7CvE_AtpzHIG1x0qUDz4RNYv________-dLBcHY_H75Ldhos8yUd9hCngP1NJM54rAONzOXlvUr9A%3D; __security_server_data_status=1; __security_mc_1_s_sdk_crypt_sdk=cec82b4e-44bd-af6f; __security_mc_1_s_sdk_cert_key=0d7f4670-4c71-9e14; download_guide=%223%2F20251217%2F0%22; volume_info=%7B%22isUserMute%22%3Atrue%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.875%7D; __ac_nonce=0694a92b100c0fbd7d900; __ac_signature=_02B4Z6wo00f015YAtHQAAIDCJ-AKbIx2wEuWILDAAIzTc8; strategyABtestKey=%221766494919.293%22; is_staff_user=false; publish_badge_show_info=%220%2C0%2C0%2C1766494932201%22; gulu_source_res=eyJwX2luIjoiMzRlYjBiNWI5YTNlY2RkMjY3ZGQzOTBkNjhjMjk1MGIzMjY2YmUyMDc3MWViYmZlMTIzNDM4ZDMxZmNkYTVjOCJ9; feed_cache_data=%7B%22uuid%22%3A%2234384835224%22%2C%22scmVersion%22%3A%221.0.8.2024%22%2C%22date%22%3A1766495959826%2C%22dyQ%22%3A%221766495930%22%2C%22awemeId%22%3A%227575515727310884115%22%2C%22awemeInfoVersion%22%3A%223.0%22%7D; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A1%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f2734373c363c34333c3133333234272927676c715a75776a716a666a69273f2763646976602778; bit_env=9kQlMfjpUO_iQttu2A3ZniKiYC7JPmuq7M0Mjs-6YaR03DtDmG8CqnUkQySoziLQSIS7rulCPl7HXereoh4FgcoLb-Es1ECvmXckWcx9maNEJ3pfnQY5XL0gjblrolVvMXJgOx8qGEB-7AWWXb-2Zkmt53UeqgtiArVodK4d9gDaZfPn_xGSebEYdzlUfyOxYaxpOYJXwfzhwpdgcwWH4OqcEpI53dfxwc_fKjWRfjrEE6VEe7FNtxsxzs8r6mX98fQuVH8nzICFkFDZTeTCw_CtsshvKlvSMI86xcMXre7Gxr3Rov-_bxdvqzxU-a0VSP-RwSb9VjH0HKf-4llbep-Nzrh8Uz4utjP2FcWjFc42eVkGzQNttF5cOw9bdg9SA-2Ey_LXAzFvJQ18lwsJ36vZIXkG6327TApHOfdu1vvseAnHukDTuTn7WXQFsNywhzFxXIKRJ1-i4i24Q9sM4hcE9yq3OCEnGzbdy-jBcU32RPv6aFOyxo7xK5ek8UUN; passport_auth_mix_state=4welyn97bw19fmmk52116p9g3s4dzyv9tljl9x2r3ud98o5a; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1536%2C%5C%22screen_height%5C%22%3A864%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A150%7D%22; ttwid=1%7C-FAWbE-c8cN-vq6Dx502LM41mDVSGMxsMDU1HaFM9rw%7C1766496310%7Cf2f3d3f82bb0de6368edbef180c9e5c586eb0836c2bf245d8175d1e704aa9593; passport_assist_user=CkEKzWgXNoMGl_27qzgahMW85Ro6WkFHi7C_6PVX7laEcVhXo9a9XC8g1yS5ag-QLvqTs_vAhuGhsAWeVM0GCDEZGRpKCjwAAAAAAAAAAAAAT90m9zRuWZH7CQXSejXuNSiIIdqrhFFHq_2VgTcQTf3xay0dV77p6qV9XdfC3Yupl0wQk_uEDhiJr9ZUIAEiAQMjjC2Q; sid_guard=0e7f2a8ef37cd0cc080bca6c1cb397cb%7C1766496312%7C5184000%7CSat%2C+21-Feb-2026+13%3A25%3A12+GMT; uid_tt=f6e70850789536affb4e1c4f0b005398; uid_tt_ss=f6e70850789536affb4e1c4f0b005398; sid_tt=0e7f2a8ef37cd0cc080bca6c1cb397cb; sessionid=0e7f2a8ef37cd0cc080bca6c1cb397cb; sessionid_ss=0e7f2a8ef37cd0cc080bca6c1cb397cb; session_tlb_tag=sttt%7C7%7CDn8qjvN80MwIC8psHLOXy__________PCMN93DUqd4eEo44Ma4FuR-YFMIphmuXIuAQUQsUbHH4%3D; sid_ucp_v1=1.0.0-KDUyZjk5YmU0ZmY0ZDA0NWQ1NWQwMjRkMmIxYzA4NGM2OGI1ZmEyNWEKIQjToPDdu6ziBxC4sKrKBhjvMSAMMKb27skGOAVA-wdIBBoCbHEiIDBlN2YyYThlZjM3Y2QwY2MwODBiY2E2YzFjYjM5N2Ni; ssid_ucp_v1=1.0.0-KDUyZjk5YmU0ZmY0ZDA0NWQ1NWQwMjRkMmIxYzA4NGM2OGI1ZmEyNWEKIQjToPDdu6ziBxC4sKrKBhjvMSAMMKb27skGOAVA-wdIBBoCbHEiIDBlN2YyYThlZjM3Y2QwY2MwODBiY2E2YzFjYjM5N2Ni; __security_mc_1_s_sdk_sign_data_key_web_protect=f6352649-45cc-adb6; login_time=1766496325194; biz_trace_id=fb9041f6; _bd_ticket_crypt_cookie=1188bc8c0188b21e7961573f3fc4496c; IsDouyinActive=false; home_can_add_dy_2_desktop=%220%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSkJ1THFNZmxFYmVqa1hTbGU5bE5DcnpYTHkxcDd3dmRoQ1hFejJERWFLc01Lc3pGdWJ4TkpOa2Q3OHN3M3A5QVkyK3NPVTVGUTlkSHE4cHdCZGtUZ0E9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJKQnVMcU1mbEViZWprWFNsZTlsTkNyelhMeTFwN3d2ZGhDWEV6MkRFYUtzTUtzekZ1YnhOSk5rZDc4c3czcDlBWTIrc09VNUZROWRIcThwd0Jka1RnQT0iLCJ0c19zaWduIjoidHMuMi45ODVkZTNmNGQwZmI1YTEzYWQ3ODhjMDE2NzNkZDc4OTM3NzEzMjllODYyMWQ2MzFmYWZhNzRiNjFiZjQ2MDlmYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJhSlJGT05zVmV0OU1EOXpUK3V3TE1iU1NQUzduS3BTTGdEaG5LRG1sN2kwPSIsInNlY190cyI6IiM1TXhucDduS0VDcDkwWnE1dStjc1h3bDRTKzJVRlY2bEFMQTV0WGxwOTJxZ0xxMFJDQTl3SHNKcnl0QU0ifQ%3D%3D; odin_tt=fda1c2e005adadfa0a508b99b6331817713d8e67b7e3b22b1d5c7a218b3a908db6abdc76a08098afdce9636473efb2d0c8bc41777ae49aef4e8b318c73aa24e3831dde1e1fc01dc1ede654f93945fc3c";

// $cookie = "hevc_supported=true; __live_version__=%221.1.2.6176%22; live_use_vvc=%22false%22; enter_pc_once=1; passport_csrf_token=0b26ede85105c515a5b4fbcb65a52b6d; passport_csrf_token_default=0b26ede85105c515a5b4fbcb65a52b6d; bd_ticket_guard_client_web_domain=2; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; SEARCH_RESULT_LIST_TYPE=%22single%22; is_dash_user=1; SEARCH_UN_LOGIN_PV_CURR_DAY=%7B%22date%22%3A1766307748914%2C%22count%22%3A1%7D; passport_assist_user=CkCQlepd8gK75WsUuS-9VGWeoO30pBqIbqe2lOYA7IyJmD8jvDsalC41TOq3TywTbSBLj1lsrPLZbOrXQkwDtaxpGkoKPAAAAAAAAAAAAABP3ARWqntpvn8s7aJ_d_uT85wi6mBbgyzIrCGwYA708gTs2KkOH9NF9yNmt5nwMlNVRxDf8IQOGImv1lQgASIBAyNkr9Y%3D; n_mh=VOVHx91KKF_1NlJfn2x3GEYxBoWuVoca4GJNiWuS1No; sid_guard=90953c491ad4f59ddd1e36716267e787%7C1766408306%7C5184000%7CFri%2C+20-Feb-2026+12%3A58%3A26+GMT; uid_tt=dec9aa8d99264241d4f077cd37324834; uid_tt_ss=dec9aa8d99264241d4f077cd37324834; sid_tt=90953c491ad4f59ddd1e36716267e787; sessionid=90953c491ad4f59ddd1e36716267e787; sessionid_ss=90953c491ad4f59ddd1e36716267e787; session_tlb_tag=sttt%7C2%7CkJU8SRrU9Z3dHjZxYmfnh__________6-R0YUUWZuTeCqtpG-OGYBZn-sBZRJs3WyrjQKGg6SYA%3D; is_staff_user=false; sid_ucp_v1=1.0.0-KGQ1NmQyNTNlYWM2YTU2ZjQyZTk1YmMwMmM2NzAxMmI2YzA5N2YwODcKIAi9nLCTpfRFEPKApcoGGO8xIAww5c2U8QU4B0D0B0gEGgJsZiIgOTA5NTNjNDkxYWQ0ZjU5ZGRkMWUzNjcxNjI2N2U3ODc; ssid_ucp_v1=1.0.0-KGQ1NmQyNTNlYWM2YTU2ZjQyZTk1YmMwMmM2NzAxMmI2YzA5N2YwODcKIAi9nLCTpfRFEPKApcoGGO8xIAww5c2U8QU4B0D0B0gEGgJsZiIgOTA5NTNjNDkxYWQ0ZjU5ZGRkMWUzNjcxNjI2N2U3ODc; _bd_ticket_crypt_cookie=05c6fdb2acffab5d0ebd60c81db01115; __security_mc_1_s_sdk_sign_data_key_web_protect=3a0c5f5d-40a1-9d8a; __security_mc_1_s_sdk_cert_key=001a20d8-452b-89a3; __security_mc_1_s_sdk_crypt_sdk=4ed2115b-48c9-a7f4; __security_server_data_status=1; login_time=1766408311496; UIFID=e92777d2cb4cf0f94a981760c14554e8d3208daf0443679909dcdbe8e735b0617ff4d91647f82403cd4b0f15a3bdc9554733eff2438ed9042aa27cbc1b8331add2f1b5c2bb689833c02e7003167886afc5d0f4658d70a1d6cf0e0197956c7a904998ecc75f15bb511020314790430661d18379988fb148a201a6964dc6204c45eed3ed275f4e1537c7394ea6e6f4aaf360747e28685627ef1c12da7636e6d559; SelfTabRedDotControl=%5B%5D; publish_badge_show_info=%220%2C0%2C0%2C1766408318733%22; download_guide=%223%2F20251222%2F0%22; strategyABtestKey=%221766514910.929%22; ttwid=1%7COOcZ0189cfvj_EQWojjwK__0J79Bc_8iB3zB--5gRd0%7C1766514907%7Ce5e39a5ee2913fee2bc22de35ced5ef51dd5eeafaa3d553e5a193e25b73763fe; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAA-8Qj7oxba1TAj5cQIbHHvbtARRy3KlmvllNAc0VIxtU%2F1766592000000%2F0%2F1766565413933%2F0%22; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAA-8Qj7oxba1TAj5cQIbHHvbtARRy3KlmvllNAc0VIxtU%2F1766592000000%2F0%2F1766566470016%2F0%22; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A2195%2C%5C%22screen_height%5C%22%3A1235%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; feed_cache_data=%7B%22uuid%22%3A%22yigechengxuy88%22%2C%22scmVersion%22%3A%221.0.8.2275%22%2C%22date%22%3A1766566483690%2C%22dyQ%22%3A%221766566475%22%2C%22awemeId%22%3A%227580624218304433471%22%2C%22awemeInfoVersion%22%3A%223.0%22%7D; my_rd=2; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f27353337333d3133333033333234272927676c715a75776a716a666a69273f2763646976602778; bit_env=Vwno-6vhStesOh2xcPeF6soPzFCBgZMdFIfe5-i_Ux04wUR_NvfoKpjZCU3jlvDJn9mHt6QCd6BHOXBvM3I3X8-6xCCZxidU-yzwwqzoMsG1P14NNZ36xBVNVGulLUMIvFVJj8ZHnVR8nmOstISj1U7wuFsNwh3PnyIOY8ljT3CT7C5HWlFPalo-pCTKuIb_wul68dLp3Ha03_hnO3gqKiLvNagwIOjR3hskkiwdcbk8tnxc9KnqSfDYiqTw7TsUWJvvvAxh1S1sE0AQHz6TzuZ5NXXMEXoDI-ildCkjZ9CmVxXUM8S4rppXgy4I9XcMAqKAoK4BKU-5jQ23HwVN5YQeTna9GVMcQzReY-CWAqxZMJPUUN1LqZAVCytMnOT3-m2G0wZxbhEE-n_vj2tXAGvSHd8LU_2XblJ9OnllV275ASNTdC6U7vwuCbDfTWijGbZ6HgFoDk8Yuz4vMAT66hDOLrK_AKsyqpoprLZE_t65ArKzqxUxombcxN2KMzo0; gulu_source_res=eyJwX2luIjoiMzRlYjBiNWI5YTNlY2RkMjY3ZGQzOTBkNjhjMjk1MGIzMjY2YmUyMDc3MWViYmZlMTIzNDM4ZDMxZmNkYTVjOCJ9; passport_auth_mix_state=rguhkxck2ca00g4vt5i2vrnhpt9tpp77; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; IsDouyinActive=true; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSGp4U0dUWTRPaHBNc3JOcUFFMU9oRFczbkJsRjhMU2JGTkxGU014b0hpQXE4QnkxTTVzNFlRbmx1bFJiVHJ5ZCtDTXI4VGhQUnN1WFg1VmRSUWpRT009IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; home_can_add_dy_2_desktop=%221%22; biz_trace_id=970775f1; odin_tt=c646d7e404460e62366b09eca7656ec8e62b38c7dbbdd66f7fe63016da5e4c00c98ac0b281f6e16b4113b6a7d886fe2a53d8c55dff006a0fcbc210c383353cab; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJIanhTR1RZNE9ocE1zck5xQUUxT2hEVzNuQmxGOExTYkZOTEZTTXhvSGlBcThCeTFNNXM0WVFubHVsUmJUcnlkK0NNcjhUaFBSc3VYWDVWZFJRalFPTT0iLCJ0c19zaWduIjoidHMuMi44NzUzOTc2NDZhYTNhODdiMWQ3MWQzZjVhMmE1ZWQ0N2NmMmJjZWQxMjUxMDc5MjZkZjk1MjIwZGU3NmUwZTJkYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiJvaDBDdVJYcTgycjlHSXpFWmdiRWk1RzZtNG41aXpsMHRhNkZCQXBLVnUwPSIsInNlY190cyI6IiMrQU1ITkdrZFdtaytBNThteUpDYXRtUEE3aGpoNVJ0VHFkUWluK1pNMGIxNDJmZUE4NDJaeXNmWmFtTnYifQ%3D%3D"

$cookie = "hevc_supported=true; __live_version__=%221.1.2.6176%22; live_use_vvc=%22false%22; enter_pc_once=1; passport_csrf_token=0b26ede85105c515a5b4fbcb65a52b6d; passport_csrf_token_default=0b26ede85105c515a5b4fbcb65a52b6d; bd_ticket_guard_client_web_domain=2; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; SEARCH_RESULT_LIST_TYPE=%22single%22; is_dash_user=1; SEARCH_UN_LOGIN_PV_CURR_DAY=%7B%22date%22%3A1766307748914%2C%22count%22%3A1%7D; passport_assist_user=CkCQlepd8gK75WsUuS-9VGWeoO30pBqIbqe2lOYA7IyJmD8jvDsalC41TOq3TywTbSBLj1lsrPLZbOrXQkwDtaxpGkoKPAAAAAAAAAAAAABP3ARWqntpvn8s7aJ_d_uT85wi6mBbgyzIrCGwYA708gTs2KkOH9NF9yNmt5nwMlNVRxDf8IQOGImv1lQgASIBAyNkr9Y%3D; n_mh=VOVHx91KKF_1NlJfn2x3GEYxBoWuVoca4GJNiWuS1No; sid_guard=90953c491ad4f59ddd1e36716267e787%7C1766408306%7C5184000%7CFri%2C+20-Feb-2026+12%3A58%3A26+GMT; uid_tt=dec9aa8d99264241d4f077cd37324834; uid_tt_ss=dec9aa8d99264241d4f077cd37324834; sid_tt=90953c491ad4f59ddd1e36716267e787; sessionid=90953c491ad4f59ddd1e36716267e787; sessionid_ss=90953c491ad4f59ddd1e36716267e787; session_tlb_tag=sttt%7C2%7CkJU8SRrU9Z3dHjZxYmfnh__________6-R0YUUWZuTeCqtpG-OGYBZn-sBZRJs3WyrjQKGg6SYA%3D; is_staff_user=false; sid_ucp_v1=1.0.0-KGQ1NmQyNTNlYWM2YTU2ZjQyZTk1YmMwMmM2NzAxMmI2YzA5N2YwODcKIAi9nLCTpfRFEPKApcoGGO8xIAww5c2U8QU4B0D0B0gEGgJsZiIgOTA5NTNjNDkxYWQ0ZjU5ZGRkMWUzNjcxNjI2N2U3ODc; ssid_ucp_v1=1.0.0-KGQ1NmQyNTNlYWM2YTU2ZjQyZTk1YmMwMmM2NzAxMmI2YzA5N2YwODcKIAi9nLCTpfRFEPKApcoGGO8xIAww5c2U8QU4B0D0B0gEGgJsZiIgOTA5NTNjNDkxYWQ0ZjU5ZGRkMWUzNjcxNjI2N2U3ODc; _bd_ticket_crypt_cookie=05c6fdb2acffab5d0ebd60c81db01115; __security_mc_1_s_sdk_sign_data_key_web_protect=3a0c5f5d-40a1-9d8a; __security_mc_1_s_sdk_cert_key=001a20d8-452b-89a3; __security_mc_1_s_sdk_crypt_sdk=4ed2115b-48c9-a7f4; __security_server_data_status=1; login_time=1766408311496; UIFID=e92777d2cb4cf0f94a981760c14554e8d3208daf0443679909dcdbe8e735b0617ff4d91647f82403cd4b0f15a3bdc9554733eff2438ed9042aa27cbc1b8331add2f1b5c2bb689833c02e7003167886afc5d0f4658d70a1d6cf0e0197956c7a904998ecc75f15bb511020314790430661d18379988fb148a201a6964dc6204c45eed3ed275f4e1537c7394ea6e6f4aaf360747e28685627ef1c12da7636e6d559; SelfTabRedDotControl=%5B%5D; publish_badge_show_info=%220%2C0%2C0%2C1766408318733%22; download_guide=%223%2F20251222%2F0%22; strategyABtestKey=%221766514910.929%22; ttwid=1%7COOcZ0189cfvj_EQWojjwK__0J79Bc_8iB3zB--5gRd0%7C1766514907%7Ce5e39a5ee2913fee2bc22de35ced5ef51dd5eeafaa3d553e5a193e25b73763fe; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAA-8Qj7oxba1TAj5cQIbHHvbtARRy3KlmvllNAc0VIxtU%2F1766592000000%2F0%2F1766565413933%2F0%22; feed_cache_data=%7B%22uuid%22%3A%22yigechengxuy88%22%2C%22scmVersion%22%3A%221.0.8.2275%22%2C%22date%22%3A1766566483690%2C%22dyQ%22%3A%221766566475%22%2C%22awemeId%22%3A%227580624218304433471%22%2C%22awemeInfoVersion%22%3A%223.0%22%7D; my_rd=2; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e582729277672715a646971273f2763646976602729277f6b5a666475273f2763646976602729276d6a6e5a6b6a716c273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f273234343532333c323033333234272927676c715a75776a716a666a69273f2763646976602778; bit_env=Fh1PFuE3u65i0_mWiBNr6zSrk4Fq88hvFwWyDieCzSlIF8iqdzU8PQY6tKIjZUJAKIjlrwwtJRtnw_R6ZrbotFK-xddQ3wym18l-AhXw1TYoyvfHomlobFhlAiw9PTL8taqwRZLcr6Ejt03pFezELuMOehyf_I0YbhgaCBp58YPu8DfSOoXWG4XNYndsd4dUFwIEw6QxEaetkmJSmWDAZwICzbKLqiru-tMj3pk-BV8-cJvKvEJKR2ZJW-2auv6QHe4z0H0dHgzrDHgsYwjlrnsMGVZd6JCgI4ZKfrN8TT-lr43sb05bAVlx5Qa2fCZcj78GzCC4Q74B8p-D8qGvht5yyZENovth9K5yiMCEKM4rF5QD5QlSsndVSIWRMdAjV_yAzRs-AxzjWglFzEKHcoy_dIRz6UwXCVbzxOWe1PBOgL8IcXuCdbWWERajRsmhdp4M3m4Alzi9aefdFfTjgaiPt-r84tnGY9mwZJyZ1Jx0dgHQez62pIFowyTbQE_Q; gulu_source_res=eyJwX2luIjoiMzRlYjBiNWI5YTNlY2RkMjY3ZGQzOTBkNjhjMjk1MGIzMjY2YmUyMDc3MWViYmZlMTIzNDM4ZDMxZmNkYTVjOCJ9; passport_auth_mix_state=rhidksg9o68c2mbodu4p577w9z0uo42fvx5gdzhw49wlfevq; IsDouyinActive=true; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A2195%2C%5C%22screen_height%5C%22%3A1235%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A0%7D%22; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAA-8Qj7oxba1TAj5cQIbHHvbtARRy3KlmvllNAc0VIxtU%2F1766592000000%2F0%2F0%2F1766580469090%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSGp4U0dUWTRPaHBNc3JOcUFFMU9oRFczbkJsRjhMU2JGTkxGU014b0hpQXE4QnkxTTVzNFlRbmx1bFJiVHJ5ZCtDTXI4VGhQUnN1WFg1VmRSUWpRT009IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; home_can_add_dy_2_desktop=%221%22; biz_trace_id=c063a698; odin_tt=909ccf8b10d967676748a448a002d92350f599f62317899123eb45778da5a1e3fcbc73c45cb66d8d4f24fce782729f7ca869383386e89ece58c1dade65712338; bd_ticket_guard_client_data_v2=eyJyZWVfcHVibGljX2tleSI6IkJIanhTR1RZNE9ocE1zck5xQUUxT2hEVzNuQmxGOExTYkZOTEZTTXhvSGlBcThCeTFNNXM0WVFubHVsUmJUcnlkK0NNcjhUaFBSc3VYWDVWZFJRalFPTT0iLCJ0c19zaWduIjoidHMuMi44NzUzOTc2NDZhYTNhODdiMWQ3MWQzZjVhMmE1ZWQ0N2NmMmJjZWQxMjUxMDc5MjZkZjk1MjIwZGU3NmUwZTJkYzRmYmU4N2QyMzE5Y2YwNTMxODYyNGNlZGExNDkxMWNhNDA2ZGVkYmViZWRkYjJlMzBmY2U4ZDRmYTAyNTc1ZCIsInJlcV9jb250ZW50Ijoic2VjX3RzIiwicmVxX3NpZ24iOiIvV2NEclBzMUFSMDBHSW1xa1BPZXRkNjBvdE53WEVia2pQVXlUZ3pXc2FjPSIsInNlY190cyI6IiNaL2VxYXVVa2xQaGRXY01hQXpNYVN0ZGVmdmpSTUFZaCs2NzUya1I4VXhaTStWK2FFbVhQcldMOUFiUjYifQ%3D%3D";

// 获取抖音主页
$url = urldecode($_REQUEST['url'] ?? $_REQUEST['id'] ?? '');


$id = $url;
preg_match('/(http[s]?:\/\/[^\s]+)/', $url, $matches);
$url = $matches[0];

// 匹配抖音 URL
if (strpos($url, 'www.douyin.com') !== false) {
    // 提取函数获取用户id
    $sec_user_id = get_userid($url);
} elseif (strpos($url, 'v.douyin.com') !== false) {
    // 先重定向后再获取用户id
    $sec_user_id = get_headers($url, true)['Location'];
    // 提取函数获取用户id
    $sec_user_id = get_userid($sec_user_id);
} else {
    // 其他情况处理
    $sec_user_id = $url;
}

$response = httpRequest(
    "https://www.douyin.com/aweme/v1/web/im/user/info/",
    'sec_user_ids=["' . $sec_user_id . '"]',
    array(
        "Content-Type: application/x-www-form-urlencoded; charset=UTF-8",
        "accept: application/json, text/plain, */*",
        "accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control: no-cache",
        "content-type: application/x-www-form-urlencoded; charset=UTF-8",
        "origin: https://www.douyin.com",
        "pragma: no-cache",
        "priority: u=1, i",
        "referer: https://www.douyin.com/user/" . $sec_user_id . "?showTab=like",
        "sec-ch-ua: \"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile: ?0",
        "sec-ch-ua-platform: \"Windows\"",
        "sec-fetch-dest: empty",
        "sec-fetch-mode: cors",
        "sec-fetch-site: same-origin",
        "cookie: " . $cookie,
        // "uifid: c4683e1a43ffa6bc6852097c712d14b81f04bc9b5ca6d30214b0e66b4e38528054345efeaee70378c5ebd842a0bea40b9bb5dea4eb56f366ec6029963fdfbff787512d041810ae8ba9565a5601209fcaa98516fe56a9f807e53ffcaa8f835d674a896494ce770108fc9897faa3f28a61bdb1a694e6ee69d7d70e4dca01dc1432fcdd10941ec80a36be77debe9429cd47f861a91ac5e37384cfc7d162e3dd8572",
        "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "x-secsdk-csrf-token: DOWNGRADE"
    )
);

$response = json_decode($response, true);
$item = $response['data'][0];
// 返回$item如下：

exit(json_encode([
    "code" => 200,
    "msg" => "解析成功",
    "sec_uid" => $sec_user_id, // 注意：这里的 $sec_user_id 需要根据你的实际数据来源设置
    "data" => [
        'id' => $sec_user_id,
        'nickname' => $item['nickname'],
        'enterprise_verify_reason' => $item['enterprise_verify_reason'],
        'author_id' => $item['uid'],
        'unique_id' => $item['unique_id'],
        'avatar' => $item['avatar_thumb']['url_list'][0],
        'avatar_small' => $item['avatar_small']['url_list'][0],
        'short_id' => $item['short_id'],
        'signature' => $item['signature'],
    ]
], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));


function httpRequest($url, $data, $headers = [])
{
    // 发起HTTP请求
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'POST');
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $response = curl_exec($ch);
    curl_close($ch);

    return $response;
}


/**
 * 从抖音分享链接中提取用户ID（优先获取sec_uid，不存在则获取user/后的ID）
 * @param string $url 抖音分享链接
 * @return string|null 返回用户ID，如果提取失败则返回null
 */
function get_userid($url)
{
    // 1. 首先尝试从URL参数中获取sec_uid
    $query = parse_url($url, PHP_URL_QUERY); // 获取URL中的查询参数部分
    if ($query) {
        parse_str($query, $params); // 将查询参数解析为关联数组
        if (isset($params['sec_uid'])) {
            return $params['sec_uid']; // 如果存在sec_uid则直接返回
        }
    }

    // 2. 如果sec_uid不存在，则尝试从路径中提取user/后的内容
    $path = parse_url($url, PHP_URL_PATH); // 获取URL的路径部分
    if (strpos($path, 'user/') !== false) {
        $parts = explode('user/', $path); // 用'user/'分割路径
        if (count($parts) > 1) {
            $user_part = explode('?', $parts[1])[0]; // 去除可能存在的后续参数
            return $user_part;
        }
    }

    // 3. 如果以上方式都失败，返回null（可根据需要改为抛出异常等错误处理）
    return null;
}

// 写个获取抖音接口重定向后的链接函数代码
function douyin_getRedirectUrl($url)
{
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $response = curl_exec($ch);
    // 获取重定向后的最终 URL
    $finalUrl = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
    curl_close($ch);
    return $finalUrl;
}
