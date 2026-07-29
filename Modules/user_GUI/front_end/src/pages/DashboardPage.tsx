import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
    Area,
    AreaChart,
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Legend,
    Line,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "../styles/dashboard.css";
import type {
    SummaryCard,
    HousingTrendPoint,
    HousingRegionPoint,
    HousingMapPoint,
} from "../interfaces";
import {
    loadHousingSummary,
    loadHousingTrends,
    loadHousingRegions,
    loadHousingMapPoints,
} from "../services";

const markerIcon = new L.Icon({
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
});

const chartPalette = ["#0f766e", "#2563eb", "#7c3aed", "#ea580c", "#059669"];

const formatCurrency = (value: number | string | null | undefined) => {
    const numericValue =
        typeof value === "string" ? Number(value.replace(/[^0-9.-]+/g, "")) : value;

    if (numericValue === null || numericValue === undefined || Number.isNaN(numericValue)) {
        return "N/A";
    }

    return new Intl.NumberFormat("en-CA", {
        style: "currency",
        currency: "CAD",
        maximumFractionDigits: 0,
    }).format(numericValue);
};

const formatNumber = (value: number | string | null | undefined) => {
    const numericValue = typeof value === "string" ? Number(value) : value;

    if (numericValue === null || numericValue === undefined || Number.isNaN(numericValue)) {
        return "0";
    }

    return new Intl.NumberFormat("en-CA").format(numericValue);
};

const formatShortDate = (value: string) => {
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return value;
    return parsed.toLocaleDateString("en-CA", {
        month: "short",
        day: "numeric",
    });
};

function FitMapBounds({ points }: { points: HousingMapPoint[] }) {
    const map = useMap();

    useEffect(() => {
        if (!points.length) return;

        const bounds = L.latLngBounds(
            points.map((point) => [Number(point.latitude), Number(point.longitude)] as [number, number])
        );

        map.fitBounds(bounds, { padding: [24, 24] });
    }, [map, points]);

    return null;
}

