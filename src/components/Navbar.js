// src/components/Navbar.js
import React from "react";
import { Link } from "react-router-dom";
import { Layout, Menu } from "antd";

const { Header } = Layout;

function Navbar() {
  return (
    <Header style={{ display: "flex" }}>
      <Menu theme="dark" mode="horizontal" defaultSelectedKeys={[]}>
        <Menu.Item key="login">
          <Link to="/login">Login</Link>
        </Menu.Item>
        <Menu.Item key="dashboard">
          <Link to="/dashboard">Dashboard</Link>
        </Menu.Item>
        <Menu.Item key="acciones">
          <Link to="/acciones">Acciones</Link>
        </Menu.Item>
      </Menu>
    </Header>
  );
}

export default Navbar;
