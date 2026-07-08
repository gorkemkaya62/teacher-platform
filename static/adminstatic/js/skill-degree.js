(function () {
  var ERROR_MESSAGE = 'Yetkinlik seviyesi 0 ile 100 arasında olmalıdır.';

  function isValidSkillDegree(value) {
    if (value === '' || value === null || value === undefined) {
      return false;
    }

    var number = Number(value);
    return Number.isInteger(number) && number >= 0 && number <= 100;
  }

  function getErrorBox(input) {
    var wrap = input.closest('.skill-field-wrap') || input.parentElement;
    return wrap ? wrap.querySelector('.skill-degree-error') : null;
  }

  function showError(input, message) {
    var wrap = input.closest('.skill-field-wrap') || input.parentElement;
    if (!wrap) {
      return;
    }

    var box = wrap.querySelector('.skill-degree-error');
    if (!box) {
      box = document.createElement('p');
      box.className = 'skill-degree-error';
      box.style.color = '#b91c1c';
      box.style.marginTop = '6px';
      wrap.appendChild(box);
    }

    box.textContent = message;
    input.setCustomValidity(message);
  }

  function clearError(input) {
    var box = getErrorBox(input);
    if (box && !box.dataset.serverError) {
      box.remove();
    }
    input.setCustomValidity('');
  }

  function validateInput(input, showEmptyError) {
    if (input.value.trim() === '') {
      if (showEmptyError) {
        showError(input, 'Yetkinlik seviyesi zorunludur.');
        return false;
      }
      clearError(input);
      return false;
    }

    if (!isValidSkillDegree(input.value)) {
      showError(input, ERROR_MESSAGE);
      return false;
    }

    clearError(input);
    return true;
  }

  function bindSkillDegreeInput(input) {
    if (!input || input.dataset.skillDegreeBound === 'true') {
      return;
    }

    input.dataset.skillDegreeBound = 'true';

    input.addEventListener('input', function () {
      validateInput(input, false);
    });

    input.addEventListener('blur', function () {
      validateInput(input, true);
    });

    var form = input.closest('form');
    if (form && form.dataset.skillFormBound !== 'true') {
      form.dataset.skillFormBound = 'true';
      form.addEventListener('submit', function (event) {
        var degreeInput = form.querySelector('.skill-degree-input, #id_skill_degree');
        if (!degreeInput) {
          return;
        }

        if (!validateInput(degreeInput, true)) {
          event.preventDefault();
          degreeInput.reportValidity();
          degreeInput.focus();
        }
      });
    }
  }

  function initSkillDegreeValidation(root) {
    var scope = root || document;
    scope.querySelectorAll('.skill-degree-input, #id_skill_degree').forEach(bindSkillDegreeInput);
  }

  window.initSkillDegreeValidation = initSkillDegreeValidation;
  initSkillDegreeValidation(document);
})();
