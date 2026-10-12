import { motion } from "framer-motion";
import "./AIBackground.css";
function AIBackground() {
  const particles = Array.from({ length: 35 });

  return (
    <div className="ai-background">

      <div className="ai-grid" />

      <div className="ai-glow ai-glow-one" />
      <div className="ai-glow ai-glow-two" />
      <div className="ai-glow ai-glow-three" />

      {/* Floating particles */}
      {particles.map((_, index) => (
        <motion.span
          key={index}
          className="ai-particle"
          initial={{
            opacity: 0,
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
          }}
          animate={{
            opacity: [0, 0.7, 0],
            y: [
              Math.random() * window.innerHeight,
              Math.random() * window.innerHeight - 120,
            ],
          }}
          transition={{
            duration: 5 + Math.random() * 7,
            repeat: Infinity,
            delay: Math.random() * 5,
            ease: "linear",
          }}
        />
      ))}

      {/* Neural lines */}
      <div className="neural-lines">
        <span />
        <span />
        <span />
        <span />
        <span />
      </div>

    </div>
  );
}

export default AIBackground;