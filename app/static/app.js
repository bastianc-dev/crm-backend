const STATUSES = ["Nuevo", "Contactado", "Interesado", "Negociación", "Ganado", "Perdido"];

const state = {
  token: localStorage.getItem("crm_access_token"),
  user: null,
  users: [],
  page: 1,
  limit: 20,
  currentView: "dashboard",
  filters: {
    search: "",
    estado: "",
    empresa: "",
    created_from: "",
    created_to: "",
    sort: "updated_at",
    order: "desc",
  },
};

const app = document.querySelector("#app");

function escapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function statusClass(status) {
  return `status-${status}`;
}

function statusBadge(status) {
  return `<span class="badge ${statusClass(status)}">${escapeHtml(status)}</span>`;
}

function isDemoAdmin() {
  return Boolean(state.user && state.user.email === "admin.demo@test.com");
}

function isDemoUser() {
  return Boolean(state.user && state.user.email && (state.user.email.endsWith("@crm-demo.app") || state.user.email.endsWith(".demo@test.com")));
}

function formatDate(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("es-CL", {
    year: "numeric",
    month: "short",
    day: "2-digit",
  }).format(new Date(value));
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  if (!toast) return;

  toast.textContent = message;
  toast.classList.remove("hidden");

  setTimeout(() => {
    toast.classList.add("hidden");
  }, 3000);
}

function humanError(data, fallback = "Ocurrió un error") {
  if (!data) return fallback;

  if (typeof data.detail === "string") {
    const map = {
      "Email ya registrado": "Ya existe una cuenta con ese correo.",
      "Token inválido": "Tu sesión expiró. Vuelve a iniciar sesión.",
      "No tienes permisos": "No puedes realizar esta acción con tu cuenta actual.",
      "Lead no encontrado": "Este lead ya no existe o fue eliminado.",
      "Usuario asignado no encontrado": "El responsable seleccionado no existe.",
      "Demo no habilitada": "El modo demo no está habilitado en este entorno. Puedes crear una cuenta normal.",
      "La demo solo puede gestionar usuarios de prueba": "La cuenta demo solo puede ver o modificar datos de prueba.",
      "No puedes desactivar tu propia cuenta": "No puedes desactivar tu propia cuenta mientras estás usando la aplicación.",
      "No puedes cambiar tu propio rol": "No puedes cambiar el rol de tu propia cuenta.",
    };

    return map[data.detail] || data.detail;
  }

  if (Array.isArray(data.detail)) {
    return "Revisa los campos del formulario. Hay datos inválidos o incompletos.";
  }

  return fallback;
}

