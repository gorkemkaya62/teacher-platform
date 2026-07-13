(function () {
  function initLockButtons() {
    document.querySelectorAll('.connto-lock-btn').forEach(function (button) {
      button.addEventListener('click', function (event) {
        var registerUrl = button.getAttribute('data-register-url') || button.getAttribute('href');
        if (!registerUrl) return;
        event.preventDefault();
        window.location.href = registerUrl;
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initLockButtons();
  });
})();
