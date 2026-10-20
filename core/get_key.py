# core/get_key.py

import requests

def get_key(url: str) -> str:
    """
    Hàm gọi API bypass thực tế để lấy key hoặc link đích trả về cho bot Discord.
    """
    if not url or not url.startswith("http"):
        return "bypass fail: Đường dẫn URL không hợp lệ!"

    try:
        # Sử dụng API công khai chuyên dụng để bypass các link rút gọn phổ biến (Link4M, Work.ink, v.v.)
        api_url = f"https://api.bypass.vip/bypass?url={requests.utils.quote(url)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(api_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # Kiểm tra nếu API trả về kết quả thành công
            if data.get("status") == 200 or "result" in data or "key" in data:
                result = data.get("result") or data.get("key") or data.get("destination")
                if result:
                    return str(result)
            
            # Nếu cấu trúc trả về khác, lấy thẳng nội dung thô
            if "url" in data:
                return str(data["url"])
                
        # Fallback sang một cổng API dự phòng nếu API chính phản hồi chậm hoặc lỗi
        fallback_api = f"https://api.vnbypass.com/api/v1/bypass?url={requests.utils.quote(url)}"
        res_fb = requests.get(fallback_api, headers=headers, timeout=15)
        if res_fb.status_code == 200:
            data_fb = res_fb.json()
            if data_fb.get("success") or "key" in data_fb:
                return str(data_fb.get("key") or data_fb.get("result"))

        return f"bypass fail: Không thể bóc tách key từ link này (Phản hồi từ server đích)."

    except requests.exceptions.Timeout:
        return "bypass fail: Quá thời gian chờ kết nối (Timeout). Vui lòng thử lại!"
    except Exception as e:
        return f"bypass fail: {str(e)}"
