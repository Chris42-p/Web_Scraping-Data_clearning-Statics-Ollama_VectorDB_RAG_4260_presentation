import { useEffect, useMemo, useState } from "react";
import type { SpiderConfig, SpiderStatus } from "../interfaces";
import {
    loadSpiderConfig,
    loadSpiderStatus,
    saveSpiderConfig,
} from "../services";

const DEFAULT_CONFIG: SpiderConfig = {
    enabled: false,
    intervalMinutes: 30,
    region: "Vancouver",
    keywords: "rental apartment",
    maxPages: 5,
};

const MAX_SPIDER_PAGES = 100;

const DEFAULT_STATUS: SpiderStatus = {
    lastRunAt: undefined,
    nextRunAt: undefined,
    isRunning: false,
};

const SPIDER_OPTIONS = [
    { key: "rew", label: "REW Spider" },
    { key: "kijiji", label: "Kijiji Spider" },
    { key: "realtylink", label: "RealtyLink Spider" },
    { key: "craigslist", label: "Craigslist Spider" },
    { key: "safety_convenience", label: "Safety & Convenience Spider" },
] as const;

export function SettingsPage() {
    const [selectedSpiderKey, setSelectedSpiderKey] = useState<string>(SPIDER_OPTIONS[0].key);
    const [spiderConfig, setSpiderConfig] = useState<SpiderConfig>(DEFAULT_CONFIG);
    const [spiderStatus, setSpiderStatus] = useState<SpiderStatus>(DEFAULT_STATUS);
    const [isSavingConfig, setIsSavingConfig] = useState(false);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [secondsLeft, setSecondsLeft] = useState<number>(DEFAULT_CONFIG.intervalMinutes * 60);

    useEffect(() => {
        async function initializeSpiderSettings() {
            setError("");
            setMessage("");

            const [configResult, statusResult] = await Promise.allSettled([
                loadSpiderConfig(selectedSpiderKey),
                loadSpiderStatus(),
            ]);

            if (configResult.status === "fulfilled") {
                setSpiderConfig(configResult.value);
                setSecondsLeft(configResult.value.intervalMinutes * 60);
            } else {
                console.error(`loadSpiderConfig failed for ${selectedSpiderKey}:`, configResult.reason);
                setSpiderConfig(DEFAULT_CONFIG);
                setSecondsLeft(DEFAULT_CONFIG.intervalMinutes * 60);
            }

            if (statusResult.status === "fulfilled") {
                setSpiderStatus(statusResult.value);
            } else {
                console.error("loadSpiderStatus failed:", statusResult.reason);
                setSpiderStatus(DEFAULT_STATUS);
            }

            if (configResult.status === "rejected" || statusResult.status === "rejected") {
                setError("Failed to load some spider settings.");
            }
        }

        initializeSpiderSettings();
    }, [selectedSpiderKey]);

    useEffect(() => {
        setSecondsLeft(spiderConfig.intervalMinutes * 60);
    }, [spiderConfig.intervalMinutes, selectedSpiderKey]);

    useEffect(() => {
        if (!spiderConfig.enabled || secondsLeft <= 0) return;

        const timer = window.setInterval(() => {
            setSecondsLeft((prev) => {
                if (prev <= 1) {
                    return spiderConfig.intervalMinutes * 60;
                }
                return prev - 1;
            });
        }, 1000);

        return () => window.clearInterval(timer);
    }, [spiderConfig.enabled, spiderConfig.intervalMinutes, secondsLeft]);

    const formattedTime = useMemo(() => {
        const minutes = Math.floor(secondsLeft / 60);
        const seconds = secondsLeft % 60;
        return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
    }, [secondsLeft]);

    function handleSpiderChange<K extends keyof SpiderConfig>(key: K, value: SpiderConfig[K]) {
        let nextValue = value;

        if (key === "intervalMinutes") {
            const numericValue = Number(value);
            nextValue = Math.min(
                Math.max(Number.isFinite(numericValue) ? numericValue : 1, 1),
                1440
            ) as SpiderConfig[K];
        }

        if (key === "maxPages") {
            const numericValue = Number(value);
            nextValue = Math.min(
                Math.max(Number.isFinite(numericValue) ? numericValue : 1, 1),
                MAX_SPIDER_PAGES
            ) as SpiderConfig[K];
        }

        setSpiderConfig((prev) => ({
            ...prev,
            [key]: nextValue,
        }));
    }

    async function handleSaveSpiderConfig() {
        if (spiderConfig.maxPages < 1 || spiderConfig.maxPages > MAX_SPIDER_PAGES) {
            setError(`Max pages must be between 1 and ${MAX_SPIDER_PAGES}.`);
            setMessage("");
            return;
        }

        if (spiderConfig.intervalMinutes < 1 || spiderConfig.intervalMinutes > 1440) {
            setError("Interval must be between 1 and 1440 minutes.");
            setMessage("");
            return;
        }

        try {
            setIsSavingConfig(true);
            setError("");
            setMessage("");

            const savedConfig = await saveSpiderConfig(selectedSpiderKey, spiderConfig);
            setSpiderConfig(savedConfig);

            const updatedStatus = await loadSpiderStatus();
            setSpiderStatus(updatedStatus);

            setMessage(`Configuration saved for ${selectedSpiderKey}.`);
        } catch (err) {
            console.error(err);
            setError("Failed to save spider configuration.");
        } finally {
            setIsSavingConfig(false);
        }
    }

    const dateTimeFormatter = new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
    });

    function formatDateTime(value?: string) {
        if (!value) return "Not available yet";
        return dateTimeFormatter.format(new Date(value));
    }

    const selectedSpiderLabel =
        SPIDER_OPTIONS.find((spider) => spider.key === selectedSpiderKey)?.label ?? selectedSpiderKey;

    return (
        <div className="dashboard-page">
            <div className="dashboard-header">
                <div>
                    <h2 className="dashboard-title">{selectedSpiderLabel}</h2>
                    <p className="dashboard-subtitle">
                        Configure rerun timing, target region, and crawl limits for your spider jobs.
                    </p>
                </div>
            </div>

            <div className="dashboard-grid">
                <section className="dashboard-card">
                    <h3>Spider Settings</h3>

                    <label className="form-label">
                        <span>Spider:</span>
                        <select
                            value={selectedSpiderKey}
                            onChange={(event) => setSelectedSpiderKey(event.target.value)}
                        >
                            {SPIDER_OPTIONS.map((spider) => (
                                <option key={spider.key} value={spider.key}>
                                    {spider.label}
                                </option>
                            ))}
                        </select>
                    </label>

                    <label className="form-label">
                        <span>Enable scheduled spider runs</span>
                        <input
                            type="checkbox"
                            checked={spiderConfig.enabled}
                            onChange={(event) => handleSpiderChange("enabled", event.target.checked)}
                        />
                    </label>

                    <label className="form-label">
                        <span>Interval (minutes): </span>
                        <input
                            type="number"
                            min={1}
                            max={1440}
                            value={spiderConfig.intervalMinutes}
                            onChange={(event) =>
                                handleSpiderChange("intervalMinutes", Number(event.target.value))
                            }
                        />
                        <small className="form-help-text">
                            Allowed range: 1 to 1440 minutes.
                        </small>
                    </label>

                    <label className="form-label">
                        <span>Region: </span>
                        <input
                            type="text"
                            value={spiderConfig.region}
                            onChange={(event) => handleSpiderChange("region", event.target.value)}
                        />
                    </label>

                    <label className="form-label">
                        <span>Keywords: </span>
                        <input
                            type="text"
                            value={spiderConfig.keywords}
                            onChange={(event) => handleSpiderChange("keywords", event.target.value)}
                        />
                    </label>

                    <label className="form-label">
                        <span>Max pages: </span>
                        <input
                            type="number"
                            min={1}
                            max={MAX_SPIDER_PAGES}
                            value={spiderConfig.maxPages}
                            onChange={(event) =>
                                handleSpiderChange("maxPages", Number(event.target.value))
                            }
                        />
                        <small className="form-help-text">
                            Allowed range: 1 to {MAX_SPIDER_PAGES}.
                        </small>
                    </label>

                    <div className="dashboard-actions">
                        <button
                            className="dashboard-button"
                            type="button"
                            onClick={handleSaveSpiderConfig}
                            disabled={isSavingConfig}
                        >
                            {isSavingConfig ? "Saving..." : "Save Config"}
                        </button>
                    </div>

                    {message ? <p className="settings-success">{message}</p> : null}
                    {error ? <p className="settings-error">{error}</p> : null}
                </section>

                <section className="dashboard-card">
                    <h3>Spider Status</h3>

                    <p>
                        <strong>Spider:</strong> <span>{selectedSpiderLabel}</span>
                    </p>
                    <br />

                    <p>
                        <strong>Running:</strong>{" "}
                        <span
                            className={
                                spiderStatus.isRunning ? "status-running" : "status-stopped"
                            }
                        >
                            {spiderStatus.isRunning ? "Yes" : "No"}
                        </span>
                    </p>
                    <br />

                    <p>
                        <strong>Last run:</strong>{" "}
                        <span className="status-last-run">
                            {formatDateTime(spiderStatus.lastRunAt)}
                        </span>
                    </p>
                    <br />

                    <p>
                        <strong>Next run:</strong>{" "}
                        <span className="status-next-run">
                            {spiderStatus.nextRunAt
                                ? formatDateTime(spiderStatus.nextRunAt)
                                : "Waiting for scheduler"}
                        </span>
                    </p>
                    <br />

                    <p>
                        <strong>Countdown:</strong>{" "}
                        <span className="status-countdown">
                            {spiderConfig.enabled ? formattedTime : "Disabled"}
                        </span>
                    </p>
                </section>
            </div>
        </div>
    );
}