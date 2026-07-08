(function () {
  function syncEducationOngoingState(scope) {
    var root = scope || document;
    root.querySelectorAll('form').forEach(function (form) {
      var checkbox = form.querySelector('.edu-ongoing-checkbox');
      var endWrap = form.querySelector('#education-end-date-wrap');
      if (!checkbox || !endWrap) {
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
