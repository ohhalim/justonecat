import streamlit as st
from streamlit_extras.stylable_container import stylable_container

def card_container(**kwargs):
    return stylable_container(
        key=kwargs.get('key'),
        css_styles="""
            {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
            }
        """
    )