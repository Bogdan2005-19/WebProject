$(document).ready(function () {
  // Filtrar por género
  $(document).on('click', '.filtro-genero', function () {
    var genero = $(this).data('genero');
    var busqueda = $('input[name="q"]').val();

    var currentUrl = new URL(window.location);
    currentUrl.searchParams.set('category', genero);
    window.history.pushState({ path: currentUrl.href }, '', currentUrl.href);


    $.ajax({
      url: '/games/',
      type: 'GET',
      data: {
        category: genero,
        q: busqueda
      },
      success: function (respuesta) {
        $('#contenedor-juegos').html(respuesta);
      },
      error: function () {
        alert('Error al cargar los juegos.');
      }
    });
  });

  // Manejar la paginación
  $(document).on('click', '.page-link', function (event) {
    event.preventDefault();

    const href = $(this).attr('href');
    const url = new URL(href, window.location.origin);
    const page = url.searchParams.get('page');
    const genero = new URL(window.location).searchParams.get('category');
    const busqueda = new URL(window.location).searchParams.get('q');

    $.ajax({
      url: '/games/',
      type: 'GET',
      data: {
        page: page,
        category: genero,
        q: busqueda
      },
      success: function (respuesta) {
        $('#contenedor-juegos').html(respuesta);
        // Actualiza también la URL en la barra de navegación
        url.searchParams.set('page', page);
        if (genero) url.searchParams.set('category', genero);
        if (busqueda) url.searchParams.set('q', busqueda);
        window.history.pushState({}, '', url.href);
      },
      error: function () {
        alert('Error al cargar los juegos.');
      }
    });
  });
});
