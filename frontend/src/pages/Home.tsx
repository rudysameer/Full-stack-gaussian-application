
import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  return (
    <main className="home-page">
      <section className="home-hero">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="hero-badge-dot" />
            Gaussian Splatting Studio
          </div>

          <h1>
            Turn your videos into
            <span> 3D worlds.</span>
          </h1>

          <p>
            Create, train, and explore photorealistic Gaussian
            Splatting scenes from your own videos.
          </p>
        </div>
      </section>

      <section className="home-actions">
        <button
          type="button"
          className="action-card action-card-primary"
          onClick={() => navigate("/new-scene")}
        >
          <div className="action-card-icon">+</div>

          <div className="action-card-content">
            <span className="action-card-label">
              Create
            </span>

            <h2>New Scene</h2>

            <p>
              Upload a video and start building a new
              Gaussian Splatting scene.
            </p>
          </div>

          <span className="action-card-arrow">→</span>
        </button>

        <button
          type="button"
          className="action-card"
          onClick={() => navigate("/scenes")}
        >
          <div className="action-card-icon scenes-icon">
            ◇
          </div>

          <div className="action-card-content">
            <span className="action-card-label">
              Library
            </span>

            <h2>My Scenes</h2>

            <p>
              Browse your existing scenes, training results,
              and reconstructed environments.
            </p>
          </div>

          <span className="action-card-arrow">→</span>
        </button>
      </section>

      <footer className="home-footer">
        <span>Gaussian Splatting</span>
        <span className="footer-separator">•</span>
        <span>3D Reconstruction Studio</span>
      </footer>
    </main>
  );
}

export default Home;
