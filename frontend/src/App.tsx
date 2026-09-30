import { BrowserRouter, Route, Routes } from "react-router-dom";

import Scenes from "./pages/Scenes";
import Home from "./pages/Home";
import NewScene from "./pages/NewScene";
import SceneDetails from "./pages/SceneDetails";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/scenes" element={<Scenes />} />
        <Route path="/new-scene" element={<NewScene />} />
        <Route path="/scenes/:projectName" element={<SceneDetails />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;