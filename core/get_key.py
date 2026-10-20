import time
import requests

def get_key(url: str, verbose_cb=None) -> str:
    """
    Hàm xử lý bypass và lấy key từ URL được truyền vào.
    verbose_cb: Hàm callback dùng để in log trạng thái (nếu có).
    """
    if verbose_cb:
        verbose_cb(f"Đang tiến hành xử lý URL: {url}")
    
    try:
        # Ví dụ logic gọi request hoặc xử lý bypass ở đây
        # response = requests.get(url, timeout=15)
        
        # Tạm thời trả về chuỗi kết quả mẫu (hoặc key thực tế sau khi giải mã)
        time.sleep(2) # Giả lập thời gian xử lý
        
        # Nếu thành công, trả về key:
        return "DEMO-KEY-SUCCESS-12345"
        
    except Exception as e:
        if verbose_cb:
            verbose_cb(f"Lỗi trong quá trình lấy key: {str(e)}")
        return f"bypass fail: {str(e)}"