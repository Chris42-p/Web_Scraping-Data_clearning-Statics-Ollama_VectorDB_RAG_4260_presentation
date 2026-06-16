import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { APP_CONFIG } from "../config";

type SpiderItem = {
    key: string;
    label: string;
};

type SpiderRunApiResponse = {
    message?: string;
    result?: {
        status?: string;
        spider?: string;
        message?: string;
    };
    summary?: {
        avgPrice: string;
        salesVolume: string;
        newListings: string;
        daysOnMarket: string;
        updatesCount: number;
    };
    nextRunAt?: string | null;
};

export function SpiderPage() {
    const navigate = useNavigate();
    const [spiders, setSpiders] = useState<SpiderItem[]>([]);
    const [loading, setLoading] = useState(false);
    const [activeSpiderKey, setActiveSpiderKey] = useState("");
    const [error, setError] = useState("");
    const [runMessage, setRunMessage] = useState("");

    useEffect(() => {
        const loadSpiders = async () => {
            try {
                setError("");

                const res = await fetch(`${APP_CONFIG.apiBaseUrl}/spiders`, {
                    credentials: "include",
                });

                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Failed to load spiders");

                setSpiders(data.spiders || []);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Unknown error");
            }
        };

        loadSpiders();
    }, []);

    const handleRunSpider = async (spiderKey: string) => {
        try {
            setLoading(true);
            setActiveSpiderKey(spiderKey);
            setError("");
            setRunMessage("");

            const res = await fetch(`${APP_CONFIG.apiBaseUrl}/spiders/run`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({ spider_key: spiderKey }),
            });

            const data: SpiderRunApiResponse = await res.json();

            if (!res.ok) {
                throw new Error((data as any)?.detail || "Failed to run spider");
            }

            const updatesCount = data.summary?.updatesCount ?? 0;
            const newListings = data.summary?.newListings ?? "0";
            const message =
                data.result?.message ||
                `Spider completed: ${updatesCount} update${updatesCount === 1 ? "" : "s"} detected, ${newListings} listings in summary.`;

            setRunMessage(message);

            navigate("/app/dashboard", {
                state: {
                    refreshDashboard: true,
                    spiderRunMessage: `Spider completed: ${updatesCount} update${updatesCount === 1 ? "" : "s"} detected, ${newListings} listings in summary.`,
                },
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
        } finally {
            setLoading(false);
            setActiveSpiderKey("");
        }
    };

    return (
        <div className="dashboard-page spider-page">

            {error && <p className="settings-error">{error}</p>}

            {runMessage && <div className="dashboard-message success">{runMessage}</div>}

            <div className="spider-actions">
                {spiders.map((spider) => (
                    <button
                        key={spider.key}
                        className="dashboard-button"
                        onClick={() => handleRunSpider(spider.key)}
                        disabled={loading}
                    >
                        {loading && activeSpiderKey === spider.key
                            ? "Running..."
                            : `Run ${spider.label}`}
                    </button>
                ))}
            </div>
        </div>
    );
}