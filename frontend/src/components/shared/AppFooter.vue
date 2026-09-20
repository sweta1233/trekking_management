<template>
  <footer class="app-footer">
    <div class="footer-container">
      <!-- Project Info Section -->
      <div class="footer-section">
        <h3 class="footer-title">🏔️ TrekMate AI</h3>
        <p class="footer-description">
          Intelligent Trekking Management Platform powered by RAG, LangGraph,
          Vector Search, and Traditional ML
        </p>
        <div class="tech-badges">
          <span class="tech-badge">RAG</span>
          <span class="tech-badge">LangGraph</span>
          <span class="tech-badge">FAISS</span>
          <span class="tech-badge">ML</span>
        </div>
      </div>

      <!-- Quick Links -->
      <div class="footer-section">
        <h4 class="footer-heading">Quick Links</h4>
        <ul class="footer-links">
          <li><a href="https://trekking-management-sand.vercel.app" target="_blank" rel="noopener">🌐 Live Demo</a></li>
          <li><a href="https://github.com/sweta1233/Trekking-management-app" target="_blank" rel="noopener">📂 Source Code</a></li>
          <li><a href="https://github.com/sweta1233/Trekking-management-app#readme" target="_blank" rel="noopener">📚 Documentation</a></li>
          <li><a href="https://github.com/sweta1233" target="_blank" rel="noopener">👤 Developer Profile</a></li>
        </ul>
      </div>

      <!-- Technologies -->
      <div class="footer-section">
        <h4 class="footer-heading">Technologies</h4>
        <ul class="footer-links">
          <li>🤖 LangChain & LangGraph</li>
          <li>🔍 Vector Database (FAISS)</li>
          <li>🧠 OpenAI / Anthropic / Gemini</li>
          <li>📊 scikit-learn & XGBoost</li>
          <li>⚡ Vue.js & Flask</li>
        </ul>
      </div>

      <!-- Contact & Social -->
      <div class="footer-section">
        <h4 class="footer-heading">Connect</h4>
        <div class="social-links">
          <a
            href="https://github.com/sweta1233"
            target="_blank"
            rel="noopener"
            class="social-link"
            title="GitHub Profile"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
          </a>
          <a
            href="https://trekking-management-sand.vercel.app"
            target="_blank"
            rel="noopener"
            class="social-link"
            title="Live Demo"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
            Live Demo
          </a>
        </div>
        <p class="footer-note">
          ⭐ Star on GitHub if this helped you!
        </p>
      </div>
    </div>

    <!-- Bottom Bar -->
    <div class="footer-bottom">
      <div class="footer-bottom-content">
        <p class="copyright">
          © 2024 TrekMate AI | Built with ❤️ by
          <a href="https://github.com/sweta1233" target="_blank" rel="noopener">@sweta1233</a>
        </p>
        <p class="portfolio-badge">
          🚀 AI Engineering Portfolio Project
        </p>
      </div>
      <div class="deployment-info">
        <span class="deployment-badge">
          <span class="status-indicator"></span>
          Deployed on Vercel
        </span>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter',
}
</script>

<style scoped>
.app-footer {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-top: auto;
  padding: 48px 24px 24px;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 32px;
  margin-bottom: 32px;
}

.footer-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.footer-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-description {
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.95;
  margin: 0;
}

.tech-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.tech-badge {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.footer-heading {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  opacity: 0.95;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-links li {
  font-size: 14px;
  opacity: 0.9;
}

.footer-links a {
  color: white;
  text-decoration: none;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.footer-links a:hover {
  opacity: 1;
  text-decoration: underline;
  transform: translateX(4px);
}

.social-links {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.social-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: white;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.15);
  padding: 10px 16px;
  border-radius: 8px;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.social-link:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.social-link svg {
  flex-shrink: 0;
}

.footer-note {
  font-size: 13px;
  opacity: 0.9;
  margin: 12px 0 0;
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding-top: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  max-width: 1200px;
  margin: 0 auto;
}

.footer-bottom-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.copyright {
  font-size: 14px;
  margin: 0;
  opacity: 0.9;
}

.copyright a {
  color: white;
  text-decoration: none;
  font-weight: 600;
  transition: opacity 0.2s;
}

.copyright a:hover {
  opacity: 1;
  text-decoration: underline;
}

.portfolio-badge {
  font-size: 13px;
  opacity: 0.85;
  margin: 0;
}

.deployment-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.deployment-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.15);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.status-indicator {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .app-footer {
    padding: 32px 16px 16px;
  }

  .footer-container {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .footer-bottom {
    flex-direction: column;
    align-items: flex-start;
    text-align: center;
  }

  .footer-bottom-content {
    width: 100%;
    align-items: center;
  }

  .deployment-info {
    width: 100%;
    justify-content: center;
  }
}
</style>
