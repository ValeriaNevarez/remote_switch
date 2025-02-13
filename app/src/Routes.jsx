import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import Login from "./Login";
import List from "./List";
import Calls from "./Calls";
import ActivateDeactivate from "./ActivateDeactivate";
import Report from "./Report"
import PrivateRoute from "./PrivateRoute";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      {
        path: "/login",
        element: <Login />,
      },
      {
        path: "/lista",
        element: (
          <PrivateRoute>
            <List />
          </PrivateRoute>
        ),
      },
      {
        path: "/llamadas",
        element: (
          <PrivateRoute>
            <Calls />
          </PrivateRoute>
        ),
      },
      {
        path: "/activar-desactivar",
        element: (
          <PrivateRoute>
            <ActivateDeactivate />
          </PrivateRoute>
        ),
      },
      {
        path: "/reporte",
        element: (
          <PrivateRoute>
            <Report />
          </PrivateRoute>
        ),
      },
    ],
  },
]);

export default router;