async function apiRequest(path, options = {}) {
  const headers = {
    ...(options.headers || {}),
  };

  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  if (options.body && !(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  let response;
  try {
    response = await fetch(path, { ...options, headers });
  } catch {
    throw new Error("No se pudo conectar con el servidor. Comprueba tu conexión e inténtalo de nuevo.");
  }

  let data = null;
  const rawBody = await response.text();

  if (rawBody) {
    try {
      data = JSON.parse(rawBody);
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    const error = new Error(humanError(data));
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

function setToken(token) {
  state.token = token;
  localStorage.setItem("crm_access_token", token);
}

function clearSession() {
  state.token = null;
  state.user = null;
  localStorage.removeItem("crm_access_token");
}

async function loginWithCredentials(email, password) {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const data = await apiRequest("/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });

  setToken(data.access_token);
  await loadSession();
}

async function loginDemo(role) {
  const data = await apiRequest(`/demo/login/${role}`, {
    method: "POST",
  });

  setToken(data.access_token);
  await loadSession();
}

async function loadSession() {
  if (!state.token) {
    renderAuth();
    return;
  }

  try {
    state.user = await apiRequest("/me");
    renderApp();
  } catch (error) {
    clearSession();
    renderAuth(error.message);
  }
}

function renderAuth(message = "") {
  app.innerHTML = document.querySelector("#auth-template").innerHTML;

  const loginForm = document.querySelector("#login-form");
  const registerForm = document.querySelector("#register-form");
  const authMessage = document.querySelector("#auth-message");

  authMessage.textContent = message;

  const authTabs = [...document.querySelectorAll("[data-auth-tab]")];

  function selectAuthTab(selectedTab, focusTab = false) {
    authTabs.forEach((tab) => {
      const selected = tab.dataset.authTab === selectedTab;
      tab.classList.toggle("active", selected);
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
      if (selected && focusTab) tab.focus();
    });

    loginForm.classList.toggle("hidden", selectedTab !== "login");
    registerForm.classList.toggle("hidden", selectedTab !== "register");
    authMessage.textContent = "";
  }

  authTabs.forEach((button, index) => {
    button.addEventListener("click", () => selectAuthTab(button.dataset.authTab));
    button.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === "Home" ? 0 : event.key === "End" ? authTabs.length - 1
        : (index + (event.key === "ArrowRight" ? 1 : -1) + authTabs.length) % authTabs.length;
      selectAuthTab(authTabs[next].dataset.authTab, true);
    });
  });

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    authMessage.textContent = "";

    const form = new FormData(loginForm);

    try {
      await loginWithCredentials(form.get("email"), form.get("password"));
    } catch (error) {
      authMessage.textContent = error.message;
    }
  });

  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    authMessage.textContent = "";

    const form = new FormData(registerForm);
    const email = form.get("email");
    const password = form.get("password");

    try {
      await apiRequest("/register", {
        method: "POST",
        body: JSON.stringify({
          nombre: form.get("nombre"),
          email,
          password,
        }),
      });

      await loginWithCredentials(email, password);
    } catch (error) {
      authMessage.textContent = error.message;
    }
  });

  document.querySelectorAll("[data-demo-role]").forEach((button) => {
    button.addEventListener("click", async () => {
      authMessage.textContent = "";

      try {
        await loginDemo(button.dataset.demoRole);
      } catch (error) {
        authMessage.textContent = error.message;
      }
    });
  });
}

function renderApp() {
  app.innerHTML = document.querySelector("#app-template").innerHTML;

  document.querySelector("#current-user-name").textContent = state.user.nombre;
  document.querySelector("#current-user-email").textContent = state.user.email;
  document.querySelector("#user-role-label").textContent = state.user.rol === "admin" ? "Administrador" : "Empleado";

  document.querySelectorAll(".admin-only").forEach((element) => {
    element.classList.toggle("hidden", state.user.rol !== "admin");
  });

  document.querySelector("#logout-button").addEventListener("click", () => {
    clearSession();
    renderAuth();
  });

  document.querySelector("#new-lead-button").addEventListener("click", () => {
    openLeadModal();
  });

  document.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", () => {
      showView(button.dataset.view);
    });
  });

  showView("dashboard");
}

async function refreshCurrentView() {
  if (state.currentView === "dashboard") {
    await renderDashboard();
    return;
  }

  if (state.currentView === "leads") {
    await renderLeads();
    return;
  }

  if (state.currentView === "users") {
    await renderUsers();
  }
}

async function showView(viewName) {
  state.currentView = viewName;

  document.querySelectorAll("[data-view]").forEach((button) => {
    const active = button.dataset.view === viewName;
    button.classList.toggle("active", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });

  document.querySelectorAll(".view").forEach((view) => {
    view.classList.add("hidden");
  });

  document.querySelector(`#${viewName}-view`).classList.remove("hidden");

  const titles = {
    dashboard: ["Panel", "Dashboard"],
    leads: ["Gestión comercial", "Leads"],
    users: ["Administración", "Usuarios"],
  };

  document.querySelector("#section-eyebrow").textContent = titles[viewName][0];
  document.querySelector("#section-title").textContent = titles[viewName][1];

  if (viewName === "dashboard") await renderDashboard();
  if (viewName === "leads") await renderLeads();
  if (viewName === "users") await renderUsers();
}

async function loadUsersIfNeeded() {
  if (state.user.rol !== "admin") {
    state.users = [state.user];
    return;
  }

  state.users = await apiRequest("/users?limit=100");
}

function userNameById(userId) {
  const user = state.users.find((item) => item.id === userId);
  return user ? user.nombre : "Sin asignar";
}

function buildLeadQuery() {
  const params = new URLSearchParams();

  Object.entries(state.filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });

  params.set("page", state.page);
  params.set("limit", state.limit);

  return params.toString();
}

