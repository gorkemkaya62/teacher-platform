(function () {
  function syncEducationOngoingState(scope) {
    var root = scope || document;
    root.querySelectorAll('.edu-ongoing-checkbox').forEach(function (checkbox) {
      var form = checkbox.closest('form');
      if (!form) {
        return;
      }

      var endWrap = form.querySelector('.edu-ongoing-end-date-wrap');
      if (!endWrap) {
        return;
      }

      function applyState() {
        var ongoing = checkbox.checked;
        endWrap.style.display = ongoing ? 'none' : '';
        var endInput = endWrap.querySelector('input[type="date"], .connto-date-picker');
        if (endInput) {
          endInput.disabled = ongoing;
          endInput.required = !ongoing;
          if (ongoing) {
            endInput.value = '';
          }
        }
      }

      if (checkbox.dataset.ongoingBound !== 'true') {
        checkbox.dataset.ongoingBound = 'true';
        checkbox.addEventListener('change', applyState);
      }

      applyState();
    });
  }

  window.syncEducationOngoingState = syncEducationOngoingState;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      syncEducationOngoingState(document);
    });
  } else {
    syncEducationOngoingState(document);
  }
})();
