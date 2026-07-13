(function () {
  var MIN_ZOOM_FOR_CITY_FOCUS = 7;

  function readJsonScript(id, fallback) {
    var element = document.getElementById(id);
    if (!element) {
      return fallback;
    }
    try {
      return JSON.parse(element.textContent);
    } catch (error) {
      return fallback;
    }
  }

  function groupTeachersByCity(teachers) {
    return teachers.reduce(function (groups, teacher) {
      if (!teacher.city) {
        return groups;
      }
      if (!groups[teacher.city]) {
        groups[teacher.city] = [];
      }
      groups[teacher.city].push(teacher);
      return groups;
    }, {});
  }

  function initTeacherMap(options) {
    var mapElement = document.getElementById(options.mapId || 'map');
    var modal = document.getElementById(options.modalId || 'mapModal');
    if (!mapElement || !modal || typeof window.L === 'undefined') {
      return;
    }

    var teachers = readJsonScript(options.teachersScriptId || 'map-teachers-data', []);
    var cityCoordinates = readJsonScript(options.coordinatesScriptId || 'city-coordinates-data', {});
    var isCourseCenterView = Boolean(options.isCourseCenterView);
    var sidebarTitle = document.getElementById('mapSidebarTitle');
    var sidebarHint = document.getElementById('mapSidebarHint');
    var sidebarList = document.getElementById('mapExpertsList');
    var teachersByCity = groupTeachersByCity(teachers);

    var map = null;
    var markers = window.L.markerClusterGroup({
      showCoverageOnHover: false,
      maxClusterRadius: 50,
    });
    var cityMarkers = {};
    var activeCity = null;

    function renderTeacherCard(teacher) {
      var link = document.createElement('a');
      link.href = teacher.profileUrl;
      if (isCourseCenterView) {
        link.target = '_blank';
        link.rel = 'noopener';
      } else {
        link.title = 'Profili görmek için üye olun';
      }

      var card = document.createElement('div');
      card.className = isCourseCenterView ? 'expert-card' : 'expert-card expert-card--locked';
      card.dataset.city = teacher.city;

      var avatar = document.createElement('span');
      avatar.className = 'connto-avatar connto-avatar--md';
      var image = document.createElement('img');
      image.className = 'connto-avatar__img';
      image.src = teacher.image;
      image.alt = teacher.name;
      avatar.appendChild(image);

      var info = document.createElement('div');
      var name = document.createElement('strong');
      name.textContent = teacher.name;
      var meta = document.createElement('small');
      meta.textContent = teacher.cityLabel + ' · ' + teacher.branch;
      info.appendChild(name);
      info.appendChild(document.createElement('br'));
      info.appendChild(meta);

      if (isCourseCenterView) {
        card.appendChild(avatar);
        card.appendChild(info);
      } else {
        var blurred = document.createElement('div');
        blurred.className = 'expert-card__blurred';
        blurred.appendChild(avatar);
        blurred.appendChild(info);
        card.appendChild(blurred);
        var lock = document.createElement('i');
        lock.className = 'fa fa-lock expert-card__lock';
        card.appendChild(lock);
      }

      link.appendChild(card);
      return link;
    }

    function renderSidebar(citySlug) {
      if (!sidebarList || !sidebarTitle) {
        return;
      }

      sidebarList.textContent = '';

      if (!citySlug) {
        sidebarTitle.textContent = 'Öğretmenler';
        if (sidebarHint) {
          sidebarHint.hidden = false;
          sidebarHint.textContent = 'Yakınlaştırın ve bir şehrin üzerine gelerek o şehirdeki öğretmenleri görün.';
        }
        return;
      }

      var cityTeachers = teachersByCity[citySlug] || [];
      var cityLabel = cityTeachers.length ? cityTeachers[0].cityLabel : '';

      sidebarTitle.textContent = cityLabel
        ? cityLabel + ' (' + cityTeachers.length + ' öğretmen)'
        : 'Seçilen şehir';
      if (sidebarHint) {
        sidebarHint.hidden = true;
      }

      if (!cityTeachers.length) {
        var empty = document.createElement('p');
        empty.className = 'map-sidebar-empty';
        empty.textContent = 'Bu şehirde arama kriterlerine uygun öğretmen bulunamadı.';
        sidebarList.appendChild(empty);
        return;
      }

      cityTeachers.forEach(function (teacher) {
        sidebarList.appendChild(renderTeacherCard(teacher));
      });
    }

    function setActiveCity(citySlug) {
      activeCity = citySlug || null;
      Object.keys(cityMarkers).forEach(function (slug) {
        var marker = cityMarkers[slug];
        var isActive = slug === activeCity;
        marker.setOpacity(isActive ? 1 : 0.82);
        marker.setZIndexOffset(isActive ? 1000 : 0);
      });
      renderSidebar(activeCity);
    }

    function canFocusCity() {
      return map && map.getZoom() >= MIN_ZOOM_FOR_CITY_FOCUS;
    }

    function focusCity(citySlug) {
      if (!canFocusCity()) {
        if (sidebarHint) {
          sidebarHint.textContent = 'Şehir detayını görmek için haritayı biraz daha yakınlaştırın.';
          sidebarHint.hidden = false;
        }
        return;
      }
      setActiveCity(citySlug);
    }

    function buildMarkers() {
      markers.clearLayers();
      cityMarkers = {};

      Object.keys(teachersByCity).forEach(function (citySlug) {
        var coords = cityCoordinates[citySlug];
        var cityTeachers = teachersByCity[citySlug];
        if (!coords || !cityTeachers.length) {
          return;
        }

        var cityLabel = cityTeachers[0].cityLabel;
        var marker = window.L.marker(coords, {
          title: cityLabel,
        });
        marker.bindPopup(
          '<strong>' + cityLabel + '</strong><br>' + cityTeachers.length + ' öğretmen'
        );
        marker.on('mouseover', function () {
          focusCity(citySlug);
        });
        marker.on('click', function () {
          focusCity(citySlug);
          map.setView(coords, Math.max(map.getZoom(), MIN_ZOOM_FOR_CITY_FOCUS));
        });
        markers.addLayer(marker);
        cityMarkers[citySlug] = marker;
      });

      map.addLayer(markers);
    }

    function initMap() {
      map = window.L.map(mapElement, {
        scrollWheelZoom: true,
      }).setView([39.0, 35.0], 6);

      window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap',
      }).addTo(map);

      buildMarkers();
      renderSidebar(null);

      map.on('zoomend', function () {
        if (!canFocusCity() && activeCity) {
          setActiveCity(null);
          if (sidebarHint) {
            sidebarHint.textContent = 'Şehir seçmek için yakınlaştırın ve bir işaretin üzerine gelin.';
            sidebarHint.hidden = false;
          }
        }
      });
    }

    if (modal.dataset.mapInitialized === 'true') {
      return;
    }
    modal.dataset.mapInitialized = 'true';

    if (window.jQuery) {
      window.jQuery(modal).on('shown.bs.modal', function () {
        if (!map) {
          initMap();
        }
        setTimeout(function () {
          map.invalidateSize();
        }, 120);
      });
    } else {
      modal.addEventListener('shown.bs.modal', function () {
        if (!map) {
          initMap();
        }
        setTimeout(function () {
          map.invalidateSize();
        }, 120);
      });
    }
  }

  window.initTeacherMap = initTeacherMap;
})();
