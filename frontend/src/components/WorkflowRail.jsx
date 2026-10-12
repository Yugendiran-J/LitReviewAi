import { Check, ChevronRight } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

const steps = [
  { label: "Research Setup", to: "/research/new", num: "01" },
  { label: "Base Papers", to: "/literature", num: "02" },
  { label: "AI Screening", to: "/screening", num: "03" },
  { label: "Evidence", to: "/evidence", num: "04" },
  { label: "Research Brief", to: "/reports", num: "05" },
];

export default function WorkflowRail({ current = 0, compact = false }) {
  const location = useLocation();
  const currentIndex = steps.findIndex((step) => step.to === location.pathname);
  const activeIndex = currentIndex >= 0 ? currentIndex : current;

  return (
    <nav
      className={`workflow-rail${compact ? " workflow-rail-compact" : ""}`}
      aria-label="Base paper discovery workflow"
    >
      {steps.map((step, index) => {
        const isDone = index < activeIndex;
        const isActive = index === activeIndex;
        return (
          <Link
            key={step.to}
            to={step.to}
            className={`workflow-step${isActive ? " workflow-step-active" : ""}${isDone ? " workflow-step-done" : ""}`}
            aria-current={isActive ? "step" : undefined}
          >
            <span className="workflow-step-number">
              {isDone ? <Check size={11} strokeWidth={2.5} /> : step.num}
            </span>
            <span>{step.label}</span>
            {index < steps.length - 1 && <ChevronRight className="workflow-chevron" size={13} />}
          </Link>
        );
      })}
    </nav>
  );
}
