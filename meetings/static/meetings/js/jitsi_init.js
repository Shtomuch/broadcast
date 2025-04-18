function initJitsiMeet(room, containerSelector, options = {}) {
  const domain = window.JITSI_DOMAIN.replace(/^https?:\/\//, '');
  const config = {
    roomName: room,
    parentNode: document.querySelector(containerSelector),
    ...options
  };
  // Підключаємо API
  const api = new JitsiMeetExternalAPI(domain, config);

  // Слухаємо події запису
  api.addListener('recordingStatusChanged', (event) => {
    console.log('Recording status:', event.on, event.fileURL);
    if (event.on && event.fileURL) {
      alert('Запис доступний за адресою:\n' + event.fileURL);
    }
  });
}
