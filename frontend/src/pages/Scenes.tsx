import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getProjects } from "../api/project";
import SceneCard from "../components/SceneCard";
import type { Project } from "../types/project";

function Scenes() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    async function loadProjects() {
      try {
        setLoading(true);
        setError(null);

        const data = await getProjects();

        setProjects(data);
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message);
        } else {
          setError("Failed to load scenes.");
        }
      } finally {
        setLoading(false);
      }
    }

    loadProjects();
  }, []);

  const filteredProjects = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return projects;
    }

    return projects.filter((project) =>
      project.project.toLowerCase().includes(query),
    );
  }, [projects, search]);

  function handleOpenScene(projectName: string) {
    navigate(
      `/scenes/${encodeURIComponent(projectName)}`,
    );
  }

  if (loading) {
    return (
      <main className="scenes-page">
        <section className="scenes-header">
          <div>
            <span className="section-eyebrow">
              LIBRARY
            </span>

            <h1>My Scenes</h1>

            <p>
              Your saved Gaussian Splatting scenes.
            </p>
          </div>
        </section>

        <div className="scenes-loading">
          Loading scenes...
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="scenes-page">
        <section className="scenes-header">
          <div>
            <span className="section-eyebrow">
              LIBRARY
            </span>

            <h1>My Scenes</h1>

            <p>
              Your saved Gaussian Splatting scenes.
            </p>
          </div>
        </section>

        <div className="scenes-error">
          <h2>Unable to load scenes</h2>
          <p>{error}</p>

          <button
            type="button"
            onClick={() => window.location.reload()}
          >
            Try Again
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="scenes-page">
      <section className="scenes-header">
        <div className="scenes-header-content">
          <span className="section-eyebrow">
            LIBRARY
          </span>

          <h1>My Scenes</h1>

          <p>
            Your saved Gaussian Splatting scenes.
          </p>
        </div>

        <div className="scenes-header-decoration">
          <div className="decoration-orb orb-one" />
          <div className="decoration-orb orb-two" />
          <div className="decoration-grid" />
        </div>
      </section>

      <section className="scenes-toolbar">
        <div className="scene-search">
          <span className="search-icon">⌕</span>

          <input
            type="text"
            placeholder="Search scenes..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />
        </div>

        {/* <button
          type="button"
          className="new-scene-button"
          onClick={() => navigate("/new-scene")}
        >
          <span className="new-scene-plus">+</span>
          New Scene
        </button> */}
          <div className="scenes-toolbar-actions">
            <button
              type="button"
              className="home-button"
              onClick={() => navigate("/")}
            >
              ← Home
            </button>

            <button
              type="button"
              className="new-scene-button"
              onClick={() => navigate("/new-scene")}
            >
              <span className="new-scene-plus">+</span>
              New Scene
            </button>
          </div>

      </section>

      {filteredProjects.length === 0 ? (
        <section className="scenes-empty">
          <div className="empty-icon">◇</div>

          <h2>
            {search
              ? "No scenes found"
              : "No scenes yet"}
          </h2>

          <p>
            {search
              ? "Try a different search term."
              : "Create your first Gaussian Splatting scene by uploading a video."}
          </p>

          {!search && (
            <button
              type="button"
              onClick={() => navigate("/new-scene")}
            >
              Create New Scene
            </button>
          )}
        </section>
      ) : (
        <section className="scene-grid">
          {filteredProjects.map((project) => (
            <SceneCard
              key={project.project}
              project={project}
              onOpen={handleOpenScene}
            />
          ))}
        </section>
      )}

      <footer className="scenes-footer">
        <span>
          {projects.length}{" "}
          {projects.length === 1
            ? "scene"
            : "scenes"}
        </span>

        <span className="footer-dot">•</span>

        <span>Gaussian Splatting Studio</span>
      </footer>
    </main>
  );
}

export default Scenes;