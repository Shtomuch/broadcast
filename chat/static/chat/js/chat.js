document.addEventListener('DOMContentLoaded', () => {
  const chatLog = document.querySelector('#chat-log');
  const chatForm = document.querySelector('#chat-form');
  const chatInput = document.querySelector('#chat-input');
  const fileInput = document.querySelector('#file-input');

  // WebSocket
  const socket = new WebSocket(wsPath);
  socket.onopen = () => console.log('WebSocket connected');
  socket.onclose = () => console.log('WebSocket disconnected');
  socket.onmessage = e => {
    const data = JSON.parse(e.data);
    const el = document.createElement('div');
    let html = `[${data.timestamp}] <strong>${data.username}:</strong> ${data.message}`;
    if (data.attachment_url) {
      html += ` <a href="${data.attachment_url}" target="_blank">📎 файл</a>`;
    }
    el.innerHTML = html;
    chatLog.appendChild(el);
    chatLog.scrollTop = chatLog.scrollHeight;
  };

  // відправка тексту
  chatForm.addEventListener('submit', e => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;
    socket.send(JSON.stringify({ message: text }));
    chatInput.value = '';
  });

  // обробка завантаження файлу
  fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    fetch(`/chat/rooms/${roomSlug}/upload/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: formData
    })
    .then(resp => resp.json())
    .then(data => {
      // локально виведемо одразу
      const el = document.createElement('div');
      el.innerHTML = `[${data.timestamp}] <strong>${data.username}:</strong> <a href="${data.attachment_url}" target="_blank">📎 файл</a>`;
      chatLog.appendChild(el);
      chatLog.scrollTop = chatLog.scrollHeight;
      fileInput.value = '';
    })
    .catch(err => console.error('Upload error:', err));
  });
});
