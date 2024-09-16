import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import * as ReactDom from "react-dom/client";
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import ViewOrderPage from './Components/CreateViewOrderUI/ViewOrderPage.tsx';
import CreateOrderPage from './Components/CreateViewOrderUI/CreateOrderPage.tsx';

document.title = "AndrewBot - Home";

const router = createBrowserRouter([

  {
    path: '/',
    element: <App />,
  },
  {
    path: '/create-order',
    element: <CreateOrderPage />,

  },
  {
    path: '/view-order',
    element: <ViewOrderPage />,
  },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
