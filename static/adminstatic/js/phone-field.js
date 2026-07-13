(function () {
  function normalizePhoneInput(input) {
    if (!input) return;
    var value = input.value.replace(/\D/g, '');
    if (value.startsWith('0')) {
      value = value.replace(/^0+/, '');
    }
    input.value = value;
  }

  function closePicker(picker) {
    var list = picker.querySelector('.connto-phone-country-picker__list');
    var trigger = picker.querySelector('.connto-phone-country-picker__trigger');
    if (!list || !trigger) return;
    list.hidden = true;
    trigger.setAttribute('aria-expanded', 'false');
    picker.classList.remove('connto-phone-country-picker--open');
  }

  function openPicker(picker) {
    var list = picker.querySelector('.connto-phone-country-picker__list');
    var trigger = picker.querySelector('.connto-phone-country-picker__trigger');
    if (!list || !trigger) return;
    list.hidden = false;
    trigger.setAttribute('aria-expanded', 'true');
    picker.classList.add('connto-phone-country-picker--open');
    var selected = list.querySelector('[aria-selected="true"]');
    if (selected) {
      selected.scrollIntoView({ block: 'nearest' });
    }
  }

  function setPickerValue(picker, code, iso, flag) {
    var select = picker.querySelector('.connto-phone-code-native');
    var trigger = picker.querySelector('.connto-phone-country-picker__trigger');
    var flagImg = picker.querySelector('.connto-phone-country-picker__flag');
    var dial = picker.querySelector('.connto-phone-country-picker__dial');
    var list = picker.querySelector('.connto-phone-country-picker__list');

    if (select) {
      select.value = code;
      select.dispatchEvent(new Event('change', { bubbles: true }));
    }
    if (flagImg && flag) {
      flagImg.src = flag;
    }
    if (dial) {
      dial.textContent = code;
    }
    if (list) {
      list.querySelectorAll('[role="option"]').forEach(function (item) {
        var isSelected = item.getAttribute('data-code') === code;
        item.setAttribute('aria-selected', isSelected ? 'true' : 'false');
      });
    }
    if (trigger) {
      trigger.setAttribute('aria-label', 'Ülke kodu: ' + code);
    }
  }

  function teardownMaterializeSelect(select) {
    if (!select || typeof window.jQuery === 'undefined') return;
    var $select = window.jQuery(select);
    if (!$select.length || typeof $select.material_select !== 'function') return;
    try {
      $select.material_select('destroy');
    } catch (error) {
      /* materialize henüz uygulanmamış olabilir */
    }
    var wrapper = select.closest('.select-wrapper');
    if (wrapper && wrapper.parentNode) {
      wrapper.parentNode.insertBefore(select, wrapper);
      wrapper.parentNode.removeChild(wrapper);
    }
    select.hidden = true;
    select.setAttribute('aria-hidden', 'true');
    select.tabIndex = -1;
  }

  function initCountryPicker(picker) {
    if (!picker || picker.dataset.phoneCountryReady === 'true') return;
    picker.dataset.phoneCountryReady = 'true';

    var select = picker.querySelector('.connto-phone-code-native');
    teardownMaterializeSelect(select);
    var trigger = picker.querySelector('.connto-phone-country-picker__trigger');
    var list = picker.querySelector('.connto-phone-country-picker__list');
    if (!select || !trigger || !list) return;

    trigger.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      if (list.hidden) {
        openPicker(picker);
      } else {
        closePicker(picker);
      }
    });

    list.querySelectorAll('[role="option"]').forEach(function (item) {
      item.addEventListener('click', function () {
        setPickerValue(
          picker,
          item.getAttribute('data-code'),
          item.getAttribute('data-iso'),
          item.getAttribute('data-flag')
        );
        closePicker(picker);
      });
    });

    document.addEventListener('click', function (event) {
      if (!picker.contains(event.target)) {
        closePicker(picker);
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        closePicker(picker);
      }
    });
  }

  function initPhoneFields(root) {
    var scope = root || document;

    scope.querySelectorAll('[data-phone-country-picker]').forEach(initCountryPicker);

    scope.querySelectorAll('.connto-phone-number').forEach(function (input) {
      input.addEventListener('input', function () {
        normalizePhoneInput(input);
      });
      input.addEventListener('blur', function () {
        normalizePhoneInput(input);
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initPhoneFields(document);
  });

  window.initPhoneFields = initPhoneFields;
})();