export function DashboardPage() {
    const navigate = useNavigate();
    const location = useLocation();

    const [summaryCards, setSummaryCards] = useState<SummaryCard[]>([
        { label: "Average Rent", value: "Loading..." },
        { label: "Listing Volume", value: "Loading..." },
        { label: "New Listings", value: "Loading..." },
        { label: "Days on Market", value: "Loading..." },
    ]);

    const [loading, setLoading] = useState(true);
    const [updatesCount, setUpdatesCount] = useState(0);
    const [errorMessage, setErrorMessage] = useState("");
    const [spiderRunMessage, setSpiderRunMessage] = useState("");

    const [dailyTrend, setDailyTrend] = useState<HousingTrendPoint[]>([]);
    const [regionTrend, setRegionTrend] = useState<HousingRegionPoint[]>([]);
    const [mapPoints, setMapPoints] = useState<HousingMapPoint[]>([]);

    const fetchDashboardData = useCallback(async () => {
        try {
            setLoading(true);
            setErrorMessage("");

            const results = await Promise.allSettled([
                loadHousingSummary(),
                loadHousingTrends(),
                loadHousingRegions(),
                loadHousingMapPoints(),
            ]);

            const summary =
                results[0].status === "fulfilled"
                    ? results[0].value
                    : {
                        avgPrice: "No data",
                        salesVolume: "0",
                        newListings: "0",
                        daysOnMarket: "0",
                        updatesCount: 0,
                        error: "Unable to load summary data.",
                    };

            const trends = results[1].status === "fulfilled" ? results[1].value : [];
            const regions = results[2].status === "fulfilled" ? results[2].value : [];
            const points = results[3].status === "fulfilled" ? results[3].value : [];

            if (results[3].status === "rejected") {
                console.error("Map data failed:", results[3].reason);
            }

            setUpdatesCount(summary?.updatesCount ?? 0);
            setSummaryCards([
                { label: "Average Rent", value: summary?.avgPrice ?? "No data" },
                { label: "Listing Volume", value: summary?.salesVolume ?? "No data" },
                { label: "New Listings", value: summary?.newListings ?? "No data" },
                { label: "Days on Market", value: summary?.daysOnMarket ?? "No data" },
            ]);

            setDailyTrend(Array.isArray(trends) ? trends : []);
            setRegionTrend(Array.isArray(regions) ? regions : []);
            setMapPoints(Array.isArray(points) ? points : []);

            if (summary?.error) {
                setErrorMessage(summary.error);
            }
        } catch (error) {
            console.error("Failed to load dashboard data:", error);

            setSummaryCards([
                { label: "Average Rent", value: "No data" },
                { label: "Listing Volume", value: "No data" },
                { label: "New Listings", value: "No data" },
                { label: "Days on Market", value: "No data" },
            ]);

            setDailyTrend([]);
            setRegionTrend([]);
            setMapPoints([]);
            setUpdatesCount(0);
            setErrorMessage("Dashboard analytics are temporarily unavailable.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDashboardData();
    }, [fetchDashboardData]);

    useEffect(() => {
        const state = location.state as
            | { refreshDashboard?: boolean; spiderRunMessage?: string }
            | null;

        if (state?.spiderRunMessage) {
            setSpiderRunMessage(state.spiderRunMessage);
        }

        if (state?.refreshDashboard) {
            fetchDashboardData();
            navigate(location.pathname, { replace: true, state: null });
        }
    }, [location.state, location.pathname, navigate, fetchDashboardData]);

    const validMapPoints = useMemo(
        () =>
            mapPoints
                .map((point) => ({
                    ...point,
                    latitude:
                        typeof point.latitude === "string"
                            ? Number(point.latitude)
                            : point.latitude,
                    longitude:
                        typeof point.longitude === "string"
                            ? Number(point.longitude)
                            : point.longitude,
                }))
                .filter(
                    (point) =>
                        Number.isFinite(point.latitude) &&
                        Number.isFinite(point.longitude)
                ),
        [mapPoints]
    );

    const adjustedMapPoints = useMemo(() => {
        const seen = new Map<string, number>();

        return validMapPoints.map((point) => {
            const lat = Number(point.latitude);
            const lng = Number(point.longitude);
            const key = `${lat.toFixed(6)},${lng.toFixed(6)}`;
            const count = seen.get(key) ?? 0;

            seen.set(key, count + 1);

            if (count === 0) {
                return {
                    ...point,
                    displayLat: lat,
                    displayLng: lng,
                };
            }

            const angle = count * 0.9;
            const offset = 0.00018 * count;

            return {
                ...point,
                displayLat: lat + Math.cos(angle) * offset,
                displayLng: lng + Math.sin(angle) * offset,
            };
        });
    }, [validMapPoints]);

    const mapCenter = useMemo<[number, number]>(() => {
        if (!validMapPoints.length) {
            return [49.2827, -123.1207];
        }

        const avgLat =
            validMapPoints.reduce((sum, point) => sum + Number(point.latitude ?? 0), 0) /
            validMapPoints.length;

        const avgLng =
            validMapPoints.reduce((sum, point) => sum + Number(point.longitude ?? 0), 0) /
            validMapPoints.length;

        return [avgLat, avgLng];
    }, [validMapPoints]);

    useEffect(() => {
        const uniqueCoords = new Set(
            validMapPoints.map(
                (point) =>
                    `${Number(point.latitude).toFixed(6)},${Number(point.longitude).toFixed(6)}`
            )
        );

        console.log("Total map points:", validMapPoints.length);
        console.log("Unique coordinate pairs:", uniqueCoords.size);
    }, [validMapPoints]);

    return (
        <div className="dashboard-home">
            <section className="dashboard-section">
                <div className="dashboard-section-header">
                    <div>
                        <h2>Market summary</h2>
                        <p className="dashboard-section-subtitle">
                            Latest rental market indicators from your connected data sources.
                        </p>
                    </div>

                    {updatesCount > 0 ? (
                        <div className="dashboard-update-pill">
                            {formatNumber(updatesCount)} updates in the last 7 days
                        </div>
                    ) : null}
                </div>

                {loading && (
                    <div className="dashboard-message loading">
                        Loading housing summary...
                    </div>
                )}

                {spiderRunMessage && (
                    <div className="dashboard-message success">{spiderRunMessage}</div>
                )}

                {errorMessage && (
                    <div className="dashboard-message error">{errorMessage}</div>
                )}

                <div className="dashboard-cards">
                    {summaryCards.map((card) => (
                        <div key={card.label} className="dashboard-card">
                            <h3>{card.label}</h3>
                            <p>{card.value}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section className="dashboard-analytics-grid">
                <div className="dashboard-chart-card">
                    <div className="dashboard-chart-header">
                        <h3>Average rent over time</h3>
                    </div>

                    <div className="dashboard-chart-frame">
                        {dailyTrend.length ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart
                                    data={dailyTrend}
                                    margin={{ top: 16, right: 20, left: 8, bottom: 10 }}
                                >
                                    <defs>
                                        <linearGradient id="rentAreaGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#0f766e" stopOpacity={0.28} />
                                            <stop offset="95%" stopColor="#0f766e" stopOpacity={0.04} />
                                        </linearGradient>
                                    </defs>

                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis dataKey="day" tickFormatter={formatShortDate} tickMargin={10} />
                                    <YAxis
                                        yAxisId="price"
                                        width={86}
                                        tickFormatter={(value) => `$${formatNumber(value)}`}
                                    />
                                    <YAxis
                                        yAxisId="count"
                                        orientation="right"
                                        width={70}
                                        tickFormatter={(value) => formatNumber(value)}
                                    />
                                    <Tooltip
                                        formatter={(value, name) => {
                                            const safeName = String(name ?? "");
                                            const numericValue = Array.isArray(value)
                                                ? Number(value[0] ?? 0)
                                                : Number(value ?? 0);

                                            if (safeName === "avg_price") {
                                                return [formatCurrency(numericValue), "Average rent"];
                                            }

                                            if (safeName === "listing_count") {
                                                return [formatNumber(numericValue), "Listings"];
                                            }

                                            return [formatNumber(numericValue), safeName];
                                        }}
                                        labelFormatter={(label) => formatShortDate(String(label ?? ""))}
                                    />
                                    <Legend />
                                    <Area
                                        yAxisId="price"
                                        type="monotone"
                                        dataKey="avg_price"
                                        name="Average rent"
                                        stroke="#0f766e"
                                        strokeWidth={2}
                                        fill="url(#rentAreaGradient)"
                                    />
                                    <Line
                                        yAxisId="count"
                                        type="monotone"
                                        dataKey="listing_count"
                                        name="Listings"
                                        stroke="#2563eb"
                                        strokeWidth={2}
                                        dot={{ r: 3 }}
                                        activeDot={{ r: 5 }}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="dashboard-empty-state">No daily trend data available.</div>
                        )}
                    </div>
                </div>

                <div className="dashboard-chart-card">
                    <div className="dashboard-chart-header">
                        <h3>Listings by region</h3>
                    </div>

                    <div className="dashboard-chart-frame">
                        {regionTrend.length ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                    data={regionTrend}
                                    margin={{ top: 16, right: 20, left: 8, bottom: 45 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis
                                        dataKey="region"
                                        angle={-24}
                                        textAnchor="end"
                                        interval={0}
                                        height={78}
                                    />
                                    <YAxis tickFormatter={(value) => formatNumber(value)} />
                                    <Tooltip
                                        formatter={(value, name) => {
                                            const safeName = String(name ?? "");
                                            const numericValue = Array.isArray(value)
                                                ? Number(value[0] ?? 0)
                                                : Number(value ?? 0);

                                            if (safeName === "avg_price") {
                                                return [formatCurrency(numericValue), "Average rent"];
                                            }

                                            if (safeName === "listings") {
                                                return [formatNumber(numericValue), "Listings"];
                                            }

                                            return [formatNumber(numericValue), safeName];
                                        }}
                                    />
                                    <Legend />
                                    <Bar dataKey="listings" name="Listings" radius={[8, 8, 0, 0]}>
                                        {regionTrend.map((entry, index) => (
                                            <Cell
                                                key={`${entry.region}-${index}`}
                                                fill={chartPalette[index % chartPalette.length]}
                                            />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="dashboard-empty-state">No regional trend data available.</div>
                        )}
                    </div>
                </div>

                <div className="dashboard-section dashboard-map-panel">
                    <div className="dashboard-panel-header">
                        <div>
                            <h2>Market map</h2>
                            <p className="dashboard-section-subtitle">
                                Listings with geocoded coordinates across Vancouver.
                            </p>
                        </div>
                    </div>

                    <div className="dashboard-map-body">
                        <div className="dashboard-map-frame">
                            {adjustedMapPoints.length ? (
                                <MapContainer
                                    center={mapCenter}
                                    zoom={11}
                                    scrollWheelZoom={true}
                                    className="dashboard-leaflet-map"
                                >
                                    <TileLayer
                                        attribution='&copy; OpenStreetMap contributors'
                                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                    />
                                    <FitMapBounds points={validMapPoints} />

                                    {adjustedMapPoints.map((point) => (
                                        <Marker
                                            key={`${point.id}-${point.displayLat}-${point.displayLng}`}
                                            position={[point.displayLat, point.displayLng]}
                                            icon={markerIcon}
                                        >
                                            <Popup>
                                                <div className="dashboard-map-popup">
                                                    <strong>{point.user_post_title || "Listing"}</strong>
                                                    <div>{formatCurrency(point.price)}</div>
                                                    <div>
                                                        {point.street_number || point.address_osm || "Address unavailable"}
                                                    </div>
                                                    <div>
                                                        {point.clean_general_area ||
                                                            point.general_area ||
                                                            point.city ||
                                                            "Vancouver"}
                                                    </div>
                                                    {point.post_url ? (
                                                        <a
                                                            href={point.post_url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                        >
                                                            Open listing
                                                        </a>
                                                    ) : null}
                                                </div>
                                            </Popup>
                                        </Marker>
                                    ))}
                                </MapContainer>
                            ) : (
                                <div className="dashboard-empty-state">
                                    No geocoded listings available for the map yet.
                                </div>
                            )}
                        </div>

                        <div className="dashboard-map-meta">
                            {formatNumber(validMapPoints.length)} geocoded listing points are available from the API.
                        </div>
                    </div>
                </div>
            </section>

            <section className="dashboard-hero dashboard-hero-bottom">
                <div className="dashboard-hero-card dashboard-hero-main">
                    <h2>Vancouver rental market workspace</h2>
                    <p>
                        Track housing documents, connect Gmail imports, run spiders, and review analytics
                        from one dashboard built for the rental market project.
                    </p>

                    <div className="dashboard-hero-actions">
                        <button
                            className="app-primary-button"
                            onClick={() => navigate("/app/gmail")}
                        >
                            Open Gmail Setup
                        </button>

                        <button
                            className="app-secondary-button"
                            onClick={() => navigate("/app/spider")}
                        >
                            Run Spiders
                        </button>
                    </div>
                </div>
            </section>
        </div>
    );
}