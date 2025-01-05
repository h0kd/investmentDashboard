// src/components/Dashboard.js
import React, { useState, useEffect } from "react";

function Dashboard() {
  const [summary, setSummary] = useState(null); // para guardar la data de /api/summary
  const [error, setError] = useState(null);

  useEffect(() => {
    // Llamada a la API para obtener summary
    fetch("http://localhost:5000/api/summary", {
      method: "GET",
      credentials: "include", // Importante si usas Flask-Login y sesión
    })
      .then((response) => {
        if (!response.ok) {
          // Si el servidor devolvió algo como 401 o 500
          throw new Error(`Error del servidor, código ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (data.success === false) {
          // Tu API podría devolver success: false en caso de error
          throw new Error(data.error || "Error al obtener los datos");
        }
        setSummary(data); // Guardamos la info en el estado
      })
      .catch((err) => {
        console.error("Error al obtener el summary:", err);
        setError(err.message);
      });
  }, []);

  // Renderiza algo simple mientras cargan los datos
  if (!summary && !error) {
    return <p>Cargando datos...</p>;
  }

  if (error) {
    return <p style={{ color: "red" }}>Error: {error}</p>;
  }

  // Una vez que tienes "summary" con la data, puedes mostrarla:
  const {
    total_empresas,
    total_acciones,
    valor_total_invertido,
    total_dividendos,
  } = summary;

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto" }}>
      <h2>Dashboard</h2>
      <div style={{ display: "grid", gap: "1rem" }}>
        <div style={{ background: "#ededed", padding: "1rem" }}>
          <strong>Empresas Registradas:</strong> {total_empresas}
        </div>
        <div style={{ background: "#d2f8d2", padding: "1rem" }}>
          <strong>Total Acciones:</strong> {total_acciones}
        </div>
        <div style={{ background: "#d2e8f8", padding: "1rem" }}>
          <strong>Valor Total Invertido:</strong> {valor_total_invertido}
        </div>
        <div style={{ background: "#f7efd2", padding: "1rem" }}>
          <strong>Total Dividendos:</strong> {total_dividendos}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
