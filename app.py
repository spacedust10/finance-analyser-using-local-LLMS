import streamlit as st
import streamlit.components.v1 as components
from config.settings import AppConfig
from config.styles import AppStyles
from services.file_service import FileService
from services.analysis_service import FinancialAnalysisService
from ui.components.sidebar import Sidebar
from ui.pages.dashboard import DashboardPage
from ui.pages.assistant import AssistantPage
from ui.pages.documents import DocumentsPage
from utils.state_manager import StateManager

VIEWS = ["Dashboard", "Assistant", "Documents"]

def main():
    """Main application entry point"""
    app_config = AppConfig()

    st.set_page_config(
        page_title=app_config.page_title,
        page_icon="▤",
        layout=app_config.layout,
        initial_sidebar_state=app_config.initial_sidebar_state
    )

    theme = st.context.theme.type or "dark"
    st.markdown(AppStyles.css(theme), unsafe_allow_html=True)
    # theme-sync: menu theme switches don't rerun Python; this hidden button
    # is clicked by the observer script so CSS and charts follow immediately
    st.button("·", key="theme_refresh")
    components.html(AppStyles.theme_sync_script(theme), height=0)

    StateManager.initialize()

    sidebar = Sidebar(FileService())
    sidebar.render()

    st.markdown(AppStyles.MASTHEAD_HTML, unsafe_allow_html=True)

    default = StateManager.get_view() if StateManager.get_view() in VIEWS else VIEWS[0]
    nav = st.segmented_control(
        "View", VIEWS, default=default, label_visibility="collapsed"
    ) or default
    StateManager.set_view(nav)

    if nav == "Dashboard":
        DashboardPage(FinancialAnalysisService()).render(theme)
    elif nav == "Assistant":
        AssistantPage().render()
    else:
        DocumentsPage().render()

if __name__ == "__main__":
    main()
