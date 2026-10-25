import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { VehicleCard, CarArt, money } from "./VehicleCard";
import { request } from "./api";
import "./style.css";

function Auth({ onLogin }) {
  const [register, setRegister] = useState(false),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      onLogin(
        await request("/auth/" + (register ? "register" : "login"), {
          method: "POST",
          body: Object.fromEntries(new FormData(e.currentTarget)),
        }),
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="auth-layout">
      <section className="auth-story">
        <a className="brand" href="/">
          A<span>↗</span> APEX MOTORS
        </a>
        <div>
          <p className="eyebrow">A BETTER WAY TO MOVE</p>
          <h1>
            Your next chapter.
            <br />
            Your next drive.
          </h1>
          <p>
            A thoughtfully selected inventory.
            <br />
            One simple place to find your perfect fit.
          </p>
          <CarArt tone={0} />
        </div>
        <small>THE OPEN ROAD STARTS HERE.</small>
      </section>
      <main className="auth-form">
        <div className="auth-box">
          <p className="eyebrow">WELCOME TO APEX</p>
          <h2>
            {register ? "Make yourself at home." : "Good to see you again."}
          </h2>
          <p>
            {register
              ? "Create an account to explore our collection."
              : "Sign in to explore the collection and manage purchases."}
          </p>
          <form onSubmit={submit}>
            <label>
              Email address
              <input
                name="email"
                type="email"
                autoComplete="email"
                required
                placeholder="you@example.com"
              />
            </label>
            <label>
              Password
              <input
                name="password"
                type="password"
                autoComplete={register ? "new-password" : "current-password"}
                minLength={10}
                maxLength={128}
                required
                placeholder="At least 10 characters"
              />
            </label>
            {error && (
              <p role="alert" className="error">
                {error}
              </p>
            )}
            <button className="primary w-full" disabled={busy}>
              {busy ? "Please wait…" : register ? "Create account" : "Sign in"}{" "}
              <span>↗</span>
            </button>
          </form>
          <p className="auth-switch">
            {register ? "Already have an account?" : "New to Apex?"}{" "}
            <button
              onClick={() => {
                setRegister(!register);
                setError("");
              }}
            >
              {register ? "Sign in" : "Create an account"}
            </button>
          </p>
        </div>
      </main>
    </div>
  );
}
const emptyVehicle = {
  make: "",
  model: "",
  category: "Sedan",
  price: "",
  quantity: 0,
};
function Editor({ modal, onClose, onSave, busy }) {
  useEffect(() => {
    const previous = document.activeElement;
    const node = document.querySelector("dialog");
    node.showModal();
    node.querySelector("input,button")?.focus();
    return () => previous?.focus();
  }, []);
  const v = modal.vehicle || emptyVehicle;
  return (
    <dialog
      onCancel={(e) => {
        if (busy) e.preventDefault();
        else onClose();
      }}
    >
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const raw = Object.fromEntries(new FormData(e.currentTarget));
          onSave(
            modal.type === "delete"
              ? {}
              : modal.type === "restock"
                ? { quantity: Number(raw.quantity) }
                : { ...raw, quantity: Number(raw.quantity) },
          );
        }}
      >
        <div className="modal-title">
          <h2>
            {modal.type === "delete"
              ? "Delete vehicle?"
              : modal.type === "restock"
                ? "Restock vehicle"
                : modal.vehicle
                  ? "Edit vehicle"
                  : "Add a vehicle"}
          </h2>
          <button
            type="button"
            aria-label="Close dialog"
            onClick={onClose}
            disabled={busy}
          >
            ×
          </button>
        </div>
        {modal.type === "delete" ? (
          <p>
            Remove {v.make} {v.model} from the inventory? This cannot be undone.
          </p>
        ) : modal.type === "restock" ? (
          <>
            <p>
              {v.make} {v.model} · currently {v.quantity} in stock
            </p>
            <label>
              Units to add
              <input
                autoFocus
                name="quantity"
                type="number"
                min="1"
                max="1000000"
                step="1"
                defaultValue="1"
                required
              />
            </label>
          </>
        ) : (
          <>
            <div className="form-grid">
              <label>
                Make
                <input
                  name="make"
                  defaultValue={v.make}
                  required
                  maxLength={80}
                />
              </label>
              <label>
                Model
                <input
                  name="model"
                  defaultValue={v.model}
                  required
                  maxLength={80}
                />
              </label>
            </div>
            <label>
              Category
              <input
                name="category"
                list="categories"
                defaultValue={v.category}
                required
                maxLength={40}
              />
              <datalist id="categories">
                {[
                  "Sedan",
                  "SUV",
                  "Hatchback",
                  "Coupe",
                  "Truck",
                  "Electric",
                ].map((x) => (
                  <option key={x}>{x}</option>
                ))}
              </datalist>
            </label>
            <div className="form-grid">
              <label>
                Price (USD)
                <input
                  name="price"
                  type="number"
                  min="0"
                  max="100000000"
                  step=".01"
                  defaultValue={v.price}
                  required
                />
              </label>
              <label>
                Quantity
                <input
                  name="quantity"
                  type="number"
                  min="0"
                  max="1000000"
                  step="1"
                  defaultValue={v.quantity}
                  required
                />
              </label>
            </div>
          </>
        )}
        {modal.error && (
          <p role="alert" className="error">
            {modal.error}
          </p>
        )}
        <div className="modal-footer">
          <button
            type="button"
            className="secondary"
            onClick={onClose}
            disabled={busy}
          >
            Cancel
          </button>
          <button className="primary" disabled={busy}>
            {busy
              ? "Saving…"
              : modal.type === "delete"
                ? "Confirm delete"
                : "Save changes"}
          </button>
        </div>
      </form>
    </dialog>
  );
}
function App() {
  const [session, setSession] = useState(null),
    [vehicles, setVehicles] = useState([]),
    [loading, setLoading] = useState(false),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [filters, setFilters] = useState({
      make: "",
      model: "",
      category: "",
      min_price: "",
      max_price: "",
    }),
    [applied, setApplied] = useState({}),
    [revision, setRevision] = useState(0),
    [modal, setModal] = useState(null),
    [busy, setBusy] = useState(null);
  // Tokens stay in memory; refreshing deliberately requires signing in again.
  const token = session?.access_token,
    admin = session?.user.role === "admin";
  useEffect(() => {
    if (!token) return;
    const controller = new AbortController();
    setLoading(true);
    setError("");
    const params = new URLSearchParams(
      Object.entries(applied).filter(([, v]) => v !== ""),
    );
    request("/vehicles/search?" + params, { token, signal: controller.signal })
      .then(setVehicles)
      .catch((e) => {
        if (e.name === "AbortError") return;
        if (e.status === 401) {
          setSession(null);
          setVehicles([]);
        } else setError(e.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [token, applied, revision]);
  async function purchase(id) {
    setBusy(id);
    setError("");
    setNotice("");
    try {
      await request(`/vehicles/${id}/purchase`, {
        token,
        method: "POST",
        body: { quantity: 1 },
      });
      setNotice("Purchase recorded. One vehicle has been deducted from stock.");
      setRevision((x) => x + 1);
    } catch (e) {
      setError(e.message);
      if (e.status === 401) setSession(null);
    } finally {
      setBusy(null);
    }
  }
  async function save(body) {
    setBusy("modal");
    try {
      const type = modal.type,
        id = modal.vehicle?.id;
      await request(
        type === "restock"
          ? `/vehicles/${id}/restock`
          : id
            ? `/vehicles/${id}`
            : "/vehicles",
        {
          token,
          method:
            type === "delete"
              ? "DELETE"
              : type === "restock" || !id
                ? "POST"
                : "PUT",
          body: type === "delete" ? undefined : body,
        },
      );
      setModal(null);
      setNotice(type === "delete" ? "Vehicle deleted." : "Inventory updated.");
      setRevision((x) => x + 1);
    } catch (e) {
      if (e.status === 401) {
        setSession(null);
        setModal(null);
      } else setModal((m) => ({ ...m, error: e.message }));
    } finally {
      setBusy(null);
    }
  }
  if (!session)
    return (
      <Auth
        onLogin={(s) => {
          setSession(s);
          setNotice("");
          setError("");
        }}
      />
    );
  const stock = vehicles.reduce((sum, v) => sum + v.quantity, 0),
    value = vehicles.reduce((sum, v) => sum + v.price * v.quantity, 0);
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a href="/" className="brand">
          A<span>↗</span>
          <div>
            APEX<small>MOTORS</small>
          </div>
        </a>
        <div className="workspace-label">WORKSPACE</div>
        <div className="nav-active">
          ▦ <span>Vehicle inventory</span>
          <span className="nav-count">{vehicles.length}</span>
        </div>
        <div className="sidebar-note">
          <span>THE APEX STANDARD</span>
          <p>
            Great cars.
            <br />
            Clear choices.
            <br />
            Open roads.
          </p>
          <div className="road-mark">↗</div>
        </div>
        <div className="profile">
          <div className="avatar">{session.user.email[0].toUpperCase()}</div>
          <div className="profile-text">
            <strong>{session.user.email.split("@")[0]}</strong>
            <small>{admin ? "Administrator" : "Customer"}</small>
          </div>
          <button
            title="Sign out"
            aria-label="Sign out"
            onClick={() => {
              setSession(null);
              setVehicles([]);
            }}
          >
            ↪
          </button>
        </div>
      </aside>
      <div className="main-area">
        <header>
          <div>
            <span className="muted">Workspace</span>
            <span className="breadcrumb">/</span>Inventory
          </div>
          <span className="live-indicator">● Connected inventory</span>
        </header>
        <main className="dashboard">
          <div className="page-title">
            <div>
              <p className="eyebrow">THE COLLECTION</p>
              <h1>
                Find your next drive<span>.</span>
              </h1>
              <p>Explore the lot. Make your move.</p>
            </div>
            {admin && (
              <button
                className="primary add-button"
                onClick={() => setModal({ type: "edit" })}
              >
                ＋ Add vehicle
              </button>
            )}
          </div>
          <section className="stats" aria-label="Filtered inventory totals">
            <div>
              <span>VEHICLE MODELS</span>
              <strong>{String(vehicles.length).padStart(2, "0")}</strong>
              <small>In the current collection</small>
            </div>
            <div>
              <span>AVAILABLE UNITS</span>
              <strong>{String(stock).padStart(2, "0")}</strong>
              <small>Ready for their next chapter</small>
            </div>
            <div>
              <span>INVENTORY VALUE</span>
              <strong>{money(value)}</strong>
              <small>USD · matching your filters</small>
            </div>
          </section>
          <section className="collection">
            <div className="section-heading">
              <h2>
                Explore inventory <span>{vehicles.length}</span>
              </h2>
              <span className="muted">Curated for every journey</span>
            </div>
            <form
              className="filters"
              onSubmit={(e) => {
                e.preventDefault();
                setApplied({ ...filters });
              }}
            >
              <label>
                Make
                <input
                  placeholder="e.g. Toyota"
                  value={filters.make}
                  onChange={(e) =>
                    setFilters({ ...filters, make: e.target.value })
                  }
                />
              </label>
              <label>
                Model
                <input
                  placeholder="Any model"
                  value={filters.model}
                  onChange={(e) =>
                    setFilters({ ...filters, model: e.target.value })
                  }
                />
              </label>
              <label>
                Category
                <input
                  placeholder="Any category"
                  value={filters.category}
                  onChange={(e) =>
                    setFilters({ ...filters, category: e.target.value })
                  }
                />
              </label>
              <label>
                Min. price
                <input
                  type="number"
                  min="0"
                  step=".01"
                  placeholder="$0"
                  value={filters.min_price}
                  onChange={(e) =>
                    setFilters({ ...filters, min_price: e.target.value })
                  }
                />
              </label>
              <label>
                Max. price
                <input
                  type="number"
                  min="0"
                  step=".01"
                  placeholder="No limit"
                  value={filters.max_price}
                  onChange={(e) =>
                    setFilters({ ...filters, max_price: e.target.value })
                  }
                />
              </label>
              <button className="primary">Search</button>
              <button
                type="button"
                className="reset"
                onClick={() => {
                  const f = {
                    make: "",
                    model: "",
                    category: "",
                    min_price: "",
                    max_price: "",
                  };
                  setFilters(f);
                  setApplied(f);
                }}
              >
                Reset
              </button>
            </form>
            {error && (
              <p role="alert" className="error">
                {error}
              </p>
            )}
            {notice && (
              <p role="status" className="notice">
                ✓ {notice}
              </p>
            )}
            {loading ? (
              <div className="empty-state" role="status">
                Loading the collection…
              </div>
            ) : vehicles.length ? (
              <div className="vehicle-grid">
                {vehicles.map((v) => (
                  <VehicleCard
                    key={v.id}
                    vehicle={v}
                    admin={admin}
                    busy={busy !== null}
                    onPurchase={purchase}
                    onEdit={(v) => setModal({ type: "edit", vehicle: v })}
                    onRestock={(v) => setModal({ type: "restock", vehicle: v })}
                    onDelete={(v) => setModal({ type: "delete", vehicle: v })}
                  />
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <h3>No vehicles found</h3>
                <p>
                  Try different filters
                  {admin
                    ? " or add your first vehicle."
                    : ". Check back soon for new arrivals."}
                </p>
              </div>
            )}
          </section>
          <footer>
            <span>APEX MOTORS</span>
            <span>Good journeys start with a great choice.</span>
          </footer>
        </main>
      </div>
      {modal && (
        <Editor
          modal={modal}
          onClose={() => setModal(null)}
          onSave={save}
          busy={busy === "modal"}
        />
      )}
    </div>
  );
}
createRoot(document.getElementById("root")).render(<App />);
