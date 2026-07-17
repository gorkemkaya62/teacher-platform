(function () {
  function bindPasswordToggleButton(button, input) {
    if (!button || !input || button.dataset.passwordToggleBound === 'true') {
      return;
    }

    button.dataset.passwordToggleBound = 'true';

    button.addEventListener('click', function () {
      var show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      button.setAttribute('aria-pressed', show ? 'true' : 'false');
      button.setAttribute('aria-label', show ? 'Şifreyi gizle' : 'Şifreyi göster');

      var icon = button.querySelector('i');
      if (icon) {
        icon.classList.toggle('fa-eye', !show);
        icon.classList.toggle('fa-eye-slash', show);
      }
    });
  }

  function enhancePasswordInput(input) {
    if (!input || input.dataset.passwordToggleEnhanced === 'true') {
      return;
    }

    var existingWrapper = input.closest('.connto-password-field, .connto-input-icon--password');
    var existingToggle = existingWrapper
      ? existingWrapper.querySelector('.connto-password-toggle')
      : null;

    if (existingToggle) {
      bindPasswordToggleButton(existingToggle, input);
      input.dataset.passwordToggleEnhanced = 'true';
      return;
    }

    var wrapper = document.createElement('div');
    wrapper.className = 'connto-password-field';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    input.dataset.passwordToggleEnhanced = 'true';
    input.classList.add('connto-password-input');

    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'connto-password-toggle';
    button.setAttribute('aria-label', 'Şifreyi göster');
    button.setAttribute('aria-pressed', 'false');
    button.innerHTML = '<i class="fa fa-eye" aria-hidden="true"></i>';
    wrapper.appendChild(button);
    bindPasswordToggleButton(button, input);
  }

  function initPasswordToggles(root) {
    var scope = root || document;
    scope.querySelectorAll('input[type="password"]').forEach(enhancePasswordInput);
  }

  window.initPasswordToggles = initPasswordToggles;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initPasswordToggles(document);
    });
  } else {
    initPasswordToggles(document);
  }
})();