async function fetchLeads() {
  const query = buildLeadQuery();
  return apiRequest(`/leads?${query}`);
}

async function renderDashboard() {
  const view = document.querySelector("#dashboard-view");

  try {
    const [stats, leadsData] = await Promise.all([
      apiRequest("/dashboard/stats"),
      apiRequest("/leads?limit=100&sort=updated_at&order=desc"),
      loadUsersIfNeeded(),
    ]);

    view.innerHTML = `
      <div class="card-grid">
        <article class="stat-card"><span>Total leads</span><strong>${stats.total}</strong></article>
        <article class="stat-card"><span>Interesados</span><strong>${stats.by_status.Interesado || 0}</strong></article>
        <article class="stat-card"><span>Negociación</span><strong>${stats.by_status["Negociación"] || 0}</strong></article>
        <article class="stat-card"><span>Ganados</span><strong>${stats.by_status.Ganado || 0}</strong></article>
      </div>

      <section class="panel">
        <div class="modal-header">
          <div>
            <h2>Pipeline por estado</h2>
            <p class="muted">El estado es la señal principal para saber en qué fase está cada oportunidad.</p>
          </div>
        </div>
        ${renderPipeline(leadsData.items)}
      </section>
    `;
  } catch (error) {
    view.innerHTML = `<div class="empty-state"><h3>No se pudo cargar el dashboard</h3><p>${escapeHtml(error.message)}</p></div>`;
  }
}

function renderPipeline(leads) {
  const grouped = Object.fromEntries(STATUSES.map((status) => [status, []]));

  leads.forEach((lead) => {
    if (grouped[lead.estado]) {
      grouped[lead.estado].push(lead);
    }
  });

  return `
    <div class="pipeline">
      ${STATUSES.map((status) => `
        <div class="pipeline-column">
          <h3>${status} <span>${grouped[status].length}</span></h3>
          ${grouped[status].slice(0, 8).map((lead) => `
            <article class="lead-card">
              <strong>${escapeHtml(lead.nombre)}</strong>
              <p>${escapeHtml(lead.empresa || "Sin empresa")}</p>
              <button class="icon-button" type="button" aria-label="Ver lead ${escapeHtml(lead.nombre)}" data-open-lead="${lead.id}">Ver</button>
            </article>
          `).join("") || `<p class="muted">Sin leads.</p>`}
        </div>
      `).join("")}
    </div>
  `;
}

