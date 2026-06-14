import { useEffect, useState } from "react";
import { APP_CONFIG } from "../config";

type SpiderItem = {
    key: string;
    label: string;
};

export function SpiderPage() {
    const [spiders, setSpiders] = useState<SpiderItem[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadSpiders = async () => {
            try {
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
            setError("");

            const res = await fetch(`${APP_CONFIG.apiBaseUrl}/spiders/run`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({ spider_key: spiderKey }),
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Failed to run spider");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard-page spider-page">
            <div className="dashboard-header"></div>

            {error && <p className="settings-error">{error}</p>}

            <div className="spider-actions">
                {spiders.map((spider) => (
                    <button
                        key={spider.key}
                        className="dashboard-button"
                        onClick={() => handleRunSpider(spider.key)}
                        disabled={loading}
                    >
                        {loading ? "Running..." : `Run ${spider.label}`}
                    </button>
                ))}
            </div>
        </div>
    );
}