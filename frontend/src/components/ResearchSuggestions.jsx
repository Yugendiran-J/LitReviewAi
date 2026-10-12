import { ArrowRight, BookOpen, ClipboardCheck, FlaskConical, SearchCheck } from "lucide-react";
import { Link } from "react-router-dom";

function getSuggestedSteps({ topic, totalPapers, screened, included, extracted, validated }) {
  const steps = [];

  if (totalPapers === 0) {
    steps.push({
      title: "Find relevant literature",
      description: topic
        ? `Start with a PubMed search based on “${topic}”.`
        : "Search PubMed to begin building your paper library.",
      label: "Search PubMed",
      to: "/literature",
      icon: SearchCheck,
      state: { suggestedQuery: topic },
    });
  } else if (screened < totalPapers) {
    steps.push({
      title: "Review screening progress",
      description: `${totalPapers - screened} ${totalPapers - screened === 1 ? "paper is" : "papers are"} not yet screened.`,
      label: "Open screening",
      to: "/screening",
      icon: ClipboardCheck,
    });
  }

  if (included > extracted) {
    steps.push({
      title: "Move to evidence extraction",
      description: `${included - extracted} included ${included - extracted === 1 ? "study is" : "studies are"} ready for evidence work.`,
      label: "Open evidence",
      to: "/evidence",
      icon: FlaskConical,
    });
  } else if (extracted > validated) {
    steps.push({
      title: "Validate extracted evidence",
      description: `${extracted - validated} extracted ${extracted - validated === 1 ? "study needs" : "studies need"} validation.`,
      label: "Review evidence",
      to: "/evidence",
      icon: ClipboardCheck,
    });
  }

  if (steps.length < 2 && totalPapers > 0) {
    steps.push({
      title: "Broaden your literature search",
      description: "Search another phrase from your research question to find additional relevant studies.",
      label: "Search more literature",
      to: "/literature",
      icon: BookOpen,
      state: { suggestedQuery: topic },
    });
  }

  return steps.slice(0, 2);
}

export default function ResearchSuggestions({
  topic = "",
  totalPapers = 0,
  screened = 0,
  included = 0,
  extracted = 0,
  validated = 0,
}) {
  const suggestions = getSuggestedSteps({
    topic,
    totalPapers,
    screened,
    included,
    extracted,
    validated,
  });

  return (
    <section className="panel suggestions-panel" aria-labelledby="suggestions-heading">
      <div className="panel-heading suggestions-heading">
        <div>
          <div className="eyebrow">BASED ON YOUR STUDY PROGRESS</div>
          <h2 id="suggestions-heading">Suggested next steps</h2>
        </div>
        <span className="suggestion-auto-label"><span /> Updated automatically</span>
      </div>
      <div className="suggestion-grid">
        {suggestions.map(({ title, description, label, to, icon: Icon, state }) => (
          <article className="suggestion-card" key={title}>
            <div className="suggestion-icon"><Icon size={17} /></div>
            <h3>{title}</h3>
            <p>{description}</p>
            <Link className="suggestion-action" to={to} state={state}>
              {label}<ArrowRight size={14} />
            </Link>
          </article>
        ))}
      </div>
      <p className="suggestion-disclaimer">
        Recommendations are generated from the study details and progress available in this workspace.
      </p>
    </section>
  );
}
