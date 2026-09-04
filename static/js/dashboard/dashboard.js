function initDashboardCharts() {
    const rawDataElement = document.getElementById('datos-graficos');
    if (!rawDataElement) return;

    let datos;
    try {
        datos = JSON.parse(rawDataElement.textContent);
    } catch (e) {
        console.error('Error parseando datos de gráficos:', e);
        return;
    }

    if (typeof Chart === 'undefined') {
        console.warn('Chart.js no está cargado. Intentando cargar dinámicamente...');
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js';
        script.onload = function () {
            initDashboardCharts();
        };
        document.head.appendChild(script);
        return;
    }

    // Paletas de Colores Armónicas
    const paletaPastelPagos = ['#10b981', '#ef4444'];
    const paletaPastelSouvenirs = ['#8b5cf6', '#f59e0b'];
    const paletaSexo = ['#2563eb', '#ec4899', '#94a3b8'];
    const paletaEstados = ['#10b981', '#f59e0b', '#ef4444', '#64748b'];
    const paletaEdades = ['#06b6d4', '#3b82f6', '#8b5cf6', '#f97316'];

    const opcionesComunes = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    boxWidth: 12,
                    padding: 14,
                    font: { size: 12, family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" },
                },
            },
            tooltip: {
                backgroundColor: '#1e293b',
                padding: 10,
                cornerRadius: 8,
                titleFont: { size: 13, weight: 'bold' },
                bodyFont: { size: 12 },
            },
        },
    };

    // 1. Gráfico de Pastel: Estado de Pagos
    const elPagos = document.getElementById('graficoPagos');
    if (elPagos && datos.pagos) {
        new Chart(elPagos, {
            type: 'pie',
            data: {
                labels: datos.pagos.labels,
                datasets: [{
                    data: datos.pagos.data,
                    backgroundColor: paletaPastelPagos,
                    borderWidth: 2,
                    borderColor: '#ffffff',
                }],
            },
            options: Object.assign({}, opcionesComunes),
        });
    }

    // 2. Gráfico de Pastel: Entrega de Souvenirs
    const elSouvenirs = document.getElementById('graficoSouvenirs');
    if (elSouvenirs && datos.souvenirs) {
        new Chart(elSouvenirs, {
            type: 'pie',
            data: {
                labels: datos.souvenirs.labels,
                datasets: [{
                    data: datos.souvenirs.data,
                    backgroundColor: paletaPastelSouvenirs,
                    borderWidth: 2,
                    borderColor: '#ffffff',
                }],
            },
            options: Object.assign({}, opcionesComunes),
        });
    }

    // 3. Gráfico de Rosquilla: Género / Sexo
    const elSexo = document.getElementById('graficoSexo');
    if (elSexo && datos.sexo) {
        new Chart(elSexo, {
            type: 'doughnut',
            data: {
                labels: datos.sexo.labels,
                datasets: [{
                    data: datos.sexo.data,
                    backgroundColor: paletaSexo,
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 4,
                }],
            },
            options: Object.assign({}, opcionesComunes, {
                cutout: '65%',
            }),
        });
    }

    // 4. Gráfico de Barras: Estados Administrativos
    const elEstados = document.getElementById('graficoEstados');
    if (elEstados && datos.estados) {
        new Chart(elEstados, {
            type: 'bar',
            data: {
                labels: datos.estados.labels,
                datasets: [{
                    data: datos.estados.data,
                    backgroundColor: paletaEstados,
                    borderRadius: 6,
                }],
            },
            options: Object.assign({}, opcionesComunes, {
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        grid: { color: '#f1f5f9' },
                    },
                    x: {
                        grid: { display: false },
                    },
                },
            }),
        });
    }

    // 5. Gráfico de Barras: Rangos de Edad
    const elEdades = document.getElementById('graficoEdades');
    if (elEdades && datos.edades) {
        new Chart(elEdades, {
            type: 'bar',
            data: {
                labels: datos.edades.labels,
                datasets: [{
                    data: datos.edades.data,
                    backgroundColor: paletaEdades,
                    borderRadius: 6,
                }],
            },
            options: Object.assign({}, opcionesComunes, {
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        grid: { color: '#f1f5f9' },
                    },
                    x: {
                        grid: { display: false },
                    },
                },
            }),
        });
    }

    // 6. Gráfico de Línea: Tendencia de Inscripciones
    const elTendencia = document.getElementById('graficoTendencia');
    if (elTendencia && datos.tendencia) {
        const ctx = elTendencia.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 260);
        gradient.addColorStop(0, 'rgba(59, 130, 246, 0.35)');
        gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

        new Chart(elTendencia, {
            type: 'line',
            data: {
                labels: datos.tendencia.labels,
                datasets: [{
                    label: 'Nuevos Socios Registrados',
                    data: datos.tendencia.data,
                    borderColor: '#2563eb',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#2563eb',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                }],
            },
            options: Object.assign({}, opcionesComunes, {
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        grid: { color: '#f1f5f9' },
                    },
                    x: {
                        grid: { color: '#f8fafc' },
                    },
                },
            }),
        });
    }

    // 8. Gráfico Radar: Salud Operativa
    const elRadar = document.getElementById('graficoRadar');
    if (elRadar && datos.radar) {
        new Chart(elRadar, {
            type: 'radar',
            data: {
                labels: datos.radar.labels,
                datasets: [{
                    label: 'Nivel (%)',
                    data: datos.radar.data,
                    borderColor: '#0284c7',
                    backgroundColor: 'rgba(2, 132, 199, 0.22)',
                    borderWidth: 2,
                    pointBackgroundColor: '#0284c7',
                    pointBorderColor: '#ffffff',
                    pointRadius: 4,
                }],
            },
            options: Object.assign({}, opcionesComunes, {
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: { stepSize: 25, backdropColor: 'transparent' },
                        grid: { color: '#e2e8f0' },
                        angleLines: { color: '#f1f5f9' },
                    },
                },
            }),
        });
    }

    // 9. Gráfico de Barras Horizontales: Distribución por Asociacion y Conjunto
    const elDistribucion = document.getElementById('graficoDistribucion');
    if (elDistribucion && datos.distribucion) {
        new Chart(elDistribucion, {
            type: 'bar',
            data: {
                labels: datos.distribucion.labels,
                datasets: [{
                    data: datos.distribucion.data,
                    backgroundColor: '#3b82f6',
                    borderRadius: 6,
                }],
            },
            options: Object.assign({}, opcionesComunes, {
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        grid: { color: '#f1f5f9' },
                    },
                    y: {
                        grid: { display: false },
                    },
                },
            }),
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    initDashboardCharts();
});