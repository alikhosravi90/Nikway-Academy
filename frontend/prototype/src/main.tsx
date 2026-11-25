import { createRoot } from "react-dom/client";
import { App } from "./app/App";
import "./styles/globals.css";
// Keep links shared by the original prototype valid after the router migration.
if (location.hash && !location.hash.startsWith("#/"))
  history.replaceState(
    null,
    "",
    `${location.pathname}${location.search}#/${location.hash.slice(1)}`,
  );
createRoot(document.getElementById("root")!).render(<App />);
