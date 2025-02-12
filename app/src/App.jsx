import Layout from "./Layout";
import Login from "./Login";
import List from "./List";
import Calls from "./Calls";
import ActivateDeactivate from "./ActivateDeactivate";
import Report from "./Report";
import { BrowserRouter, Routes, Route } from "react-router-dom";

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
          <Route path = "/" element = { <Layout></Layout> }>
            <Route index element = { <Login></Login> }></Route>
            <Route path = "/lista" element = { <List></List> }></Route>
            <Route path = "/llamadas" element = { <Calls></Calls> }></Route>
            <Route path = "/activar-desactivar" element = { <ActivateDeactivate></ActivateDeactivate> }></Route>
            <Route path = "/reporte" element = { <Report></Report> }></Route>
          </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App