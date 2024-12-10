function chat_message_append(sourceEl, targetEl) {
  if (targetEl) {
    const markdownEl = targetEl.parentElement.querySelector(".markdown");
    targetEl.textContent += sourceEl.textContent;
    markdownEl.innerHTML = window.markdownToHtml(targetEl.textContent);
    if (window.hljs?.highlightElement) {
      markdownEl.querySelectorAll("code").forEach((block) => {
        window.hljs.highlightElement(block);
      });
    } else {
      console.warn("hljs module not found");
    }
  } else {
    console.warn("targetEl not found");
  }
}
