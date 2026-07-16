(function () {
  var ERROR_MSG = 'Kayıt olmak için en az 18 yaşında olmalısınız.';

  function parseInputDate(value) {
    if (!value) {
      return null;
    }
    var parts = value.split('-');
    if (parts.length !== 3) {
      return null;
    }
    return new Date(
      parseInt(parts[0], 10),
      parseInt(parts[1], 10) - 1,
      parseInt(parts[2], 10)
    );
  }

  function getMinimumAge(input) {
    return parseInt(input.getAttribute('data-register-min-age') || '18', 10);
  }

  function calculateAge(birthDate, today) {
    var age = today.getFullYear() - birthDate.getFullYear();
    var monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age -= 1;
    }
    return age;
  }

  function isUnderMinimumAge(value, minAge) {
    var birthDate = parseInputDate(value);
    if (!birthDate || isNaN(birthDate.getTime())) {
      return false;
    }
    return calculateAge(birthDate, new Date()) < minAge;
  }

  function showAgeError() {
    if (window.Swal) {
      window.Swal.fire({
        icon: 'warning',
        title: 'Uyarı',
        text: ERROR_MSG,
        confirmButtonColor: '#2D7D6F',
        confirmButtonText: 'Tamam',
      });
      return;
    }
    window.alert(ERROR_MSG);
  }

  function setBirthDateError(field, active) {
    if (!field) {
      return;
    }
    field.classList.toggle('connto-field--birth-error', active);
  }

  function validateRegisterBirthDateInput(input, options) {
    if (!input) {
      return true;
    }

    options = options || {};
    var showPopup = options.showPopup !== false;
    var field = input.closest('.connto-field--date');
    var minAge = getMinimumAge(input);

    if (!input.value || !isUnderMinimumAge(input.value, minAge)) {
      setBirthDateError(field, false);
      return true;
    }

    input.value = '';
    setBirthDateError(field, true);
    if (showPopup) {
      showAgeError();
    }
    return false;
  }

  function initRegisterBirthDateValidation(root) {
    var scope = root || document;
    var form = scope.getElementById('individual_form');
    var input = scope.getElementById('id_birth_date');
    if (!form || !input) {
      return;
    }

    input.addEventListener('change', function () {
      validateRegisterBirthDateInput(input, { showPopup: true });
    });

    input.addEventListener('input', function () {
      validateRegisterBirthDateInput(input, { showPopup: true });
    });

    form.addEventListener('submit', function (event) {
      if (!validateRegisterBirthDateInput(input, { showPopup: true })) {
        event.preventDefault();
      }
    });
  }

  window.validateRegisterBirthDateInput = validateRegisterBirthDateInput;
  window.initRegisterBirthDateValidation = initRegisterBirthDateValidation;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initRegisterBirthDateValidation(document);
    });
  } else {
    initRegisterBirthDateValidation(document);
  }
})();