async function renderLeads() {
  const view = document.querySelector("#leads-view");

  try {
    await loadUsersIfNeeded();
    const data = await fetchLeads();

    view.innerHTML = `
      <section class="panel">
        <div class="toolbar">
          <label class="filter-field"><span class="sr-only">Buscar leads</span><input id="filter-search" type="search" value="${escapeHtml(state.filters.search)}" placeholder="Buscar nombre, correo, empresa o teléfono"></label>
          <label class="filter-field"><span class="sr-only">Filtrar por estado</span><select id="filter-status">
            <option value="">Todos los estados</option>
            ${STATUSES.map((status) => `<option value="${status}" ${state.filters.estado === status ? "selected" : ""}>${status}</option>`).join("")}
          </select></label>
          <label class="filter-field"><span class="sr-only">Filtrar por empresa</span><input id="filter-company" value="${escapeHtml(state.filters.empresa)}" placeholder="Empresa"></label>
          <label class="filter-field"><span class="sr-only">Fecha de creación desde</span><input id="filter-from" type="date" value="${escapeHtml(state.filters.created_from)}"></label>
          <label class="filter-field"><span class="sr-only">Fecha de creación hasta</span><input id="filter-to" type="date" value="${escapeHtml(state.filters.created_to)}"></label>
          <label class="filter-field"><span class="sr-only">Ordenar por</span><select id="filter-sort">
            <option value="updated_at" ${state.filters.sort === "updated_at" ? "selected" : ""}>Última actualización</option>
            <option value="created_at" ${state.filters.sort === "created_at" ? "selected" : ""}>Fecha creación</option>
            <option value="name" ${state.filters.sort === "name" ? "selected" : ""}>Nombre</option>
          </select></label>
        </div>

        ${data.items.length ? renderLeadTable(data.items) : renderEmptyLeads()}
        ${renderPagination(data)}
      </section>
    `;

    bindLeadFilters();
    bindLeadActions();
  } catch (error) {
    view.innerHTML = `<div class="empty-state"><h3>No se pudieron cargar los leads</h3><p>${escapeHtml(error.message)}</p></div>`;
  }
}

function renderEmptyLeads() {
  return `
    <div class="empty-state">
      <h3>Todavía no hay leads para mostrar</h3>
      <p>Crea tu primer lead para empezar a organizar oportunidades comerciales.</p>
      <button class="primary-button" type="button" data-create-first-lead>Crear lead</button>
    </div>
  `;
}

