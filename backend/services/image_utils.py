import cv2
import numpy as np
import base64

def image_to_base64(image_array):
    """将 OpenCV 图像转为 Base64"""
    try:
        _, buffer = cv2.imencode('.jpg', image_array)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        print(f"❌ Base64 转换失败: {e}")
        return ""

def apply_enhancement(img_bgr, method="None"):
    """应用图像增强算法"""
    if method == "None" or method == "None":
        return img_bgr
        
    try:
        if "CLAHE" in method:
            lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl, a, b))
            return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        elif "Gamma" in method:
            gamma = 1.2
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
            return cv2.LUT(img_bgr, table)
            
    except Exception as e:
        print(f"⚠️ 图像增强失败，返回原图: {e}")
        return img_bgr
        
    return img_bgr