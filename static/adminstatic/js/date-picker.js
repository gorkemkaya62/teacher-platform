(function () {
  function openDatePicker(input) {
    if (!input) {
      return;
    }
    input.focus();
    if (typeof input.showPicker === 'function') {
      try {
        input.showPicker();
      } catch (err) {
        input.click();
      }
    }
  }

  function ensureDateFieldWrapper(input) {
    var wrap = input.closest('.connto-date-field');
    if (!wrap) {
      wrap = document.createElement('div');
      wrap.className = 'connto-date-field';
      input.parentNode.insertBefore(wrap, input);
      wrap.appendChild(input);
    }

    if (!wrap.querySelector('.connto-date-trigger')) {
      var trigger = document.createElement('button');
      trigger.type = 'button';
      trigger.className = 'connto-date-trigger';
      trigger.setAttribute('aria-label', 'Takvimden tarih seç');
      trigger.setAttribute('tabindex', '-1');
      trigger.innerHTML = '<i class="fa fa-calendar" aria-hidden="true"></i>';
      wrap.appendChild(trigger);
    }

    return wrap;
  }

  function bindDatePicker(input) {
    if (!input || input.dataset.datePickerBound === 'true') {
      return;
    }

    input.dataset.datePickerBound = 'true';
    input.classList.add('connto-date-picker');

    var wrap = ensureDateFieldWrapper(input);
    var trigger = wrap ? wrap.querySelector('.connto-date-trigger') : null;

    input.addEventListener('keydown', function (event) {
      if (event.key === 'Tab' || event.key === 'Escape') {
        return;
      }
      event.preventDefault();
    });

    input.addEventListener('paste', function (event) {
      event.preventDefault();
    });

    input.addEventListener('click', function () {
      openDatePicker(input);
    });

    if (trigger) {
      trigger.addEventListener('click', function () {
        openDatePicker(input);
      });
    }

    input.addEventListener('change', function () {
      if (input.getAttribute('data-register-min-age') && typeof window.validateRegisterBirthDateInput === 'function') {
        window.validateRegisterBirthDateInput(input, { showPopup: true });
      }
    });
  }

  function initDatePickers(root) {
    var scope = root || document;
    scope.querySelectorAll('input[type="date"], .connto-date-picker').forEach(bindDatePicker);
  }

  window.initDatePickers = initDatePickers;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initDatePickers(document);
    });
  } else {
    initDatePickers(document);
  }
})();
