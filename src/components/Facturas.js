import React, { useEffect, useState } from "react";
import { Table } from "antd";

function Facturas() {
	const [facturas, setFacturas] = useState([]);
	const [sortBy, setSortBy] = useState("NumeroFactura");
	const [order, setOrder] = useState("asc");
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);

	// Llamada al endpoint /api/facturas
	useEffect(() => {
		fetch(
			`http://localhost:5000/api/facturas?sort_by=${sortBy}&order=${order}`,
			{
				credentials: "include", // Si usas Flask-Login/sesiones
			}
		)
			.then((response) => {
				if (!response.ok) {
					throw new Error(
						`Error al consultar facturas. Código: ${response.status}`
					);
				}
				return response.json();
			})
			.then((data) => {
				if (!data.success) {
					throw new Error(data.error || "Error desconocido.");
				}
				setFacturas(data.facturas);
				setSortBy(data.sort_by);
				setOrder(data.order);
				setLoading(false);
			})
			.catch((err) => {
				console.error("Error:", err);
				setError(err.message);
				setLoading(false);
			});
	}, [sortBy, order]);

	if (loading) {
		return <p>Cargando facturas...</p>;
	}

	if (error) {
		return <p style={{ color: "red" }}>Error: {error}</p>;
	}

	// Columnas de la tabla
	const columns = [
		{
			title: "N° Factura",
			dataIndex: "numeroFactura",
			key: "numeroFactura",
		},
		{
			title: "Empresa Emisora",
			dataIndex: "empresaEmisora",
			key: "empresaEmisora",
		},
		{
			title: "Corredora",
			dataIndex: "corredora",
			key: "corredora",
		},
		{
			title: "Nombre Activo",
			dataIndex: "nombreActivo",
			key: "nombreActivo",
		},
		{
			title: "Tipo",
			dataIndex: "tipo",
			key: "tipo",
		},
		{
			title: "Fecha",
			dataIndex: "fecha",
			key: "fecha",
		},
		{
			title: "Cantidad",
			dataIndex: "cantidad",
			key: "cantidad",
			render: (cantidad) =>
				cantidad.toLocaleString("en-US", { minimumFractionDigits: 2 }),
		},
		{
			title: "Precio Unitario",
			dataIndex: "precioUnitario",
			key: "precioUnitario",
			render: (pu) => pu.toLocaleString("en-US", { minimumFractionDigits: 2 }),
		},
		{
			title: "Sub Total",
			dataIndex: "subTotal",
			key: "subTotal",
			render: (st) => st.toLocaleString("en-US", { minimumFractionDigits: 2 }),
		},
		{
			title: "Valor Total",
			dataIndex: "valor",
			key: "valor",
			render: (val) =>
				val.toLocaleString("en-US", { minimumFractionDigits: 2 }),
		},
		{
			title: "Factura (PDF)",
			dataIndex: "adjuntoFactura",
			key: "adjuntoFactura",
			render: (archivo) =>
				archivo ? (
					<a href={archivo} target="_blank" rel="noreferrer">
						Ver PDF
					</a>
				) : (
					<span>Sin archivo</span>
				),
		},
		{
			title: "Acciones",
			key: "acciones",
			render: (_, record) => (
				<>
					<button className="btn btn-primary btn-sm me-2">Editar</button>
					<button className="btn btn-danger btn-sm">Eliminar</button>
				</>
			),
		},
	];

	return (
		<div style={{ margin: "2rem" }}>
			<h1>Listado de Facturas</h1>
			{/* Botón para agregar factura, etc. */}
			<button className="btn btn-info mb-3">Agregar Factura</button>

			<Table
				columns={columns}
				dataSource={facturas}
				rowKey="numeroFactura"
				pagination={false}
			/>
			<br />
			{/* Botón para volver a la página de Acciones, por ejemplo */}
			<a href="/acciones" className="btn btn-info">
				Volver a Acciones
			</a>
		</div>
	);
}

export default Facturas;
