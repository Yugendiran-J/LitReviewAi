import { BookOpenCheck, Check, CircleAlert, X } from "lucide-react";
import PageHeader from "../components/PageHeader";
import "./BasePaperGuide.css";

const dos = [
  {
    title: "Read and understand the paper",
    description:
      "Understand the research problem, objectives, methodology, and findings before using the paper.",
  },
  {
    title: "Choose a relevant base paper",
    description:
      "Select a paper that closely matches your project topic and research question.",
  },
  {
    title: "Identify the research gap",
    description:
      "Study the limitations and future-work sections to find problems that remain unsolved.",
  },
  {
    title: "Understand the methodology",
    description:
      "Learn how the authors collected data, selected algorithms, and evaluated their system.",
  },
  {
    title: "Cite the original paper",
    description:
      "Give proper credit whenever you use ideas, findings, methods, figures, or text from another publication.",
  },
  {
    title: "Compare multiple papers",
    description:
      "Use several relevant studies to understand different approaches and avoid depending on a single source.",
  },
  {
    title: "Develop your own contribution",
    description:
      "Improve an existing method, address a limitation, compare approaches, or investigate a new research question.",
  },
  {
    title: "Verify the information",
    description:
      "Check important claims, results, references, and technical details against the original paper.",
  },
  {
    title: "Follow publication requirements",
    description:
      "Use the required citation style and follow your institution's academic guidelines.",
  },
  {
    title: "Keep evidence of your work",
    description:
      "Record the sources, datasets, experiments, and changes that support your research.",
  },
];

const donts = [
  {
    title: "Do not copy and paste",
    description:
      "Never present another author's writing as your own, even if you change a few words.",
  },
  {
    title: "Do not change words only",
    description:
      "Simply replacing words with synonyms does not make copied ideas or text original.",
  },
  {
    title: "Do not blindly trust the paper",
    description:
      "Check whether the methodology, evidence, and conclusions are appropriate for your research.",
  },
  {
    title: "Do not fabricate results",
    description:
      "Never invent experimental results, accuracy values, datasets, or observations.",
  },
  {
    title: "Do not claim someone else's contribution",
    description:
      "Clearly distinguish the original authors' work from your proposed contribution.",
  },
  {
    title: "Do not ignore limitations",
    description:
      "Understand the weaknesses and assumptions of the base paper before building on it.",
  },
  {
    title: "Do not use fake references",
    description:
      "Never include citations that you have not verified or that do not support your claims.",
  },
  {
    title: "Do not misuse figures or tables",
    description:
      "Follow copyright, licensing, and permission requirements when reproducing published material.",
  },
  {
    title: "Do not rely on one paper alone",
    description:
      "A single paper may not represent the full state of research in a field.",
  },
  {
    title: "Do not submit AI-generated content blindly",
    description:
      "Review AI-generated text, verify factual claims, and disclose AI assistance when required by your institution or publisher.",
  },
];

const steps = [
  ["1", "Check relevance", "Does the paper address a question and population close to yours?"],
  ["2", "Assess quality", "Are the methods suitable, transparent, and appropriate for the claims?"],
  ["3", "Verify and compare", "Check the source and compare its findings with newer and related studies."],
  ["4", "Cite and build", "Cite ideas accurately, then develop your own synthesis and research direction."],
];

export default function BasePaperGuide() {
  return (
    <div className="page-stack base-paper-guide">
      <PageHeader
        eyebrow="Quick reference"
        title="How to use a base paper"
        description="A base paper can help you understand a topic and find useful methods and sources. Use it as a starting point for your own research—not as something to copy or rely on alone."
      />

      <section className="guide-callout" aria-label="Key principle">
        <div className="guide-callout-icon" aria-hidden="true">
          <BookOpenCheck size={20} />
        </div>
        <p>
          <strong>Start with the paper, then verify and expand.</strong> Your
          question, evidence, and conclusions should be your own and supported
          by appropriate sources.
        </p>
      </section>

      <div className="guide-columns">
        <section className="guide-card guide-card-do" aria-labelledby="guide-dos">
          <div className="guide-card-heading">
            <span className="guide-heading-icon" aria-hidden="true">
              <Check size={17} />
            </span>
            <div>
              <div className="guide-eyebrow">What users should do</div>
              <h2 id="guide-dos">Do’s</h2>
            </div>
          </div>
          <ul className="guide-list">
            {dos.map((item) => (
              <li key={item.title}>
                <Check className="guide-list-icon" size={16} aria-hidden="true" />
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="guide-card guide-card-dont" aria-labelledby="guide-donts">
          <div className="guide-card-heading">
            <span className="guide-heading-icon" aria-hidden="true">
              <X size={17} />
            </span>
            <div>
              <div className="guide-eyebrow">What users should avoid</div>
              <h2 id="guide-donts">Don’ts</h2>
            </div>
          </div>
          <ul className="guide-list">
            {donts.map((item) => (
              <li key={item.title}>
                <X className="guide-list-icon" size={16} aria-hidden="true" />
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="guide-workflow" aria-labelledby="guide-workflow-heading">
        <div className="guide-workflow-heading">
          <div className="guide-eyebrow">A simple approach</div>
          <h2 id="guide-workflow-heading">From first read to your own research</h2>
        </div>
        <ol className="guide-steps">
          {steps.map(([number, title, description]) => (
            <li key={number}>
              <span className="guide-step-number" aria-hidden="true">{number}</span>
              <div>
                <h3>{title}</h3>
                <p>{description}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <aside className="guide-note" aria-label="Academic integrity reminder">
        <CircleAlert size={17} aria-hidden="true" />
        <p>
          <strong>Remember:</strong> Citation styles, copyright rules, and
          academic-integrity policies vary. Follow your institution's guidance
          and ask a supervisor or librarian when you are unsure.
        </p>
      </aside>
    </div>
  );
}
