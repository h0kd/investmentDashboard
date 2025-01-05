// src/components/Login.js
import React, { useState } from "react";
// Ojo: usa la versión de React Router que tengas (v6 usa useNavigate)
import { useNavigate } from "react-router-dom";
import { Button, Checkbox, Form, Input } from "antd";

function Login() {
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const onFinish = async (values) => {
    console.log("Success:", values);

    const { username, password } = values;

    // Instanciamos el hook para la navegación
    try {
      const response = await fetch("http://localhost:5000/api/login", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      if (response.ok && data.success) {
        // Login exitoso
        setMessage("¡Inicio de sesión exitoso!");
        // Redirigimos a "/dashboard"
        navigate("/dashboard");
      } else {
        // Muestra el mensaje de error enviado por el backend
        setMessage(data.message || "Error al iniciar sesión");
      }
    } catch (error) {
      console.error("Error al hacer login:", error);
      setMessage("Error de red o del servidor");
    }
  };

  const onFinishFailed = (errorInfo) => {
    console.log("Error al validar el formulario:", errorInfo);
  };

  return (
    <div style={{ maxWidth: "400px", margin: "0 auto" }}>
      <h2>Iniciar Sesión</h2>
      <Form
        name="basic"
        labelCol={{
          span: 8,
        }}
        wrapperCol={{
          span: 16,
        }}
        style={{
          maxWidth: 600,
        }}
        initialValues={{
          remember: true,
        }}
        onFinish={onFinish}
        onFinishFailed={onFinishFailed}
        autoComplete="off"
      >
        <Form.Item
          label="Nombre de usuario"
          name="username"
          rules={[
            {
              required: true,
              message: "Escriba su nombre de usuario!",
            },
          ]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          label="Contrasena"
          name="password"
          rules={[
            {
              required: true,
              message: "Escriba su contraseña!",
            },
          ]}
        >
          <Input.Password />
        </Form.Item>

        <Form.Item name="remember" valuePropName="checked" label={null}>
          <Checkbox>Recordarme</Checkbox>
        </Form.Item>

        <Form.Item label={null}>
          <Button type="primary" htmlType="submit">
            Login
          </Button>
        </Form.Item>
      </Form>

      {message && <p style={{ color: "green" }}>{message}</p>}
    </div>
  );
}

export default Login;
