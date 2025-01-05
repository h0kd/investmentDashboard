// src/components/Acciones.js

import React, { useEffect, useState } from "react";
// import { useNavigate } from "react-router-dom";
// Si quieres verificar si el usuario no está logueado y redirigir, etc.

import "chart.js/auto";
import { Table } from "antd"; // si prefieres Ant Design, o un <table> HTML normal
import { Bar } from "react-chartjs-2"; // de react-chartjs-2

function Acciones() {
  const [acciones, setAcciones] = useState([]);
  const [totalCompras, setTotalCompras] = useState(0);
  const [totalVentas, setTotalVentas] = useState(0);
  const [chartLabels, setChartLabels] = useState([]);
  const [chartData, setChartData] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Llamada a la API /api/acciones cuando se monta el componente
  useEffect(() => {
    fetch("http://localhost:5000/api/acciones", {
      credentials: "include", // Para incluir cookies de sesión si usas Flask-Login
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Error en servidor: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        if (!data.success) {
          throw new Error(data.error || "Error desconocido en /api/acciones");
        }
        // Guardamos la data en el estado
        setAcciones(data.acciones);
        setTotalCompras(data.total_compras);
        setTotalVentas(data.total_ventas);
        setChartLabels(data.labels);
        setChartData(data.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching acciones:", err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <p>Cargando datos de acciones...</p>;
  }

  if (error) {
    return <p style={{ color: "red" }}>Error: {error}</p>;
  }

  // Opcional: Si usas react-chartjs-2, construimos la config de la Bar chart
  const barChartData = {
    labels: chartLabels,
    datasets: [
      {
        label: "Total Compras por Empresa",
        data: chartData,
        backgroundColor: "rgba(54, 162, 235, 0.6)",
      },
    ],
  };

  // Si usas Ant Design Table
  const columns = [
    {
      title: "#",
      dataIndex: "indice",
      key: "indice",
      width: "60px",
    },
    {
      title: "Nombre Empresa",
      dataIndex: "nombre",
      key: "nombre",
    },
    {
      title: "RUT",
      dataIndex: "rut",
      key: "rut",
    },
    {
      title: "Total Acciones",
      dataIndex: "cantidad",
      key: "cantidad",
    },
  ];

  return (
    <div style={{ margin: "2rem" }}>
      <h2>Acciones</h2>

      {/* Botones (como Facturas, etc.) si los necesitas */}
      <div style={{ marginBottom: "1rem" }}>
        <button style={{ marginRight: "1rem" }} className="btn btn-info">
          Facturas
        </button>
      </div>

      {/* Tabla de acciones */}
      <Table
        columns={columns}
        dataSource={acciones}
        rowKey={(record) => record.indice}
        pagination={false}
      />

      {/* Totales de compras/ventas */}
      <div
        style={{
          marginTop: "1rem",
          background: "#333",
          color: "#fff",
          padding: "1rem",
        }}
      >
        <div>
          <strong>Total en Compras:</strong> {totalCompras.toLocaleString()}
        </div>
        <div>
          <strong>Total en Ventas:</strong> {totalVentas.toLocaleString()}
        </div>
      </div>

      {/* Gráfico con Chart.js */}
      <div style={{ maxWidth: "600px", marginTop: "2rem" }}>
        <h3>Grafico - Compras por Empresa</h3>
        <Bar data={barChartData} />
      </div>
    </div>
  );
}

export default Acciones;