function renderLeadTable(leads) {
  return `
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th scope="col">Lead</th>
            <th scope="col">Estado</th>
            <th scope="col">Empresa</th>
            <th scope="col">Responsable</th>
            <th scope="col">Actualizado</th>
            <th scope="col">Acciones</th>
          </tr>
        </thead>
        <tbody>
          ${leads.map((lead) => `
            <tr>
              <td>
                <strong>${escapeHtml(lead.nombre)}</strong><br>
                <span class="muted">${escapeHtml(lead.email || lead.telefono || "Sin contacto")}</span>
              </td>
              <td>${statusBadge(lead.estado)}</td>
              <td>${escapeHtml(lead.empresa || "-")}</td>
              <td>${escapeHtml(userNameById(lead.assigned_user_id))}</td>
              <td>${formatDate(lead.updated_at)}</td>
              <td>
                <div class="actions">
                  <button class="icon-button" type="button" aria-label="Ver lead ${escapeHtml(lead.nombre)}" data-open-lead="${lead.id}">Ver</button>
                  <button class="icon-button" type="button" aria-label="Editar lead ${escapeHtml(lead.nombre)}" data-edit-lead="${lead.id}">Editar</button>
                  ${state.user.rol === "admin" || lead.assigned_user_id === state.user.id ? `<button class="danger-button" type="button" aria-label="Eliminar lead ${escapeHtml(lead.nombre)}" data-delete-lead="${lead.id}">Eliminar</button>` : ""}
                </div>
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function renderPagination(data) {
  return `
    <div class="pagination">
      <span>Página ${data.page} de ${data.pages || 1} · ${data.total} resultado(s)</span>
      <div class="button-row">
        <button class="secondary-button" type="button" data-page-prev ${data.page <= 1 ? "disabled" : ""}>Anterior</button>
        <button class="secondary-button" type="button" data-page-next ${data.page >= data.pages ? "disabled" : ""}>Siguiente</button>
      </div>
    </div>
  `;
}

function bindLeadFilters() {
  const updateAndRender = async () => {
    const currentInput = document.activeElement;
    const inputId = currentInput?.id;
    const position = typeof currentInput?.selectionStart === "number"
      ? [currentInput.selectionStart, currentInput.selectionEnd] : null;
    state.page = 1;
    await renderLeads();
    const nextInput = inputId ? document.getElementById(inputId) : null;
    if (nextInput) {
      nextInput.focus();
      if (position && typeof nextInput.setSelectionRange === "function") {
        nextInput.setSelectionRange(...position);
      }
    }
  };

  document.querySelector("#filter-search")?.addEventListener("input", debounce((event) => {
    state.filters.search = event.target.value.trim();
    updateAndRender();
  }, 350));

  document.querySelector("#filter-status")?.addEventListener("change", (event) => {
    state.filters.estado = event.target.value;
    updateAndRender();
  });

  document.querySelector("#filter-company")?.addEventListener("input", debounce((event) => {
    state.filters.empresa = event.target.value.trim();
    updateAndRender();
  }, 350));

  document.querySelector("#filter-from")?.addEventListener("change", (event) => {
    state.filters.created_from = event.target.value;
    updateAndRender();
  });

  document.querySelector("#filter-to")?.addEventListener("change", (event) => {
    state.filters.created_to = event.target.value;
    updateAndRender();
  });

  document.querySelector("#filter-sort")?.addEventListener("change", (event) => {
    state.filters.sort = event.target.value;
    updateAndRender();
  });

  document.querySelector("[data-page-prev]")?.addEventListener("click", () => {
    state.page -= 1;
    renderLeads();
  });

  document.querySelector("[data-page-next]")?.addEventListener("click", () => {
    state.page += 1;
    renderLeads();
  });

  document.querySelector("[data-create-first-lead]")?.addEventListener("click", () => openLeadModal());
}

function bindLeadActions() {
  document.querySelectorAll("[data-edit-lead]").forEach((button) => {
    button.addEventListener("click", async () => {
      const lead = await apiRequest(`/leads/${button.dataset.editLead}`);
      openLeadModal(lead);
    });
  });

  document.querySelectorAll("[data-delete-lead]").forEach((button) => {
    button.addEventListener("click", async () => {
      if (!confirm("¿Eliminar este lead? Esta acción no se puede deshacer.")) return;

      try {
        await apiRequest(`/leads/${button.dataset.deleteLead}`, {
          method: "DELETE",
        });

        showToast("Lead eliminado");
        await refreshCurrentView();
      } catch (error) {
        showToast(error.message);
      }
    });
  });
}

function openLeadDetail(lead) {
  openModal(`
    <div class="modal-header">
      <div>
        <h2>${escapeHtml(lead.nombre)}</h2>
        <p class="muted">${escapeHtml(lead.empresa || "Sin empresa")} · ${statusBadge(lead.estado)}</p>
      </div>
      <button class="icon-button" type="button" data-close-modal>Cerrar</button>
    </div>

    <div class="card-grid">
      <article class="stat-card"><span>Responsable</span><strong style="font-size:20px">${escapeHtml(userNameById(lead.assigned_user_id))}</strong></article>
      <article class="stat-card"><span>Correo</span><strong style="font-size:20px">${escapeHtml(lead.email || "-")}</strong></article>
      <article class="stat-card"><span>Teléfono</span><strong style="font-size:20px">${escapeHtml(lead.telefono || "-")}</strong></article>
      <article class="stat-card"><span>Cargo</span><strong style="font-size:20px">${escapeHtml(lead.cargo || "-")}</strong></article>
    </div>

    <section class="panel">
      <h3>Notas</h3>
      <p>${escapeHtml(lead.notas || "Sin notas registradas.")}</p>
    </section>

    <div class="button-row" style="margin-top:18px">
      <button class="primary-button" type="button" data-edit-from-detail="${lead.id}">Editar lead</button>
      ${state.user.rol === "admin" || lead.assigned_user_id === state.user.id ? `<button class="danger-button" type="button" data-delete-from-detail="${lead.id}">Eliminar lead</button>` : ""}
    </div>
  `);

  document.querySelector("[data-edit-from-detail]")?.addEventListener("click", () => {
    closeModal();
    openLeadModal(lead);
  });

  document.querySelector("[data-delete-from-detail]")?.addEventListener("click", async () => {
    if (!confirm("¿Eliminar este lead? Esta acción no se puede deshacer.")) return;

    try {
      await apiRequest(`/leads/${lead.id}`, { method: "DELETE" });
      closeModal();
      showToast("Lead eliminado");
      await refreshCurrentView();
    } catch (error) {
      showToast(error.message);
    }
  });
}

async function openLeadModal(lead = null) {
  await loadUsersIfNeeded();

  const isEditing = Boolean(lead);
  const assignedOptions = state.users.map((user) => `
    <option value="${user.id}" ${Number(lead?.assigned_user_id || state.user.id) === user.id ? "selected" : ""}>
      ${escapeHtml(user.nombre)}
    </option>
  `).join("");

  openModal(`
    <div class="modal-header">
      <div>
        <h2>${isEditing ? "Editar lead" : "Nuevo lead"}</h2>
        <p class="muted">El estado ayuda a saber qué tan cerca está esta oportunidad de convertirse en cliente.</p>
      </div>
      <button class="icon-button" type="button" data-close-modal>Cerrar</button>
    </div>

    <form id="lead-form" class="form-grid">
      <label>
        Nombre *
        <input name="nombre" required maxlength="150" value="${escapeHtml(lead?.nombre || "")}" placeholder="Nombre del contacto o empresa">
      </label>

      <label>
        Estado
        <select name="estado">
          ${STATUSES.map((status) => `<option value="${status}" ${(lead?.estado || "Nuevo") === status ? "selected" : ""}>${status}</option>`).join("")}
        </select>
      </label>

      <label>
        Empresa
        <input name="empresa" maxlength="150" value="${escapeHtml(lead?.empresa || "")}" placeholder="Empresa u organización">
      </label>

      <label>
        Cargo
        <input name="cargo" maxlength="100" value="${escapeHtml(lead?.cargo || "")}" placeholder="Cargo o rol, opcional">
      </label>

      <label>
        Correo
        <input name="email" type="email" value="${escapeHtml(lead?.email || "")}" placeholder="Correo del lead, opcional">
      </label>

      <label>
        Teléfono
        <input name="telefono" maxlength="30" value="${escapeHtml(lead?.telefono || "")}" placeholder="Teléfono del lead, opcional">
      </label>

      ${state.user.rol === "admin" ? `
        <label class="full">
          Responsable
          <select name="assigned_user_id">${assignedOptions}</select>
        </label>
      ` : ""}

      <label class="full">
        Notas
        <textarea name="notas" maxlength="2000" placeholder="Información relevante, seguimiento o próximos pasos">${escapeHtml(lead?.notas || "")}</textarea>
      </label>

      <div class="button-row full">
        <button class="primary-button" type="submit">${isEditing ? "Guardar cambios" : "Crear lead"}</button>
        <button class="secondary-button" type="button" data-close-modal>Cancelar</button>
      </div>
    </form>
  `);

  document.querySelector("#lead-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = new FormData(event.target);
    const payload = Object.fromEntries(form.entries());

    Object.keys(payload).forEach((key) => {
      if (payload[key] === "") payload[key] = null;
    });

    if (payload.assigned_user_id) {
      payload.assigned_user_id = Number(payload.assigned_user_id);
    }

    try {
      await apiRequest(isEditing ? `/leads/${lead.id}` : "/leads", {
        method: isEditing ? "PATCH" : "POST",
        body: JSON.stringify(payload),
      });

      closeModal();
      showToast(isEditing ? "Lead actualizado" : "Lead creado");
      await refreshCurrentView();
    } catch (error) {
      showToast(error.message);
    }
  });
}

