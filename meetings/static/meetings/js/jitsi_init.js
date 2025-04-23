function initJitsiMeet(room, containerSelector, options = {}) {
  const domain = window.JITSI_DOMAIN;   // наприклад 'meet.jit.si'
  console.log('[Jitsi] initJitsiMeet', { room, domain });

  const config = {
    roomName: room,
    parentNode: document.querySelector(containerSelector),

    // --- Отключаємо prejoin та lobby, щоб не було кнопок Sign in ---
    configOverwrite: {
      prejoinPageEnabled: false,
      enableWelcomePage: false,
      lobbyEnabled: false,
      ...options.configOverwrite
    },

    interfaceConfigOverwrite: {
      TOOLBAR_BUTTONS: [
        'microphone','camera','desktop','hangup','chat','tileview'
      ],
      ...options.interfaceConfigOverwrite
    },

    // Тут можуть бути jwt або userInfo, якщо використовуєте власний сервер
    jwt: options.jwt || null,
    userInfo: options.userInfo || {}
  };

  console.log('[Jitsi] creating ExternalAPI with config:', config);
  let api;
  window.APP_ENV = 'production';
  try {
    api = new JitsiMeetExternalAPI(domain, config);
  } catch (e) {
    console.error('[Jitsi] ExternalAPI init failed:', e);
    return;
  }

  api.addEventListener('errorOccurred', err =>
    console.error('[Jitsi] errorOccurred', err)
  );
  api.addEventListener('iframeLoaded', () =>
    console.log('[Jitsi] iframeLoaded')
  );
  api.addEventListener('videoConferenceJoined', () =>
    console.log('[Jitsi] videoConferenceJoined')
  );
  api.addEventListener('participantRoleChanged', evt =>
    console.log('[Jitsi] participantRoleChanged', evt)
  );

  return api;
}
