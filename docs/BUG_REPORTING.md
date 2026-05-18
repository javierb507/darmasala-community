# Reporte de bugs in-app → GitHub Issues

Esta función permite a los administradores reportar problemas directamente desde dentro de la aplicación. Cada reporte se convierte en un issue de GitHub con la descripción del admin más un bloque de **contexto técnico** capturado automáticamente (URL, versión, commit, navegador, usuario que reporta).

---

## 1. Cómo funciona

```
Admin ── click botón "Reportar bug" (esquina inferior derecha)
         │
         └── Modal con título / descripción / "qué hacías"
                │
                └── POST /admin/bug-report/submit
                       │
                       └── DarmaSala ── POST api.github.com/repos/<owner>/<repo>/issues
                                          (header Authorization: Bearer GITHUB_ISSUE_TOKEN)
                                          │
                                          └── GitHub crea el issue
                                          └── Devuelve URL + número
                                          └── Modal muestra enlace
```

- El botón solo aparece si el admin está logueado **y** `bug_report_enabled = true` en `Configuracion`.
- El token NUNCA viaja al navegador: se queda en el servidor.
- Cada sesión está limitada a **5 issues por hora** para evitar spam accidental.

---

## 2. Crear el token de GitHub

Necesitas un **fine-grained personal access token** con permiso de escritura en *Issues* del repositorio destino.

1. Entra en https://github.com/settings/personal-access-tokens/new
2. **Token name**: `darmasala-bug-reporter`
3. **Expiration**: 90 días o más (o "No expiration" si lo aceptas).
4. **Resource owner**: el dueño del repo (tu usuario u organización).
5. **Repository access** → **Only select repositories** → `darmasala` (o el que uses).
6. **Permissions → Repository permissions**:
   - `Issues` → **Read and write**
   - (todo lo demás puede quedarse en *No access*)
7. Crea y copia el token: empieza por `github_pat_…`. **Solo se muestra una vez.**

> Alternativa rápida: usar un **classic PAT** con scope `public_repo` (si el repo es público) o `repo` (si es privado). Más permisos de los necesarios, pero más rápido de crear.

---

## 3. Configurar en el VPS

Edita `/etc/systemd/system/darmasala.service` y añade:

```ini
Environment="GITHUB_ISSUE_TOKEN=github_pat_…"
```

Recarga y reinicia:

```bash
sudo systemctl daemon-reload
sudo systemctl restart darmasala
```

> En desarrollo local: `export GITHUB_ISSUE_TOKEN=github_pat_…` antes de `python run.py`.

---

## 4. Configurar en la UI

Login como admin → **Configuración → Reporte de bugs** (URL directa `/admin/bug-report`).

| Campo | Valor sugerido |
|---|---|
| Activar botón "Reportar bug" | ✅ |
| Repositorio destino | `javierb507/darmasala` |
| Etiquetas por defecto | `bug,reportado-desde-app` |

Pulsa **Guardar configuración**. Recarga la página: aparecerá un botón flotante negro **"Reportar bug"** abajo a la derecha.

---

## 5. Probarlo

1. Click en el botón flotante → se abre el modal.
2. Rellena **Título** (obligatorio) y **Descripción**.
3. *Enviar*.
4. Si todo va bien verás: `Issue creado: #42` con enlace al issue en GitHub.

---

## 6. Qué contiene el issue creado

Título: lo que escribiste, capado a 200 chars.

Cuerpo (markdown):
```
### Descripción
<lo que escribió el usuario>

### ¿Qué estabas haciendo?
<lo que escribió el usuario>

### Contexto técnico
- URL: https://darmasala.cloud/admin/alumnos
- Versión: 2.0.1-final (build 2026-05-12 22:10)
- Commit: e36aed5 — rama main
- Usuario: admin (rol admin)
- User-Agent: Mozilla/5.0 …
- Timestamp UTC: 2026-05-17T18:42:00Z

_Reportado automáticamente desde la aplicación._
```

Etiquetas: las que configuraste (por defecto `bug` + `reportado-desde-app`).

---

## 7. Seguridad

| Riesgo | Mitigación |
|---|---|
| Spam de issues | Rate limit: 5 issues/hora por sesión. |
| Filtración de datos personales en descripciones | Aviso visible en el modal: "no incluyas datos personales de alumnos". |
| Token expuesto en el frontend | El token nunca sale del servidor. Solo el server llama a la API. |
| Token comprometido por logs | El cliente usa `Authorization: Bearer …` (no aparece en URL). |
| Repo público con issues públicos | Recomendado: repo privado, o un repo dedicado de tickets. |

---

## 8. Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| Botón flotante no aparece | `bug_report_enabled != 'true'` o no estás logueado | Activa en `/admin/bug-report` |
| `Token NO configurado` en el panel | Falta env var | Añadir `GITHUB_ISSUE_TOKEN` y reiniciar systemd |
| `GitHub respondió 401` | Token caducado o sin permiso | Regenera con permiso `Issues: write` |
| `GitHub respondió 404` | Repo mal escrito (mayúsculas, dueño) | Comprueba formato `owner/nombre` exacto |
| `Has reportado demasiados bugs en la última hora` | Rate limit | Espera; el contador es por sesión |

---

## 9. Endpoints

| Método | Ruta | Auth | Propósito |
|---|---|---|---|
| GET  | `/admin/bug-report` | admin | Pantalla de configuración |
| POST | `/admin/bug-report/save` | admin | Guarda repo + labels + flag |
| POST | `/admin/bug-report/submit` | admin | Crea el issue (form o JSON) |

---

## 10. Extensiones futuras (no implementadas)

- Captura de screenshot via `html2canvas` y adjuntar a Discusión.
- Enviar también a Sentry/Datadog.
- Botón visible para alumnos del portal (requiere repo de tickets distinto y sanitización extra).
- Asignar issues automáticamente según labels.
