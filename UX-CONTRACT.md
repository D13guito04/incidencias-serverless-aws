# UX Contract

## Product context

- Audience: usuarios con sesión que necesitan registrar y hacer seguimiento de incidencias.
- Primary jobs: crear incidencias, consultar las propias y cambiar su estado.
- Target market(s): España.
- Active locales: es-ES.
- Language/content register: español claro y directo; fechas presentadas con locale es-ES.
- Timezone/calendar policy: las fechas de creación se almacenan en UTC y se muestran en la zona horaria del navegador.
- Accessibility target: WCAG 2.2 AA.

## Business-context sources

| Domain / scope | Authoritative source | Source type | Reviewed date |
|---|---|---|---|
| Auth, routes, data model and deployment | `docs/configuracion-consola.md` | Project configuration record | 2026-11-23 |
| Lambda request and response behavior | `lambdas/*/lambda_function.py` | API implementation | 2026-11-23 |
| Visual system | `DESIGN.md` | Design contract | 2026-11-23 |

## Visual contract

- Project design source: `DESIGN.md`.
- Token ownership: `DESIGN.md` owns palette, spacing and visual choices; `frontend/index.html` implements them.
- Runtime design-system/token source: inline CSS variables in `frontend/index.html`.
- Supported themes: light.
- Design-context review policy: update the design source when changing a shared visual pattern.

## Canonical UI Map

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
|---|---|---|---|---|
| Select/Listbox | Native HTML select, owned by the frontend | `frontend/index.html` and `premium-ui.json` | Native select for priority and incident state | Keyboard selection, visible focus and static audit |
| Form | Native HTML forms with page-owned validation and async handlers | `frontend/index.html`; API rules in `lambdas/crear-incidencia/lambda_function.py` and `lambdas/cambiar-estado/lambda_function.py` | Create incident; edit incident state | Required-field checks, duplicate-submit state, POST and PATCH response handling |
| CRUD | Frontend workflow calling the authenticated HTTP API | `frontend/index.html` and the three Lambda handlers | Create, read own records, update state; deletion is not exposed in the UI | Authenticated create/list/update flow; 401 and 404 handling |

## Component behavior

| Component | Default | Hover | Focus | Active | Disabled | Busy | Error |
|---|---|---|---|---|---|---|---|
| Button | Clear text label | Color/border change | Visible outline | Darker surface | Reduced emphasis, no action | Label describes work | Inline feedback follows the action |
| Input | Label and help text | Native | Visible outline | n/a | n/a | Submit button shows progress | Inline message and aria-invalid |
| Select | Native control | Native | Visible outline | Native | n/a | Disabled during state save | Inline validation message |
| Textarea | Optional description | Native | Visible outline | n/a | n/a | n/a | n/a |
| Incident list | Most recent first | n/a | Saved item receives focus after creation | n/a | n/a | Loading status and aria-busy | Preserves existing data and offers retry |

## Flow ledger

| Operation | Trigger | Pending | Success destination | Success feedback | Failure recovery | Focus outcome | Source ref |
|---|---|---|---|---|---|---|---|
| Create | Submit the new incident form | Submit button disabled; label changes | New record appears at the top | “Incidencia creada.” | Keep values on API failure; reload list if response cannot be confirmed | Focus the new incident title | `frontend/index.html` |
| Read | Login or select Actualizar | List announces loading; refresh button disabled | Own incidents replace the list | Count and records update | Preserve existing records and allow retry | Keep refresh control available | `frontend/index.html` |
| Edit state | Submit a record's state form | Save and select disabled | Updated state shown on the same record | “Estado actualizado.” | Explain 400/404/API errors without changing displayed state | Return focus to save button | `frontend/index.html` |
| Session expiry | API returns 401 | Clear in-memory session | Login prompt | Re-authentication message | User can sign in again | Login control remains available | `frontend/index.html` |

## Dataset navigation

- Exploratory list: the signed-in user's incidents, newest first.
- URL state: none; records and tokens are not placed in the URL.
- Empty/loading/error treatment: explicit live status text; failed refresh preserves the current list.
- Selection scope: no bulk selection.

## Async and resilience

- Mutations use pessimistic updates: the displayed state changes only after the API succeeds.
- Duplicate submission is prevented by disabling the active submit button.
- Create failures preserve form values. An ambiguous create response triggers a list reload before another attempt.
- A 401 clears tokens held in memory and asks the user to sign in again.
- A 404 during state update explains that the record was not found and offers list synchronization.
- Late list responses are ignored after a newer request or a successful create.

## Validation and permission

- Title is required after trimming; priority must be `baja`, `media` or `alta`.
- State must be `abierta`, `en curso` or `cerrada`.
- Invalid fields receive inline messages, `aria-invalid`, and focus moves to the first invalid field.
- The API authorizer verifies the Cognito ID token. The UI keeps tokens in memory and does not persist them in localStorage.
- The list is scoped by the authenticated identity in the API; client-side values do not define record ownership.

## Verification

- Static checks: HTML parser, `git diff --check`, and the frontend strict audit.
- Browser check: CloudFront login flow, responsive layout, and authenticated CRUD flow.
- Failure paths: 401 expiry, API/network failure, invalid input, and 404 state update.
- Local Live Server is for layout review; Cognito login uses the registered CloudFront redirect URL.
