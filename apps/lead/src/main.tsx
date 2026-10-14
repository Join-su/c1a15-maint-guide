import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@c1a15/ui/styles/guide-a.css";
import "@c1a15/ui/styles/direction-guide.css";
import "./app.css";
import { App } from "./App";

// 파트장 앱(1280 × 620 PC 기준, P-12). 승인 화면 · 토큰은 Prototype v17(packages/ui/src/styles = 승인 CSS 원본).
const root = document.getElementById("root");
if (root) {
  createRoot(root).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
}
