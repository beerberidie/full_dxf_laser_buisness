class CustomFooter extends HTMLElement {
  connectedCallback() {
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        footer {
          background: #1a202c;
          color: white;
          padding: 2rem;
          text-align: center;
          margin-top: auto;
        }
        .footer-content {
          max-width: 1200px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .footer-links {
          display: flex;
          justify-content: center;
          flex-wrap: wrap;
          gap: 1.5rem;
          list-style: none;
          padding: 0;
          margin: 0;
        }
        .footer-links a {
          color: #a0aec0;
          text-decoration: none;
          transition: color 0.2s;
        }
        .footer-links a:hover {
          color: white;
        }
        .social-links {
          display: flex;
          justify-content: center;
          gap: 1.5rem;
        }
        .social-links a {
          color: #a0aec0;
          transition: color 0.2s;
        }
        .social-links a:hover {
          color: white;
        }
        .copyright {
          color: #718096;
          font-size: 0.875rem;
        }
        @media (max-width: 768px) {
          .footer-links {
            flex-direction: column;
            align-items: center;
            gap: 0.75rem;
          }
        }
      </style>
      <footer>
        <div class="footer-content">
          <ul class="footer-links">
            <li><a href="#">Privacy Policy</a></li>
            <li><a href="#">Terms of Service</a></li>
            <li><a href="#">Contact Us</a></li>
            <li><a href="#">API Documentation</a></li>
          </ul>
          <div class="social-links">
            <a href="#"><i data-feather="twitter"></i></a>
            <a href="#"><i data-feather="linkedin"></i></a>
            <a href="#"><i data-feather="github"></i></a>
            <a href="#"><i data-feather="facebook"></i></a>
          </div>
          <p class="copyright">&copy; 2024 OmniComm Hub. All rights reserved.</p>
        </div>
      </footer>
    `;
  }
}
customElements.define('custom-footer', CustomFooter);