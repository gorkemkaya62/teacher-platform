(function () {
  function refreshMaterialSelect(selectEl) {
    if (!window.jQuery || !jQuery.fn.material_select) {
      return;
    }
    var $select = jQuery(selectEl);
    if ($select.hasClass("browser-default")) {
      return;
    }
    $select.material_select("destroy");
    $select.material_select();
  }

  function populateDistricts(citySelect, districtSelect, selectedDistrict) {
    var city = citySelect.value;
    districtSelect.disabled = true;
    districtSelect.innerHTML = '<option value="">Yükleniyor...</option>';
    refreshMaterialSelect(districtSelect);

    if (!city) {
      districtSelect.innerHTML = '<option value="">Seçiniz</option>';
      districtSelect.disabled = true;
      refreshMaterialSelect(districtSelect);
      return;
    }

    fetch("/adminpanel/api/districts/?city=" + encodeURIComponent(city))
      .then(function (response) {
        if (!response.ok) {
          throw new Error("district request failed");
        }
        return response.json();
      })
      .then(function (data) {
        var options = '<option value="">Seçiniz</option>';
        data.districts.forEach(function (item) {
          var selected =
            selectedDistrict && selectedDistrict === item.value ? " selected" : "";
          options +=
            '<option value="' +
            item.value +
            '"' +
            selected +
            ">" +
            item.label +
            "</option>";
        });
        districtSelect.innerHTML = options;
        districtSelect.disabled = false;
        refreshMaterialSelect(districtSelect);
      })
      .catch(function () {
        districtSelect.innerHTML = '<option value="">İlçeler yüklenemedi</option>';
        districtSelect.disabled = true;
        refreshMaterialSelect(districtSelect);
      });
  }

  window.initCityDistrictSelect = function (citySelector, districtSelector) {
    var citySelect = document.querySelector(citySelector);
    var districtSelect = document.querySelector(districtSelector);
    if (!citySelect || !districtSelect) {
      return;
    }

    var onCityChange = function () {
      populateDistricts(citySelect, districtSelect, "");
    };

    citySelect.removeEventListener("change", citySelect._cityDistrictChangeHandler || function () {});
    citySelect._cityDistrictChangeHandler = onCityChange;
    citySelect.addEventListener("change", onCityChange);

    if (window.jQuery) {
      jQuery(citySelect).off("change.cityDistrict").on("change.cityDistrict", onCityChange);
    }

    var initialDistrict =
      districtSelect.getAttribute("data-selected-district") || districtSelect.value;

    populateDistricts(citySelect, districtSelect, initialDistrict);
  };
})();
