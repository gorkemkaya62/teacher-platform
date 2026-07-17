(function () {
  function normalizeValue(value) {
    return (value || '').trim();
  }

  function isValidSocialLink(value, prefix) {
    var normalized = normalizeValue(value);
    if (!normalized) {
      return true;
    }

    var lowerValue = normalized.toLowerCase();
    var lowerPrefix = (prefix || '').toLowerCase();
    if (!lowerPrefix || !lowerValue.startsWith(lowerPrefix)) {
      return false;
    }

    try {
      var url = new URL(normalized);
      if (url.protocol !== 'https:') {
        return false;
      }
      var path = (url.pathname || '').replace(/^\/+|\/+$/g, '');
      return Boolean(path);
    } catch (error) {
      return false;
    }
  }

  function buildErrorMessage(label, prefix) {
    return label + ' için yalnızca ' + prefix + ' ile başlayan bağlantılar kullanılabilir.';
  }

  function showSocialLinkError(message) {
    if (window.Swal) {
      window.Swal.fire({
        icon: 'warning',
        title: 'Uyarı',
        text: message,
        confirmButtonColor: '#2D7D6F',
        confirmButtonText: 'Tamam',
      });
      return;
    }
    window.alert(message);
  }

  function getErrorBox(input) {
    var wrap = input.closest('.connto-social-link-row');
    return wrap ? wrap.querySelector('.connto-social-link-error') : null;
  }

  function showFieldError(input, message) {
    var wrap = input.closest('.connto-social-link-row');
    if (!wrap) {
      return;
    }

    var box = wrap.querySelector('.connto-social-link-error');
    if (!box) {
      box = document.createElement('p');
      box.className = 'connto-social-link-error';
      box.style.color = '#b91c1c';
      box.style.marginTop = '6px';
      wrap.appendChild(box);
    }

    box.textContent = message;
    input.setCustomValidity(message);
  }

  function clearFieldError(input) {
    var box = getErrorBox(input);
    if (box && !box.dataset.serverError) {
      box.remove();
    }
    input.setCustomValidity('');
  }

  function isPlatformEnabled(platform) {
    var checkbox = document.querySelector(
      '.connto-social-platform-checkbox[data-social-platform="' + platform + '"]'
    );
    return Boolean(checkbox && checkbox.checked);
  }

  function validateSocialLinkInput(input, options) {
    if (!input) {
      return true;
    }

    options = options || {};
    var showPopup = options.showPopup !== false;
    var platform = input.getAttribute('data-social-platform') || '';
    if (platform && !isPlatformEnabled(platform)) {
      clearFieldError(input);
      return true;
    }

    var value = normalizeValue(input.value);
    var prefix = input.getAttribute('data-social-prefix') || '';
    var label = input.getAttribute('data-social-label') || 'Sosyal medya';

    if (!value) {
      clearFieldError(input);
      return true;
    }

    if (isValidSocialLink(value, prefix)) {
      clearFieldError(input);
      return true;
    }

    var message = buildErrorMessage(label, prefix);
    input.value = '';
    showFieldError(input, message);
    if (showPopup) {
      showSocialLinkError(message);
    }
    return false;
  }

  function syncSocialLinkRow(checkbox) {
    var platform = checkbox.getAttribute('data-social-platform');
    if (!platform) {
      return;
    }

    var row = document.querySelector('.connto-social-link-row[data-social-platform="' + platform + '"]');
    if (!row) {
      return;
    }

    var input = row.querySelector('.connto-social-link-input');
    if (checkbox.checked) {
      row.hidden = false;
      if (input) {
        input.disabled = false;
      }
      return;
    }

    row.hidden = true;
    if (input) {
      input.value = '';
      input.disabled = true;
      clearFieldError(input);
    }
  }

  function bindSocialPlatformCheckbox(checkbox) {
    if (!checkbox || checkbox.dataset.socialPlatformBound === 'true') {
      return;
    }

    checkbox.dataset.socialPlatformBound = 'true';
    checkbox.addEventListener('change', function () {
      syncSocialLinkRow(checkbox);
    });
    syncSocialLinkRow(checkbox);
  }

  function bindSocialLinkInput(input) {
    if (!input || input.dataset.socialLinkBound === 'true') {
      return;
    }

    input.dataset.socialLinkBound = 'true';

    input.addEventListener('blur', function () {
      validateSocialLinkInput(input, { showPopup: true });
    });

    input.addEventListener('paste', function () {
      window.setTimeout(function () {
        validateSocialLinkInput(input, { showPopup: true });
      }, 0);
    });

    var form = input.closest('form');
    if (form && form.dataset.socialLinksBound !== 'true') {
      form.dataset.socialLinksBound = 'true';
      form.addEventListener('submit', function (event) {
        var valid = true;

        form.querySelectorAll('.connto-social-platform-checkbox').forEach(function (checkbox) {
          syncSocialLinkRow(checkbox);
        });

        form.querySelectorAll('.connto-social-link-input').forEach(function (field) {
          var platform = field.getAttribute('data-social-platform') || '';
          if (platform && !isPlatformEnabled(platform)) {
            field.disabled = true;
            return;
          }
          field.disabled = false;
          if (!validateSocialLinkInput(field, { showPopup: true })) {
            valid = false;
          }
        });

        if (!valid) {
          event.preventDefault();
        }
      });
    }
  }

  function showServerErrors(root) {
    var scope = root || document;
    scope.querySelectorAll('.connto-social-link-error[data-server-error="1"]').forEach(function (box) {
      var row = box.closest('.connto-social-link-row');
      if (row) {
        row.hidden = false;
        var platform = row.getAttribute('data-social-platform');
        if (platform) {
          var checkbox = scope.querySelector(
            '.connto-social-platform-checkbox[data-social-platform="' + platform + '"]'
          );
          if (checkbox) {
            checkbox.checked = true;
          }
        }
      }
      showSocialLinkError(box.textContent.trim());
    });
  }

  function initSocialLinksValidation(root) {
    var scope = root || document;
    scope.querySelectorAll('.connto-social-platform-checkbox').forEach(bindSocialPlatformCheckbox);
    scope.querySelectorAll('.connto-social-link-input').forEach(bindSocialLinkInput);
    showServerErrors(scope);
  }

  window.validateSocialLinkInput = validateSocialLinkInput;
  window.initSocialLinksValidation = initSocialLinksValidation;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initSocialLinksValidation(document);
    });
  } else {
    initSocialLinksValidation(document);
  }
})();
