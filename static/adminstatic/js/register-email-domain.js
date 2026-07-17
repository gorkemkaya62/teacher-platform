(function () {
  function syncCustomDomainField(scope) {
    var root = scope || document;
    root.querySelectorAll('.connto-field--email-domain').forEach(function (field) {
      var select = field.querySelector('.connto-email-domain-select');
      var wrap = field.querySelector('[data-email-custom-wrap]');
      if (!select || !wrap) {
        return;
      }

      var showCustom = select.value === 'custom';
      wrap.classList.toggle('connto-email-field__custom--hidden', !showCustom);
      var customInput = wrap.querySelector('.connto-email-domain-custom-input');
      if (customInput) {
        customInput.required = showCustom;
        if (!showCustom) {
          customInput.setCustomValidity('');
        }
      }
    });
  }

  function bindEmailDomainField(field) {
    var select = field.querySelector('.connto-email-domain-select');
    if (!select || select.dataset.emailDomainBound === 'true') {
      return;
    }

    select.dataset.emailDomainBound = 'true';
    select.addEventListener('change', function () {
      syncCustomDomainField(field.parentElement || document);
    });
  }

  function initEmailDomainFields(root) {
    var scope = root || document;
    scope.querySelectorAll('.connto-field--email-domain').forEach(bindEmailDomainField);
    syncCustomDomainField(scope);
  }

  window.initEmailDomainFields = initEmailDomainFields;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initEmailDomainFields(document);
    });
  } else {
    initEmailDomainFields(document);
  }
})();
