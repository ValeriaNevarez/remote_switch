import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import Login from "./Login";
import List from "./List";
import ManualRedirect from "./ManualRedirect";
import PrivateRoute from "./PrivateRoute";
import LoginRoute from "./LoginRoute";

const router = createBrowserRouter([
  {
    path: "/manual",
    element: <ManualRedirect />,
  },
  {
    path: "/",
    element: <App />,
    children: [
      {
        path: "/login",
        element: (
          <LoginRoute>
            <Login />
          </LoginRoute>
        ),
      },
      {
        index: true,
        element: (
          <PrivateRoute>
            <List />
          </PrivateRoute>
        ),
      },
    ],
  },
]);

export default router;
