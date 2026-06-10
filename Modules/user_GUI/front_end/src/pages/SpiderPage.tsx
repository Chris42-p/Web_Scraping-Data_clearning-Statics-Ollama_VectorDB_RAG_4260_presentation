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
    const [result, setResult] = useState<any>(null);

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
            setResult(null);

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
            setResult(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1>Spiders</h1>
            <p>Run rental and neighbourhood data spiders from the dashboard.</p>

            {error && <p style={{ color: "red" }}>{error}</p>}

            <div style={{ display: "grid", gap: "12px", marginTop: "16px" }}>
                {spiders.map((spider) => (
                    <button
                        key={spider.key}
                        onClick={() => handleRunSpider(spider.key)}
                        disabled={loading}
                    >
                        {loading ? "Running..." : `Run ${spider.label}`}
                    </button>
                ))}
            </div>

            {result && (
                <div style={{ marginTop: "24px" }}>
                    <h2>Spider Result</h2>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}