// static/chat/js/chat.js
document.addEventListener('DOMContentLoaded', () => {
  /* ---------- DOM ---------- */
  const chatBox   = document.getElementById('chat-box');
  const msgInput  = document.getElementById('msg-input');
  const sendBtn   = document.getElementById('send-btn');
  const fileInput = document.getElementById('file-input');
  const uploadBtn = document.getElementById('upload-btn');
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';


  /* ---------- Logger ---------- */
  const log = {
    info : (...args) => console.log('%c[Chat]', 'color:#0d6efd; font-weight:bold;', ...args),
    warn : (...args) => console.warn('[Chat]', ...args),
    error: (...args) => console.error('[Chat]', ...args)
  };

  /* ---------- Утиліти ---------- */
  function escapeHTML(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
  }

  function setInputsDisabled(disabled) {
    if (msgInput) msgInput.disabled = disabled;
    if (sendBtn) sendBtn.disabled = disabled;
    if (fileInput) fileInput.disabled = disabled;
    if (uploadBtn) uploadBtn.disabled = disabled;
    log.info(`Inputs ${disabled ? 'disabled' : 'enabled'}.`);
  }

  // Перевірка наявності основних елементів
  if (!chatBox) {
    log.error('Критичний елемент #chat-box не знайдено!');
    return;
  }
  if (msgInput && !sendBtn) log.warn('#send-btn не знайдено, надсилання текстових повідомлень може не працювати.');
  if (fileInput && !uploadBtn) log.warn('#upload-btn не знайдено, завантаження файлів може не працювати.');


  /* ---------- WebSocket ---------- */
  const wsScheme  = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const roomSlug  = chatBox.dataset.slug;

  if (!roomSlug) {
    log.error('Атрибут data-slug для кімнати чату не знайдено на #chat-box!');
    if (msgInput || uploadBtn) setInputsDisabled(true); // Блокуємо ввід, якщо немає slug
    return;
  }

  const socketUrl = `${wsScheme}://${window.location.host}/ws/chat/${roomSlug}/`;
  log.info('Підключення до WebSocket:', socketUrl);
  appendTemporaryMessage('Підключення до чату...', 'info');

  const socket = new WebSocket(socketUrl);

  socket.onopen = () => {
    removeTemporaryMessage();
    log.info('WebSocket з\'єднано успішно.');
    appendTemporaryMessage('З\'єднано!', 'success', 2000);
    if (msgInput || uploadBtn) setInputsDisabled(false); // Розблоковуємо після успішного з'єднання
  };

  socket.onclose = e => {
    removeTemporaryMessage();
    log.warn('WebSocket закрито.', `Код: ${e.code}, Причина: "${e.reason}", Чисто: ${e.wasClean}`);
    appendTemporaryMessage(`Зв'язок втрачено (код: ${e.code}). Спробуйте оновити сторінку.`, 'error');
    if (msgInput || uploadBtn) setInputsDisabled(true);
  };

  socket.onerror = e => {
    removeTemporaryMessage();
    log.error('WebSocket помилка:', e);
    appendTemporaryMessage('Помилка WebSocket. Деталі в консолі.', 'error');
    // setInputsDisabled(true) вже буде викликано в onclose, який зазвичай слідує за onerror
  };

  socket.onmessage = e => {
    try {
      const data = JSON.parse(e.data);
      log.info('WebSocket: Отримано повідомлення:', data);

      // Перевірка типу повідомлення (якщо сервер надсилає)
      // if (data.type !== 'chat_message') {
      //   log.info('Отримано нетипове повідомлення:', data);
      //   return;
      // }

      // Екранування даних перед вставкою в HTML
      const author = escapeHTML(data.author || 'Анонім');
      const created = escapeHTML(data.created || ''); // Припускаємо, що час вже відформатовано
      const content = data.content ? escapeHTML(data.content) : '';

      const messageDiv = document.createElement('div');
      let innerHTML = `<strong>${author}</strong> [${created}]: `;

      if (content) {
        innerHTML += content; // Вже екранований текст
      }

      if (data.file_url) {
        const filename = escapeHTML(data.filename || 'файл'); // Використовуємо data.filename
        innerHTML += ` <a href="${escapeHTML(data.file_url)}" download="${filename}" class="link-secondary ms-1">📎 ${filename}</a>`;
      }

      messageDiv.innerHTML = innerHTML;
      chatBox.appendChild(messageDiv);
      chatBox.scrollTop = chatBox.scrollHeight;

    } catch (err) {
      log.error('Помилка обробки або рендерингу повідомлення:', err, 'Отримані дані:', e.data);
    }
  };

  /* ---------- Тимчасові повідомлення в чаті ---------- */
  let tempMsgIdCounter = 0;
  function appendTemporaryMessage(text, type = 'info', duration = 0) {
    const tempMsgId = `temp-msg-${tempMsgIdCounter++}`;
    const messageDiv = document.createElement('div');
    messageDiv.id = tempMsgId;
    messageDiv.style.padding = '5px';
    messageDiv.style.fontSize = '0.9em';
    messageDiv.style.textAlign = 'center';
    if (type === 'error') {
      messageDiv.style.color = 'red';
      messageDiv.style.fontWeight = 'bold';
    } else if (type === 'success') {
      messageDiv.style.color = 'green';
    } else {
      messageDiv.style.color = '#6c757d'; // Bootstrap secondary
    }
    messageDiv.textContent = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    if (duration > 0) {
      setTimeout(() => removeTemporaryMessage(tempMsgId), duration);
    }
    return tempMsgId;
  }

  function removeTemporaryMessage(id) {
    const query = id ? `#${id}` : '[id^="temp-msg-"]'; // Видалити конкретне або всі тимчасові
    document.querySelectorAll(query).forEach(el => el.remove());
  }


  /* ---------- Відправка тексту ---------- */
  const sendMessage = () => {
    if (!msgInput) return; // Якщо поля вводу немає
    const text = msgInput.value.trim();
    if (!text) {
      msgInput.focus();
      return;
    }
    if (socket.readyState !== WebSocket.OPEN) {
      log.warn('WebSocket не відкрито. Повідомлення не надіслано.');
      appendTemporaryMessage('Неможливо надіслати: зв\'язок не встановлено.', 'error', 3000);
      return;
    }

    const payload = { message: text }; // На сервері ваш consumer має розпарсити це JSON повідомлення
    try {
      socket.send(JSON.stringify(payload));
      log.info('WebSocket: Надіслано текстове повідомлення:', payload);
      msgInput.value = '';
      msgInput.focus();
    } catch (err) {
      log.error('Помилка при надсиланні WebSocket повідомлення:', err);
      appendTemporaryMessage('Помилка надсилання повідомлення.', 'error', 3000);
    }
  };

  if (sendBtn && msgInput) {
    sendBtn.addEventListener('click', sendMessage);
    msgInput.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }


  /* ---------- Завантаження файлу ---------- */
  if (uploadBtn && fileInput && csrfToken) {
    uploadBtn.addEventListener('click', async () => {
      if (!fileInput.files || fileInput.files.length === 0) {
        log.info('Файл для завантаження не вибрано.');
        // Можна додати тимчасове повідомлення, якщо файл не вибрано
        appendTemporaryMessage('Будь ласка, виберіть файл.', 'info', 2000);
        return;
      }
      if (socket.readyState !== WebSocket.OPEN) {
        log.warn('WebSocket не відкрито. Завантаження файлу скасовано.');
        appendTemporaryMessage('Неможливо завантажити: зв\'язок не встановлено.', 'error', 3000);
        return;
      }

      const fileToUpload = fileInput.files[0];
      const formData = new FormData();
      formData.append('file', fileToUpload); // На сервері очікуємо поле 'file'

      setInputsDisabled(true); // Блокуємо інпути на час завантаження
      const tempUploadMsgId = appendTemporaryMessage(`Завантаження файлу: ${escapeHTML(fileToUpload.name)}...`, 'info');

      try {
        log.info('Розпочато завантаження файлу:', fileToUpload.name, `(${Math.round(fileToUpload.size / 1024)}KB)`);
        const response = await fetch(`/chat/r/${roomSlug}/upload/`, { // Переконайтесь, що URL правильний
          method: 'POST',
          headers: { 'X-CSRFToken': csrfToken },
          body: formData
        });

        removeTemporaryMessage(tempUploadMsgId); // Видаляємо повідомлення "Завантаження..."

        if (!response.ok) {
          let errorText = `Помилка ${response.status} (${response.statusText})`;
          try {
            const errorData = await response.json();
            errorText = errorData.error || errorData.detail || errorText; // Спробувати отримати деталі помилки з JSON
          } catch (e) { /* Ігноруємо, якщо відповідь не JSON */ }
          throw new Error(errorText);
        }

        const responseData = await response.json(); // Припускаємо, що сервер повертає JSON
        log.info('Файл успішно завантажено. Відповідь сервера:', responseData);
        // Сервер має надіслати WebSocket повідомлення про цей файл,
        // тому клієнт тут нічого не рендерить, а чекає на socket.onmessage.
        fileInput.value = ''; // Очищуємо поле вибору файлу
        appendTemporaryMessage(`Файл "${escapeHTML(fileToUpload.name)}" завантажено.`, 'success', 3000);

      } catch (err) {
        removeTemporaryMessage(tempUploadMsgId);
        log.error('Помилка завантаження файлу:', err);
        appendTemporaryMessage(`Помилка завантаження: ${err.message}`, 'error', 5000);
      } finally {
        setInputsDisabled(false); // Розблоковуємо інпути
      }
    });
  } else if (uploadBtn || fileInput) {
      log.warn('Елементи для завантаження файлу (кнопка, поле вводу або CSRF токен) не повністю налаштовані.');
  }

  // Початкове розблокування інпутів, якщо WebSocket ще не відкрився
  // (onopen їх розблокує, якщо з'єднання успішне)
  if (socket.readyState !== WebSocket.OPEN) {
    if (msgInput || uploadBtn) setInputsDisabled(true);
  }

});