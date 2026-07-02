import { useEffect, useRef, useState } from "react";
import { APP_CONFIG } from "../config";

type SpiderItem = {
  key: string;
  label: string;
};

type SpiderRunApiResponse = {
  message?: string;
  started?: boolean;
  spider?: string;
  job_id?: string;
  nextRunAt?: string | null;
  detail?: string;
};

type SpiderJob = {
  job_id: string;
  spider: string;
  status: string;
  started_at: string;
  finished_at?: string | null;
  error?: string | null;
};

type JobStatus = "" | "running" | "completed" | "failed" | "aborted";

function formatSpiderMessage(spiderName: string, status: JobStatus) {
  switch (status) {
    case "running":
      return `${spiderName} has started.`;
    case "completed":
      return `${spiderName} has completed.`;
    case "aborted":
      return `${spiderName} was stopped.`;
    case "failed":
      return `${spiderName} failed to complete.`;
    default:
      return "";
  }
}

export function SpiderPage() {
  const [spiders, setSpiders] = useState<SpiderItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeSpiderKey, setActiveSpiderKey] = useState("");
  const [activeJobId, setActiveJobId] = useState("");
  const [jobStatus, setJobStatus] = useState<JobStatus>("");
  const [error, setError] = useState("");
  const [runMessage, setRunMessage] = useState("");
  const pollingStoppedRef = useRef(false);

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

  useEffect(() => {
    if (!activeJobId || !loading) return;

    pollingStoppedRef.current = false;

    const interval = window.setInterval(async () => {
      if (pollingStoppedRef.current) return;

      try {
        const res = await fetch(`${APP_CONFIG.apiBaseUrl}/spiders/jobs`, {
          credentials: "include",
        });

        const jobs: SpiderJob[] = await res.json();
        const job = jobs.find((item) => item.job_id === activeJobId);

        if (!job) return;

        if (job.status === "running") {
          return;
        }

        if (
          job.status === "completed" ||
          job.status === "failed" ||
          job.status === "aborted"
        ) {
          pollingStoppedRef.current = true;
          window.clearInterval(interval);

          const finalStatus = job.status as JobStatus;
          const displayName = getSpiderDisplayName(job.spider, spiders);
          setJobStatus(finalStatus);
          setRunMessage(formatSpiderMessage(displayName, finalStatus));

          if (finalStatus === "failed") {
            console.error("Spider failed:", job.error);
          }

          setLoading(false);
          setActiveSpiderKey("");
          setActiveJobId("");
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);

    return () => {
      pollingStoppedRef.current = true;
      window.clearInterval(interval);
    };
  }, [activeJobId, loading]);

  const handleRunSpider = async (spiderKey: string) => {
    try {
      setLoading(true);
      setActiveSpiderKey(spiderKey);
      setActiveJobId("");
      setJobStatus("running");
      setError("");
      setRunMessage(formatSpiderMessage(getSpiderDisplayName(spiderKey, spiders), "running"));
      pollingStoppedRef.current = false;

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
        throw new Error(data.detail || "Failed to run spider");
      }

      setActiveJobId(data.job_id ?? "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setLoading(false);
      setActiveSpiderKey("");
      setActiveJobId("");
      setJobStatus("");
    }
  };


  function humanizeSpiderName(value: string) {
    return value
      .split("_")
      .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
      .join(" ");
  }

  function getSpiderDisplayName(spiderKey: string, spiders: SpiderItem[]) {
    const found = spiders.find((s) => s.key === spiderKey);
    return found?.label || humanizeSpiderName(spiderKey);
  }

  const handleAbortSpider = async () => {
    if (!activeJobId) return;

    try {
      const res = await fetch(`${APP_CONFIG.apiBaseUrl}/spiders/${activeJobId}/abort`, {
        method: "POST",
        credentials: "include",
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to abort spider");
      }

      pollingStoppedRef.current = true;
      setJobStatus("aborted");
      setRunMessage(
        formatSpiderMessage(getSpiderDisplayName(activeSpiderKey, spiders), "aborted"));
      setLoading(false);
      setActiveSpiderKey("");
      setActiveJobId("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  };

  return (
    <div className="dashboard-page spider-page">
      {error && <p className="settings-error">{error}</p>}
      {runMessage && (
        <div
          className={`dashboard-message ${jobStatus === "failed" ? "error" : jobStatus === "aborted" ? "warning" : "success"
            }`}
        >
          {runMessage}
        </div>
      )}

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

        {loading && activeJobId ? (
          <button className="stop-spider-button" onClick={handleAbortSpider}>
            Stop Spider
          </button>
        ) : null}
      </div>
    </div>
  );
}