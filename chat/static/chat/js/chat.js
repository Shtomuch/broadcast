document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const msgInput = document.getElementById("msg-input");
  const sendBtn = document.getElementById("send-btn");
  const fileInput = document.getElementById("file-input");
  const uploadBtn = document.getElementById("upload-btn");

  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  const roomSlug = chatBox.dataset.slug;
  const socket = new WebSocket(`${wsScheme}://${window.location.host}/ws/chat/${roomSlug}/`);

  socket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    const node = document.createElement("div");
    let content = "";
    if (data.content) content += data.content;
    if (data.file_url) {
      content += ` <a href="${data.file_url}" download>📎 файл</a>`;
    }
    node.innerHTML = `<strong>${data.author}</strong> [${data.created}]: ${content}`;
    chatBox.appendChild(node);
    chatBox.scrollTop = chatBox.scrollHeight;
  };

  sendBtn.onclick = () => {
    if (msgInput.value.trim() === "") return;
    if (socket.readyState !== WebSocket.OPEN) {
      console.warn("WebSocket is not open");
      return;
    }
    socket.send(JSON.stringify({ message: msgInput.value }));
    msgInput.value = "";
  };

  if (uploadBtn) {
    function getCsrfToken() {
      const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
      return input ? input.value : '';
    }
    uploadBtn.onclick = () => {
      if (!fileInput.files.length) return;
      const formData = new FormData();
      formData.append('file', fileInput.files[0]);
      fetch(`/chat/r/${roomSlug}/upload/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
        body: formData,
      }).then(() => { fileInput.value = '' });
    };
  }
});
