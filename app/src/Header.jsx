function Header() {
  return (
    <nav class="navbar navbar-expand-lg bg-dark" data-bs-theme="dark">
      <div class="container-fluid">
        <a class="navbar-brand" >
          Switch Remoto
        </a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav d-flex justify-content-evenly">
            <li class="nav-item">
              <a class="nav-link active px-4" aria-current="page" href="#">
                Lista dispositivos
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link px-4" href="#">
                Realizar llamada
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link px-4" href="#">
                Activar/Desactivar dispositivo
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link px-4" href="#">
                Reporte
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default Header;
