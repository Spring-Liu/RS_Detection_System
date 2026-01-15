from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import DetectionRecord
from services.engine import detector
from services.image_utils import apply_enhancement, image_to_base64
from PIL import Image
import io
import numpy as np
import cv2

router = APIRouter()

@router.post("/detect/")
async def detect_endpoint(
    file: UploadFile = File(...), 
    model_name: str = Form(...),
    category: str = Form("aerial"),  # <--- 【修改 1】新增：接收 category 参数，默认 aerial
    conf: float = Form(...),
    use_sahi: str = Form("false"),
    enhance_type: str = Form("None"),
    db: Session = Depends(get_db)
):
    try:
        # 1. 参数清洗
        sahi_flag = use_sahi.lower() == 'true'
        
        # 2. 读取图片
        contents = await file.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # 3. 图像增强
        if enhance_type and enhance_type != "None":
            img_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            img_enhanced = apply_enhancement(img_bgr, enhance_type)
            pil_image = Image.fromarray(cv2.cvtColor(img_enhanced, cv2.COLOR_BGR2RGB))
            mode_suffix = f" + {enhance_type}"
        else:
            mode_suffix = ""

        # 4. 调用引擎推理
        # 【修改 2】将 category 传给 detector
        final_img, count, stats, mode_base = detector.run_inference(
            pil_image, 
            model_name, 
            category,  # <--- 必须传这个，告诉引擎去哪个文件夹找模型
            conf, 
            sahi_flag
        )
        
        final_mode = mode_base + mode_suffix

        # 5. 数据库存储
        new_record = DetectionRecord(
            filename=file.filename,
            model_type=final_mode,
            object_count=count,
            details=stats,
            # 如果你的数据库表支持 category 字段，建议最好也存进去
            # category=category 
        )
        db.add(new_record)
        db.commit()

        # 6. 返回结果
        return {
            "message": "Success",
            "image_base64": image_to_base64(final_img),
            "total_objects": count,
            "details": stats,
            "mode": final_mode
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")