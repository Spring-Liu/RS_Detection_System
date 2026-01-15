# frontend/tabs/admin_tab.py (重构最终版：专注于稳定和可读性)

import streamlit as st
import requests
import pandas as pd
from utils.config import BACKEND_URL
from utils.api_client import upload_new_model, get_remote_model_list, delete_remote_model

# --- 1. API 调用辅助函数 (保持不变) ---
def get_all_users():
    token = st.session_state.get("token")
    if not token: return None
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers, timeout=5)
        if response.status_code == 200: return response.json()
        st.error(f"获取用户列表失败: {response.status_code} - {response.json().get('detail', '权限或网络错误')}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"网络请求错误: {e}")
        return None

def update_user_role(username, new_role):
    token = st.session_state.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.put(
            f"{BACKEND_URL}/admin/users/{username}/role", 
            params={"role": new_role}, 
            headers=headers, 
            timeout=5
        )
        if response.status_code == 200: return True, "角色更新成功"
        return False, response.json().get('detail', '更新角色失败')
    except requests.exceptions.RequestException as e:
        return False, str(e)

def delete_user(username):
    token = st.session_state.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(f"{BACKEND_URL}/admin/users/{username}", headers=headers, timeout=5)
        if response.status_code == 200: return True, "用户删除成功"
        return False, response.json().get('detail', '删除用户失败')
    except requests.exceptions.RequestException as e:
        return False, str(e)
# --- 2. 核心模型操作回调函数 ---
def set_delete_candidate(filename: str, category: str):
    """设置待删除的模型，触发确认对话框"""
    # 状态键已在 app.py 中初始化，这里可以直接访问
    st.session_state['delete_candidate']['filename'] = filename
    st.session_state['delete_candidate']['category'] = category
    st.session_state['show_delete_confirm'] = True 
    st.rerun()
def perform_model_deletion(filename: str, category: str):
    """执行模型删除操作并处理结果"""
    with st.spinner(f"正在删除 {filename}..."):
        success, msg = delete_remote_model(filename, category)
        if success:
            st.success(f"✅ {msg}")
            if "model_dict" in st.session_state:
                del st.session_state["model_dict"]
        else:
            st.error(f"❌ 操作失败: {msg}")
        
        # 无论成功失败，都清除确认状态
        st.session_state['delete_candidate'] = {'filename': None, 'category': None}
        st.session_state['show_delete_confirm'] = False
        st.rerun()
def cancel_deletion():
    """取消删除操作"""
    st.session_state['delete_candidate'] = {'filename': None, 'category': None}
    st.session_state['show_delete_confirm'] = False
    # 不需要 rerun，因为清除状态后页面会自动重绘
# --- 3. 模型管理模块渲染 ---
def render_model_management():
    """渲染模型管理模块（上传、列表展示和删除操作）"""
    st.subheader("⚙️ 模型管理与部署")
    st.markdown("---") 


    if st.session_state.get('show_delete_confirm', False):
        candidate = st.session_state['delete_candidate']
        filename = candidate['filename']
        category = candidate['category']
        
        if filename:
            # 使用一个 Expander 或 Info Box 来组织确认区域
            st.warning(f"⚠️ 确认永久删除模型文件：**{filename}** (场景: {category})？此操作不可逆！", icon="🚨")
            
            confirm_col, cancel_col, _ = st.columns([1, 1, 4])
            
            with confirm_col:
                st.button(
                    "✅ 确认删除", 
                    key="final_confirm_delete_btn", 
                    type="primary", 
                    on_click=perform_model_deletion, 
                    args=(filename, category)
                )
            
            with cancel_col:
                st.button(
                    "❌ 取消", 
                    key="cancel_delete_btn",
                    on_click=cancel_deletion 
                )
            
            st.markdown("---") # 确保确认框下方有一个分隔线
        else:
            # 清理状态以防万一
            cancel_deletion()

    col_upload, col_list = st.columns([1, 3])
    # ----------------------------------------
    # 左侧 1：上传卡片
    # ----------------------------------------
    with col_upload:
        with st.container(border=True):
            st.markdown("#### 📤 模型文件上传")
            
            model_category = st.radio(
                "选择模型场景",
                ("aerial", "sar"),
                format_func=lambda x: "✈️ 航拍检测" if x == "aerial" else "📡 SAR 检测",
                key="admin_model_cat_upload"
            )
            
            uploaded_model = st.file_uploader(f"上传 {model_category} 模型 (.pt)", type=['pt'])
            
            # 禁用上传按钮，如果删除确认框正在显示
            upload_disabled = st.session_state.get('show_delete_confirm', False)
            if uploaded_model:
                if st.button("确认上传并加载", type="primary", use_container_width=True, disabled=upload_disabled):
                    with st.spinner("正在上传..."):
                        success, msg = upload_new_model(
                            uploaded_model.getvalue(), 
                            uploaded_model.name,
                            model_category 
                        )
                        if success:
                            st.success(f"✅ {msg}")
                            if "model_dict" in st.session_state: 
                                del st.session_state["model_dict"]
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                            
            if st.button("🔄 刷新模型列表", key="model_refresh_btn", use_container_width=True, disabled=upload_disabled):
                 if "model_dict" in st.session_state:
                     del st.session_state["model_dict"]
                 st.rerun()

    with col_list:
        with st.container(border=True):
            st.markdown("#### 📋 当前生效模型库")
            
            tab_aerial, tab_sar = st.tabs(["✈️ 航拍模型", "📡 SAR 模型"])
            
            current_models = get_remote_model_list()
            
            if not isinstance(current_models, dict):
                st.warning("⚠️ 数据格式异常，无法解析模型列表")
                return

            # 禁用列表按钮，如果删除确认框正在显示
            list_disabled = st.session_state.get('show_delete_confirm', False)

            # --- 列表渲染辅助函数 ---
            def render_model_list_with_delete(model_list, category):
                if not model_list:
                    st.info(f"暂无 {category} 模型", icon="📂")
                    return

                # 列表头部
                header_cols = st.columns([0.65, 0.25, 0.2])
                header_cols[0].markdown("**模型文件名**")
                header_cols[2].markdown("**操作**")
                st.markdown("---")

                for model_name in model_list:
                    delete_key = f"set_delete_{category}_{model_name}"
                    
                    model_cols = st.columns([0.65, 0.25, 0.2], gap="small")

                    # 第一列：文件名
                    model_cols[0].code(model_name)
                    # 第三列：删除按钮
                    model_cols[2].button(
                        "🗑️ 删除", 
                        key=delete_key, 
                        type="secondary", 
                        use_container_width=True,
                        disabled=list_disabled, # 确认对话框出现时禁用列表按钮
                        on_click=set_delete_candidate,
                        args=(model_name, category)
                    )
            # --- Tab 1 & 2 渲染 ---
            with tab_aerial:
                render_model_list_with_delete(current_models.get("aerial", []), "aerial")

            with tab_sar:
                render_model_list_with_delete(current_models.get("sar", []), "sar")
# --- 4. 用户管理模块 (保持不变) ---
def render_user_management():
    st.subheader("👥 用户管理与权限控制")
    st.markdown("---")

    # 1. 刷新逻辑
    if st.button("🔄 刷新用户数据", key="user_refresh_top_btn"):
        st.session_state["user_list_cache"] = get_all_users()
        st.rerun()

    if "user_list_cache" not in st.session_state:
        st.session_state["user_list_cache"] = get_all_users()

    user_data = st.session_state.get("user_list_cache")
    if not user_data:
        st.info("暂无用户数据或权限不足。", icon="❗")
        return

    # 2. 转换为 DataFrame 方便处理
    df = pd.DataFrame(user_data)

    # 3. 仿照模型管理的列表渲染
    with st.container(border=True):
        st.markdown("#### 📋 系统用户列表")

        # 列表头部
        h_cols = st.columns([0.3, 0.3, 0.25, 0.15])
        h_cols[0].markdown("**用户名**")
        h_cols[1].markdown("**创建时间**")
        h_cols[2].markdown("**角色权限**")
        h_cols[3].markdown("**操作**")
        st.markdown("---")

        # 循环渲染每一行用户
        for _, row in df.iterrows():
            uname = row['username']
            urole = row['role']
            utime = row['created_at']

            u_cols = st.columns([0.3, 0.3, 0.25, 0.15], vertical_alignment="center")

            # 第一列：用户名
            u_cols[0].code(uname)

            # 第二列：时间
            u_cols[1].text(utime)

            # 第三列：角色选择（仿照模型管理的交互，直接在行内放置下拉框）
            new_role = u_cols[2].selectbox(
                "角色",
                ["user", "admin"],
                index=(0 if urole == 'user' else 1),
                key=f"role_sel_{uname}",
                label_visibility="collapsed"
            )

            # 检查角色是否发生变化，若变化则触发更新
            if new_role != urole:
                if uname == st.session_state.get("username"):
                    st.toast("⚠️ 不能修改自己的角色", icon="❌")
                else:
                    success, msg = update_user_role(uname, new_role)
                    if success:
                        st.toast(f"✅ {uname} 已设为 {new_role}")
                        del st.session_state["user_list_cache"]
                        st.rerun()
                    else:
                        st.error(msg)

            # 第四列：删除按钮（核心修改点）
            if uname == st.session_state.get("username"):
                u_cols[3].button("🚫", key=f"del_self_{uname}", disabled=True, help="不能删除自己")
            else:
                if u_cols[3].button("🗑️", key=f"del_btn_{uname}", type="secondary", use_container_width=True):

                    with st.spinner(f"正在删除 {uname}..."):
                        success, msg = delete_user(uname)
                        if success:
                            st.success(f"用户 {uname} 已删除")
                            del st.session_state["user_list_cache"]
                            st.rerun()
                        else:
                            st.error(msg)
            st.markdown("<hr style='margin:0.5rem 0; opacity:0.2'>", unsafe_allow_html=True)


# --- 5. 总管理员 Tab 渲染函数 ---
def render_admin_tab():
    st.title("🛡️ 系统管理中心")
    st.markdown("欢迎来到管理员后台，请在左侧选择操作模块。")
    st.markdown("---")

    nav_col, content_col = st.columns([1, 4])

    with nav_col:
        st.markdown("##### 模块选择")
        admin_module = st.radio(
            "选择管理模块",
            options=[
                "模型管理", 
                "用户管理"
            ],
            index=0,
            key="admin_main_nav",
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.info("💡 提示：所有操作需谨慎，直接影响系统稳定性。", icon="⚠️")

    with content_col:
        if admin_module == "模型管理":
            render_model_management()
        elif admin_module == "用户管理":
            render_user_management()