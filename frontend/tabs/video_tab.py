import streamlit as st
import cv2
import numpy as np
import tempfile
import time
from utils.api_client import send_detect_request, decode_base64_image

from utils.config import VIDEO_FRAME_SKIP #

def process_frame(frame_bgr, model_name, category, conf):
    """
    处理单帧：输入 BGR，输出 RGB
    """
    # 1. 编码图片 (OpenCV 需要 BGR 输入)
    success, img_encoded = cv2.imencode('.jpg', frame_bgr)
    if not success:
        # 失败返回原图 (BGR -> RGB)
        return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB), 0

    img_bytes = img_encoded.tobytes()

    # 2. 发送请求

    success, result = send_detect_request(
        file_bytes=img_bytes,
        file_name="video_frame.jpg",
        file_type="image/jpeg",
        model_name=model_name,
        category=category,
        conf=conf,
        use_sahi=False,
        enhance_type="None"
    )

    if success:
        # 3. 解码结果 (PIL 解码出来默认是 RGB)
        res_img_pil = decode_base64_image(result['image_base64'])
        if res_img_pil:
            return np.array(res_img_pil), result['total_objects']

    # 兜底：返回原图 (BGR -> RGB)
    return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB), 0

def render_video_tab(model_dict: dict):
    st.markdown("### 📹 视频目标检测")

    st.markdown("#### 🕹️ 检测参数配置")

    # 使用 col1/col2/col3/col4 将参数横向排列
    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 1.5, 1.5, 1])

    with col1:
        # ✅ 局部变量 category_choice
        category_choice = st.selectbox(
            "检测场景", 
            ["aerial", "sar"],
            format_func=lambda x: "✈️ 航拍 (Aerial)" if x == "aerial" else "📡 雷达 (SAR)",
            key="vid_scene_select"
        )

    # 提取可用模型列表
    available_models = model_dict.get(category_choice, ["default"])

    with col2:

        model_choice = st.selectbox("选择模型权重", available_models, key="vid_model_select")

    with col3:

        conf_thres = st.slider("置信度", 0.0, 1.0, 0.35, key="vid_conf_slider")

    with col4:

        use_sahi = st.checkbox("开启 SAHI (高延迟)", value=False, key="vid_sahi_checkbox")

    with col5:

        fix_color = st.checkbox("🎨 颜色异常修复", value=True, help="如果看到颜色反转，请勾选此项")

    st.markdown("---")

    video_source = st.radio("选择视频源", ["本地视频文件", "实时摄像头 (Webcam)"], horizontal=True)

    st_frame = st.empty()
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1: kpi_frame = st.empty()
    with kpi2: kpi_obj = st.empty()
    with kpi3: kpi_fps = st.empty()



    stop_button = st.button("🔴 停止推流", type="secondary")

    cap = None

    # 初始化视频源
    if video_source == "本地视频文件":
        video_file = st.file_uploader("上传视频文件", type=['mp4', 'avi'])
        if video_file:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(video_file.read())
            cap = cv2.VideoCapture(tfile.name)
    elif video_source == "实时摄像头 (Webcam)":
        if st.checkbox("启动摄像头", key="start_webcam_checkbox"):
            cap = cv2.VideoCapture(0)

    # 主循环
    if cap is not None and cap.isOpened():

        # 确保启动摄像头后 stop_button 默认为 False，防止立即停止
        if 'stop_video_stream' not in st.session_state:
            st.session_state['stop_video_stream'] = False

        if stop_button:
            st.session_state['stop_video_stream'] = True

        frame_count = 0
        start_time = time.time()

        # ⚠️ 启动循环，直到用户点击停止或视频结束
        while cap.isOpened() and not st.session_state['stop_video_stream']:

            ret, frame = cap.read() # 这里读到的是 BGR
            if not ret:
                st.info("视频播放结束")
                break

            frame_count += 1
            if frame_count % VIDEO_FRAME_SKIP != 0:
                continue

            # === 核心处理：使用局部变量 ===
            processed_frame, obj_count = process_frame(
                frame, 
                model_choice,    # ✅ 局部变量
                category_choice, # ✅ 局部变量
                conf_thres       # ✅ 局部变量
            )


            final_image = processed_frame
            if fix_color:
                # 勾选时，将检测结果返回的 RGB 强制转换为 BGR
                # 目的是抵消 opencv 某些版本读取 BGR 时显示的颜色反转
                final_image = cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR)

            # === 显示 ===
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time if elapsed_time > 0 else 0

            # 始终告诉 Streamlit 内部是 RGB (即使我们做了 BGR 转换，显示时仍是 RGB)
            st_frame.image(final_image, channels="RGB", use_container_width=True)

            kpi_frame.metric("已处理帧", frame_count)
            kpi_obj.metric("当前帧目标", obj_count)
            kpi_fps.metric("FPS", f"{fps:.1f}")

        # 退出循环后
        cap.release()
        st.session_state['stop_video_stream'] = False # 重置停止标志

    elif cap is not None:
         # 确保 cap 释放
         cap.release()
         st.session_state['stop_video_stream'] = False