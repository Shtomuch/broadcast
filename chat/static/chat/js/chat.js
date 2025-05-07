document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const msgInput = document.getElementById("msg-input");
  const sendBtn = document.getElementById("send-btn");

  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  const roomSlug = chatBox.dataset.slug;
  const socket = new WebSocket(`${wsScheme}://${window.location.host}/ws/chat/${roomSlug}/`);

  socket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    const node = document.createElement("div");
    node.innerHTML = `<strong>${data.author}</strong> [${data.created}]: ${data.content}`;
    chatBox.appendChild(node);
    chatBox.scrollTop = chatBox.scrollHeight;
  };

  sendBtn.onclick = () => {
    if (msgInput.value.trim() !== "") {
      socket.send(JSON.stringify({ message: msgInput.value }));
      msgInput.value = "";
    }
  };
});
