import streamlit as st


def get_share_button(cache_id:str):
    """share button
    ```python
        import streamlit.components.v1 as components
        components.html(get_share_button("dasd"))
    ```
    """
    # 自定义的 JavaScript 和 HTML，用于实现点击复制功能
    copy_button_html = f"""
        <button id="copyButton">share</button>
        <textarea id="markdownContent" style="position:absolute;left:-9999px;">{cache_id}</textarea>
        <script>
            document.getElementById('copyButton').onclick = function() {{
                var url = window.parent.location.href.split('?')[0];
                var copyText = document.getElementById('markdownContent').value;
                var shareLink = url + "?c=" + copyText;
                var tempInput = document.createElement('textarea');
                tempInput.value = shareLink;
                document.body.appendChild(tempInput);
                tempInput.select();
                document.execCommand('copy');
                document.body.removeChild(tempInput);
                alert('内容已复制到剪贴板: ' + shareLink);
            }}
        </script>
    """
    return copy_button_html
def get_copy_script(cache_id: str):
    """Generate HTML and JavaScript to copy text to clipboard."""
    copy_script_html = f"""
        <script>
            function copyToClipboard() {{
                var url = window.parent.location.href.split('?')[0];
                var shareLink = url + "?c={cache_id}";
                var tempInput = document.createElement('textarea');
                tempInput.value = shareLink;
                document.body.appendChild(tempInput);
                tempInput.select();
                document.execCommand('copy');
                document.body.removeChild(tempInput);
                alert('内容已复制到剪贴板: ' + shareLink);
            }}
            copyToClipboard();
        </script>
    """
    return copy_script_html
# def load_share_button(cache_id: str):
#     """生成一个可点击的按钮，点击后复制分享链接"""
#     copy_button_html = f"""
#         <textarea id="markdownContent" style="position:absolute;left:-9999px;">{cache_id}</textarea>
#         <button id="copyButton" style="padding: 8px; background-color: #007bff; color: white; border: none; cursor: pointer; border-radius: 5px;">复制分享链接</button>
#         <script>
#             document.getElementById("copyButton").onclick = function() {{
#                 var url = window.parent.location.href.split('?')[0];
#                 var copyText = document.getElementById('markdownContent').value;
#                 var shareLink = url + "?c=" + copyText;

#                 // 现代浏览器使用 Clipboard API
#                 if (navigator.clipboard && navigator.clipboard.writeText) {{
#                     navigator.clipboard.writeText(shareLink).then(function() {{
#                         alert('内容已复制到剪贴板: ' + shareLink);
#                     }}, function(err) {{
#                         console.error('复制失败:', err);
#                         fallbackCopyTextToClipboard(shareLink);
#                     }});
#                 }} else {{
#                     fallbackCopyTextToClipboard(shareLink);
#                 }}
#             }};

#             function fallbackCopyTextToClipboard(text) {{
#                 var tempInput = document.createElement('textarea');
#                 tempInput.value = text;
#                 document.body.appendChild(tempInput);
#                 tempInput.select();
#                 try {{
#                     document.execCommand('copy');
#                     alert('内容已复制到剪贴板: ' + text);
#                 }} catch (err) {{
#                     console.error('复制失败:', err);
#                 }}
#                 document.body.removeChild(tempInput);
#             }}
#         </script>
#     """
#     return copy_button_html


# def load_share_button(cache_id: str):
#     """share button
#     ```python
#         import streamlit.components.v1 as components
#         components.html(get_share_button("dasd"))
#     ```
#     """
#     # 自定义的 JavaScript 和 HTML，用于实现点击复制功能
#     copy_button_html = f"""
#         <script>
#             window.onload = function() {{
#                 var url = window.parent.location.href.split('?')[0];
#                 var copyText = "{cache_id}";
#                 var shareLink = url + "?c=" + copyText;

#                 // 现代浏览器使用 Clipboard API
#                 if (navigator.clipboard && navigator.clipboard.writeText) {{
#                     navigator.clipboard.writeText(shareLink).then(function() {{
#                         alert('navigator内容已复制到剪贴板: ' + shareLink);
#                     }}, function(err) {{
#                         console.error('navigator复制失败:', err);
#                         fallbackCopyTextToClipboard(shareLink);
#                     }});
#                 }} else {{
#                     fallbackCopyTextToClipboard(shareLink);
#                 }}
#             }};
#             function fallbackCopyTextToClipboard(text) {{
#                 var tempInput = document.createElement('textarea');
#                 tempInput.value = text;
#                 document.body.appendChild(tempInput);
#                 tempInput.select();
#                 try {{
#                     document.execCommand('copy');
#                     alert('execCommand内容已复制到剪贴板: ' + text);
#                 }} catch (err) {{
#                     console.error('execCommand复制失败:', err);
#                 }}
#                 document.body.removeChild(tempInput);
#             }}
#         </script>
#     """
#     return copy_button_html


def load_share_button(cache_id: str):
    """share button
    ```python
        import streamlit.components.v1 as components
        components.html(get_share_button("dasd"))
    ```
    """
    # 自定义的 JavaScript 和 HTML，用于实现点击复制功能
    copy_button_html = f"""
        <script>
            console.log('log');
            function copyShareLink(cacheId) {{
                var url = window.parent.location.href.split('?')[0];
                var shareLink = url + "?c=" + cacheId;
                // 现代浏览器使用 Clipboard API
                if (navigator.clipboard && navigator.clipboard.writeText) {{
                    navigator.clipboard.writeText(shareLink).then(function() {{
                        alert('navigator内容已复制到剪贴板: ' + shareLink);
                    }}, function(err) {{
                        console.error('navigator复制失败:', err);
                        fallbackCopyTextToClipboard(shareLink);
                    }});
                }} else {{
                    fallbackCopyTextToClipboard(shareLink);
                }}
            }}

            function fallbackCopyTextToClipboard(text) {{
                var tempInput = document.createElement('textarea');
                tempInput.value = text;
                document.body.appendChild(tempInput);
                tempInput.select();
                try {{
                    document.execCommand('copy');
                    alert('execCommand内容已复制到剪贴板: ' + text);
                }} catch (err) {{
                    console.error('execCommand复制失败:', err);
                }}
                document.body.removeChild(tempInput);
            }}
        </script>
    """
    return copy_button_html