async function renderUsers() {
  const view = document.querySelector("#users-view");

  if (state.user.rol !== "admin") {
    view.innerHTML = `<div class="empty-state"><h3>No tienes permisos</h3><p>Solo administradores pueden gestionar usuarios.</p></div>`;
    return;
  }

  try {
    await loadUsersIfNeeded();

    view.innerHTML = `
      <section class="panel">
        <div class="modal-header">
          <div>
            <h2>Usuarios</h2>
            <p class="muted">Crea empleados, cambia roles y desactiva cuentas.</p>
          </div>
          <button class="primary-button" type="button" id="new-user-button">Nuevo usuario</button>
        </div>

        ${isDemoAdmin() ? `
          <div class="demo-warning">
            <strong>Modo demo administrador</strong>
            Solo se muestran cuentas de prueba. Esta cuenta no puede ver, editar ni desactivar usuarios reales.
          </div>
        ` : ""}

        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th scope="col">Nombre</th>
                <th scope="col">Correo</th>
                <th scope="col">Rol</th>
                <th scope="col">Estado</th>
                <th scope="col">Acciones</th>
              </tr>
            </thead>
            <tbody>
              ${state.users.map((user) => `
                <tr>
                  <td><strong>${escapeHtml(user.nombre)}</strong></td>
                  <td>${escapeHtml(user.email)}</td>
                  <td>${user.rol === "admin" ? "Administrador" : "Empleado"}</td>
                  <td>${user.activo ? "Activo" : "Inactivo"}</td>
                  <td>
                    <div class="actions">
                      <button class="icon-button" type="button" aria-label="Editar usuario ${escapeHtml(user.nombre)}" data-edit-user="${user.id}">Editar</button>
                      ${user.id === state.user.id ? `<span class="muted">Tu cuenta</span>` : user.activo ? `<button class="danger-button" type="button" aria-label="Desactivar usuario ${escapeHtml(user.nombre)}" data-deactivate-user="${user.id}">Desactivar</button>` : ""}
                    </div>
                  </td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      </section>
    `;

    document.querySelector("#new-user-button").addEventListener("click", () => openUserModal());

    document.querySelectorAll("[data-edit-user]").forEach((button) => {
      button.addEventListener("click", () => {
        const user = state.users.find((item) => item.id === Number(button.dataset.editUser));
        openUserModal(user);
      });
    });

    document.querySelectorAll("[data-deactivate-user]").forEach((button) => {
      button.addEventListener("click", async () => {
        if (!confirm("¿Desactivar este usuario?")) return;

        try {
          await apiRequest(`/users/${button.dataset.deactivateUser}`, {
            method: "DELETE",
          });

          showToast("Usuario desactivado");
          state.users = [];
          await refreshCurrentView();
        } catch (error) {
          showToast(error.message);
        }
      });
    });
  } catch (error) {
    view.innerHTML = `<div class="empty-state"><h3>No se pudieron cargar los usuarios</h3><p>${escapeHtml(error.message)}</p></div>`;
  }
}

function openUserModal(user = null) {
  const isEditing = Boolean(user);
  const isCurrentUser = Boolean(user && state.user && user.id === state.user.id);

  openModal(`
    <div class="modal-header">
      <div>
        <h2>${isEditing ? "Editar usuario" : "Nuevo usuario"}</h2>
        <p class="muted">Los empleados solo ven sus leads. Los administradores ven todo.${isDemoAdmin() ? " En modo demo solo se pueden usar correos @crm-demo.app." : ""}</p>
      </div>
      <button class="icon-button" type="button" data-close-modal>Cerrar</button>
    </div>

    <form id="user-form" class="form-grid">
      <label>
        Nombre
        <input name="nombre" required maxlength="100" value="${escapeHtml(user?.nombre || "")}" placeholder="Nombre de la cuenta">
      </label>

      <label>
        Correo
        <input name="email" type="email" required value="${escapeHtml(user?.email || "")}" placeholder="correo@crm-demo.app">
      </label>

      <label>
        Rol
        <select name="rol" ${isCurrentUser ? "disabled" : ""}>
          <option value="employee" ${user?.rol === "employee" ? "selected" : ""}>Empleado</option>
          <option value="admin" ${user?.rol === "admin" ? "selected" : ""}>Administrador</option>
        </select>
      </label>

      <label>
        Estado
        <select name="activo" ${isCurrentUser ? "disabled" : ""}>
          <option value="true" ${user?.activo !== false ? "selected" : ""}>Activo</option>
          ${isCurrentUser ? "" : `<option value="false" ${user?.activo === false ? "selected" : ""}>Inactivo</option>`}
        </select>
      </label>

      ${!isEditing ? `
        <label class="full">
          Contraseña
          <input name="password" type="password" required minlength="8" placeholder="mínimo 8 caracteres">
        </label>
      ` : `
        <label class="full">
          Nueva contraseña
          <input name="password" type="password" minlength="8" placeholder="opcional">
        </label>
      `}

      <div class="button-row full">
        <button class="primary-button" type="submit">${isEditing ? "Guardar cambios" : "Crear usuario"}</button>
        <button class="secondary-button" type="button" data-close-modal>Cancelar</button>
      </div>
    </form>
  `);

  document.querySelector("#user-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = new FormData(event.target);
    const payload = Object.fromEntries(form.entries());

    if (isCurrentUser) {
      payload.activo = true;
      payload.rol = user.rol;
    } else {
      payload.activo = payload.activo === "true";
    }

    if (!payload.password) {
      delete payload.password;
    }

    try {
      await apiRequest(isEditing ? `/users/${user.id}` : "/users", {
        method: isEditing ? "PATCH" : "POST",
        body: JSON.stringify(payload),
      });

      closeModal();
      showToast(isEditing ? "Usuario actualizado" : "Usuario creado");
      state.users = [];
      await refreshCurrentView();
    } catch (error) {
      showToast(error.message);
    }
  });
}

let modalReturnFocus = null;

function handleModalKeys(event) {
  if (event.key === "Escape") {
    event.preventDefault();
    closeModal();
    return;
  }

  if (event.key !== "Tab") return;
  const dialog = document.querySelector("#modal-root .modal-card");
  if (!dialog) return;
  const focusable = [...dialog.querySelectorAll(
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
  )].filter((element) => element.getClientRects().length > 0);
  if (!focusable.length) {
    event.preventDefault();
    dialog.focus();
    return;
  }
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog)) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function openModal(content) {
  modalReturnFocus = document.activeElement;
  document.querySelector("#modal-root").innerHTML = `
    <div class="modal-backdrop">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="modal-title" tabindex="-1">${content}</div>
    </div>
  `;

  const dialog = document.querySelector("#modal-root .modal-card");
  const title = dialog.querySelector("h2");
  if (title) title.id = "modal-title";

  dialog.querySelectorAll("[data-close-modal]").forEach((button) => {
    button.addEventListener("click", closeModal);
  });
  document.querySelector(".modal-backdrop").addEventListener("click", (event) => {
    if (event.target.classList.contains("modal-backdrop")) closeModal();
  });
  document.addEventListener("keydown", handleModalKeys);
  (dialog.querySelector("[data-close-modal]") || dialog).focus();
}

function closeModal() {
  document.removeEventListener("keydown", handleModalKeys);
  document.querySelector("#modal-root").innerHTML = "";
  if (modalReturnFocus?.isConnected) modalReturnFocus.focus();
  modalReturnFocus = null;
}

function debounce(callback, delay) {
  let timeoutId;

  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => callback(...args), delay);
  };
}

document.addEventListener("click", async (event) => {
  const target = event.target.closest("[data-open-lead]");
  if (!target || !state.user) return;

  try {
    const lead = await apiRequest(`/leads/${target.dataset.openLead}`);
    await loadUsersIfNeeded();
    openLeadDetail(lead);
  } catch (error) {
    showToast(error.message);
  }
});

loadSession();
