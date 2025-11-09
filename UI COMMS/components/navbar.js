class CustomNavbar extends HTMLElement {
  connectedCallback() {
    this.attachShadow({ mode: 'open' });
    this.shadowRoot.innerHTML = `
      <style>
        nav {
          background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
          padding: 1rem 2rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .logo {
          color: white;
          font-weight: bold;
          font-size: 1.5rem;
          display: flex;
          align-items: center;
        }
        .logo-icon {
          margin-right: 0.75rem;
        }
        .nav-links {
          display: flex;
          gap: 1.5rem;
          list-style: none;
          margin: 0;
          padding: 0;
        }
        a {
          color: white;
          text-decoration: none;
          transition: opacity 0.2s;
          font-weight: 500;
          display: flex;
          align-items: center;
        }
        a:hover {
          opacity: 0.9;
        }
        .nav-icon {
          margin-right: 0.5rem;
        }
        .user-menu {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .avatar {
          width: 2.5rem;
          height: 2.5rem;
          border-radius: 9999px;
          border: 2px solid white;
        }
        @media (max-width: 768px) {
          nav {
            flex-direction: column;
            padding: 1rem;
          }
          .logo {
            margin-bottom: 1rem;
          }
          .nav-links {
            flex-direction: column;
            align-items: center;
            gap: 0.75rem;
          }
          .user-menu {
            margin-top: 1rem;
          }
        }
      </style>
      <nav>
        <a href="/" class="logo">
          <i data-feather="message-square" class="logo-icon"></i>
          OmniComm Hub
        </a>
        <ul class="nav-links">
          <li><a href="#"><i data-feather="home" class="nav-icon"></i> Dashboard</a></li>
          <li><a href="#"><i data-feather="settings" class="nav-icon"></i> Settings</a></li>
          <li><a href="#"><i data-feather="help-circle" class="nav-icon"></i> Help</a></li>
        </ul>
        <div class="user-menu">
          <img src="http://static.photos/people/200x200/10" alt="User" class="avatar">
        </div>
      </nav>
    `;
  }
}
customElements.define('custom-navbar', CustomNavbar);